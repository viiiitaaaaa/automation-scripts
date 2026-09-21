// Переносит отмеченные цены конкурентов в шаблон цен «Лист6».
//
// Как это работает:
//   1. В листе «Сравнение» у строки конкурента ставится отметка в колонке Z
//      («Менять»). Строка конкурента относится к нашему товару — это ближайшая
//      строка выше, у которой в B стоит текстовый артикул продавца.
//   2. Цена конкурента в H — это ВИТРИНА, то есть уже с учётом СПП. Наша цена
//      в шаблоне задаётся ДО СПП, поэтому цель пересчитывается:
//
//         цена со скидкой = цена конкурента / (1 - СПП/100)
//
//      Сейчас СПП почти везде 0 и цена меняется незначительно, но как только WB
//      вернёт скидку, без этого множителя витрина окажется НИЖЕ цели ровно на
//      размер СПП (цель 375 при СПП 15 % требует 441 ₽ со скидкой, иначе
//      покупатель увидит 319).
//   3. В «Лист6» меняется только J «Новая цена, RUB». Скидка берётся из строки:
//      если владелец вписал новую в L — считаем от неё, иначе от текущей K.
//      Колонка M («Цена со скидкой») пересчитается формулой самого листа.
//   4. Отметки дублируются в служебный лист «Выбор цен» парой «наш артикул +
//      артикул WB конкурента»: `compare.js` пересобирает «Сравнение» и строки
//      съезжают, так что отметки в Z живут только до следующей пересборки.
//
// Запуск:
//   node apply-prices.js           — только показать план, ничего не менять
//   node apply-prices.js --apply   — записать цены в «Лист6» и журнал
//   node apply-prices.js --marks   — поставить флажки в Z у строк конкурентов
//                                    и вернуть отметки из журнала «Выбор цен»

const { BOOK_URL } = require('./book');

// ================== НАСТРОЙКИ ==================
const CMP = 'Сравнение';
const TPL = 'Лист6';
const LOG = 'Выбор цен';
const MARK_COL = 26;          // Z — отметка «Применить»
// Флажок Google Sheets отдаётся как TRUE/ИСТИНА; слова оставлены для отметок,
// проставленных руками до появления флажков.
const MARK_RE = /^(true|истина|менять|да|\+|v|x|✓)$/i;
const APPLY = process.argv.includes('--apply');
const MARKS = process.argv.includes('--marks');
// колонки «Лист6» (1-based)
const T = { art: 4, price: 9, newPrice: 10, disc: 11, newDisc: 12, withDisc: 13 };
// ===============================================

async function post(payload, tries = 6) {
  for (let t = 1; t <= tries; t++) {
    try {
      const r = await fetch(BOOK_URL, {
        method: 'POST', body: JSON.stringify(payload), signal: AbortSignal.timeout(300000),
      });
      const txt = (await r.text()).trim();
      // Apps Script под нагрузкой отдаёт 404 и HTML-страницу вместо ответа
      if (r.ok && !txt.startsWith('<')) return txt;
    } catch (e) {}
    await new Promise(res => setTimeout(res, 3000 * t));
  }
  throw new Error('Google Sheets не ответил');
}
const read = async (sheet, a1) => JSON.parse(await post({ read: { sheet, a1 } }));

const numRaw = v => {
  const n = Number(String(v ?? '').replace(/[\s ₽%]/g, '').replace(',', '.'));
  return Number.isFinite(n) ? n : NaN;
};
// ПУСТАЯ ЯЧЕЙКА — ЭТО NaN, А НЕ НОЛЬ. Number('') возвращает 0, из-за чего
// пустая «Новая скидка» (L) читалась как скидка 0 %, и цена считалась от
// полной цены до скидки вместо текущих 62 %.
const num = v => (String(v ?? '').trim() === '' ? NaN : numRaw(v));

const money = x => x.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

// Ставит флажки в Z у всех строк конкурентов и возвращает отметки из журнала.
// Нужно после каждой пересборки «Сравнения»: compare.js пересоздаёт лист.
async function installMarks(cmp, LAST) {
  // Строка конкурента — та, где есть артикул WB (C) и НЕТ нашего артикула в B.
  // По формуле =IMAGE ориентироваться нельзя: у конкурентов без фото её нет
  // (в прогоне 04.08.2026 таких было 123), они оставались без флажка, а
  // возвращённая из журнала галочка показывалась словом TRUE.
  const isComp = n => {
    const v = cmp.values[n - 1] || [];
    const f = (cmp.formulas[n - 1] || [])[1] || '';
    const our = String(v[1] ?? '').trim() && !f.startsWith('=IMAGE');
    return !our && String(v[2] ?? '').trim();
  };

  const ranges = [];
  let from = 0;
  for (let n = 2; n <= LAST + 1; n++) {
    const comp = n <= LAST && isComp(n);
    if (comp && !from) from = n;
    if (!comp && from) { ranges.push(`Z${from}:Z${n - 1}`); from = 0; }
  }
  await post({ sheet: CMP, at: 1, col: MARK_COL, rows: [['Применить']] });
  for (let i = 0; i < ranges.length; i += 40) {
    await post({ sheet: CMP, checkbox: { ranges: ranges.slice(i, i + 40) } });
  }
  console.log(`Флажки поставлены: ${ranges.length} групп конкурентов.`);

  // возвращаем прошлые отметки по паре «наш артикул + артикул WB»
  let log;
  try { log = await read(LOG, 'A1:K500'); } catch (e) { log = null; }
  if (!log || !log.values || log.values.length < 2) return;
  const want = new Set(log.values.slice(1)
    .filter(r => String(r[0] ?? '').trim())
    .map(r => `${String(r[0]).trim()}|${String(r[1]).trim()}`));

  let owner = null, back = 0;
  for (let n = 2; n <= LAST; n++) {
    const v = cmp.values[n - 1] || [];
    const f = (cmp.formulas[n - 1] || [])[1] || '';
    if (String(v[1] ?? '').trim() && !f.startsWith('=IMAGE')) { owner = String(v[1]).trim(); continue; }
    if (!owner) continue;
    if (!want.has(`${owner}|${String(v[2] ?? '').trim()}`)) continue;
    await post({ sheet: CMP, at: n, col: MARK_COL, rows: [[true]] });
    back++;
  }
  console.log(`Возвращено отметок из «${LOG}»: ${back}.`);
}

(async () => {
  const cmp = await read(CMP, 'A1:Z1000');
  const LAST = cmp.lastRow;

  if (MARKS) { await installMarks(cmp, LAST); process.exit(0); }

  // ---------- 1. разбираем «Сравнение» ----------
  // Наша строка: в B текстовый артикул. У конкурента в B формула =IMAGE,
  // поэтому пустой B там не показатель — проверяем именно формулу.
  const marks = [];
  let owner = null;
  for (let n = 2; n <= LAST; n++) {
    const v = cmp.values[n - 1] || [];
    const f = cmp.formulas[n - 1] || [];
    const isOur = String(v[1] ?? '').trim() && !String(f[1] || '').startsWith('=IMAGE');
    if (isOur) {
      owner = {
        row: n,
        art: String(v[1]).trim(),
        price: num(v[5]),      // F — цена со скидкой продавца
        spp: num(v[6]) || 0,   // G — СПП %
        shelf: num(v[7]),      // H — цена после СПП
      };
      continue;
    }
    const mark = String(v[MARK_COL - 1] ?? '').trim();
    if (!mark || !MARK_RE.test(mark)) continue;
    if (!owner) { console.log(`   строка ${n}: отметка без нашего товара выше — пропускаю`); continue; }
    marks.push({
      row: n, owner,
      wb: String(v[2] ?? '').trim(),
      brand: String(v[3] ?? '').trim(),
      target: num(v[7]),        // H конкурента — витрина, уже с его СПП
      profit: num(v[23]),       // X — новая прибыль на ед. по этой цене
    });
  }
  if (!marks.length) {
    console.log(`В «${CMP}» нет ни одной отметки в колонке Z. Поставьте «Менять» у строки конкурента.`);
    process.exit(0);
  }

  // Одна цена на товар: если отмечено несколько конкурентов — берём самого дешёвого.
  const byArt = new Map();
  for (const m of marks) {
    const cur = byArt.get(m.owner.art);
    if (!cur || m.target < cur.target) byArt.set(m.owner.art, m);
  }
  marks.filter(m => byArt.get(m.owner.art) !== m).forEach(m =>
    console.log(`   ${m.owner.art}: отмечено несколько конкурентов, беру самого дешёвого`));

  // ---------- 2. строки шаблона ----------
  const tpl = await read(TPL, 'A1:N1000');
  const tplRow = new Map();
  tpl.values.forEach((r, i) => {
    const a = String(r[T.art - 1] ?? '').trim();
    if (a && i > 0) tplRow.set(a, i + 1);
  });

  // ---------- 3. считаем ----------
  const plan = [];
  for (const m of byArt.values()) {
    const row = tplRow.get(m.owner.art);
    if (!row) { console.log(`   ${m.owner.art}: нет строки в «${TPL}» — пропускаю`); continue; }
    const r = tpl.values[row - 1];
    const price = num(r[T.price - 1]);
    const discNew = num(r[T.newDisc - 1]);
    const disc = Number.isFinite(discNew) ? discNew : num(r[T.disc - 1]);
    if (!Number.isFinite(price) || !Number.isFinite(disc)) {
      console.log(`   ${m.owner.art}: в «${TPL}» не читаются цена или скидка — пропускаю`);
      continue;
    }
    // цель после СПП -> цена со скидкой -> цена до скидки
    const withDisc = m.target / (1 - m.owner.spp / 100);
    const newPrice = Math.round(withDisc / (1 - disc / 100));
    const factWithDisc = newPrice * (1 - disc / 100);
    const factShelf = factWithDisc * (1 - m.owner.spp / 100);
    plan.push({ ...m, row, price, disc, withDisc, newPrice, factWithDisc, factShelf });
  }

  // ---------- 4. отчёт ----------
  console.log(`\nОтмечено к смене цен: ${plan.length}` + (APPLY ? '' : '   (черновой прогон, --apply чтобы записать)'));
  for (const p of plan) {
    console.log(`\n${p.owner.art}  (строка ${p.row} в «${TPL}», конкурент ${p.wb} ${p.brand})`);
    console.log(`   сейчас:  цена до скидки ${money(p.price)} × скидка ${p.disc}%` +
                ` = ${money(p.price * (1 - p.disc / 100))} → витрина ${money(p.owner.shelf)}`);
    console.log(`   цель:    витрина ${money(p.target)} при СПП ${p.owner.spp}%` +
                ` → цена со скидкой ${money(p.withDisc)}`);
    console.log(`   станет:  цена до скидки ${money(p.newPrice)} × скидка ${p.disc}%` +
                ` = ${money(p.factWithDisc)} → витрина ${money(p.factShelf)}` +
                `  (отклонение ${money(p.factShelf - p.target)} ₽)`);
    if (Number.isFinite(p.profit)) console.log(`   прибыль на ед. по этой цене: ${money(p.profit)} ₽`);
  }

  if (!APPLY) {
    console.log('\nНичего не записано. Повторите с --apply.');
    process.exit(0);
  }

  // ---------- 5. запись ----------
  console.log('\nПишу цены в «' + TPL + '»...');
  for (const p of plan) {
    await post({ sheet: TPL, at: p.row, col: T.newPrice, rows: [[p.newPrice]] });
    console.log(`   ${p.owner.art}: J${p.row} = ${p.newPrice}`);
  }

  const stamp = new Date().toLocaleString('ru-RU');
  const rows = [[
    'Наш артикул', 'Артикул WB конкурента', 'Бренд конкурента', 'Цена конкурента после СПП',
    'СПП, %', 'Цена со скидкой (цель)', 'Скидка, %', 'Новая цена до скидки',
    'Витрина по факту', 'Строка «Лист6»', 'Когда',
  ]];
  for (const p of plan) {
    rows.push([p.owner.art, p.wb, p.brand, p.target, p.owner.spp,
               Math.round(p.withDisc * 100) / 100, p.disc, p.newPrice,
               Math.round(p.factShelf * 100) / 100, p.row, stamp]);
  }
  await post({ sheet: LOG, rows, clear: true });
  console.log(`Журнал «${LOG}» обновлён: ${rows.length - 1} строк.`);
  process.exit(0);
})().catch(e => { console.error('\nОШИБКА:', e.message); process.exit(1); });
