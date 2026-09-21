// Сверка «К перечислению» с реальными суммами кабинета WB.
//
// Качает с https://seller.wildberries.ru/suppliers-mutual-settlements/reports-implementations/reports-weekly-new
// сводный excel всех отчётов в сокращённой форме (кнопка «Скачать excel»
// на списке — внутрь отчётов заходить не нужно). В файле одна строка на
// отчёт («Основной» / «По выкупам») с колонкой «Итого к оплате».
//
// Затем в «Динамика финансы» для каждой строки нижнего блока (в колонке B
// период вида «с ДД.ММ.ГГГГ по ДД.ММ.ГГГГ») проставляет:
//   W — Итого к оплате ВБ, ₽ (сумма двух отчётов недели, число);
//   X — Совпадение C/ВБ, %  (формула =C/W*100 — 100 значит сошлись).
//
// А по неделям, для которых в reports/extracted лежат сами отчёты, ещё и
// удержания ВБ — без них C не сходится с AG:
//   L — штрафы;
//   M — прочие удержания (всё, кроме рекламы);
//   N — реклама, УДЕРЖАННАЯ ВБ («Оказание услуг "WB Продвижение"»);
//   P — мелкие поступления по программе лояльности;
//   Q — компенсация (в отчёте «Добровольная выплата…» идёт со знаком минус,
//       то есть ВБ платит нам).
//
// ПОЧЕМУ В N НЕ РАСХОД КАБИНЕТА. `ads.js` собирает потраченное (за 27.07–02.08
// это 81 625 ₽), а ВБ удержал 77 173 ₽ — остаток переносится в следующий отчёт.
// Для юнит-экономики нужна потраченная сумма, она и лежит в колонке V недельной
// вкладки; для «к перечислению» — удержанная. До 27.07.2026 они почти совпадали,
// поэтому расхождения не было видно.
//
// Больше НИЧЕГО в «Динамике финансы» не трогает: лист перестроен владельцем.
//
// Запуск:
//   node pay-compare.js            — скачать свежий файл и проставить
//   node pay-compare.js --local    — без скачивания, по последнему файлу в pay/

const fs = require('fs');
const path = require('path');
const XLSX = require('xlsx');
const { attach } = require('./cdp-lite');

// ================== НАСТРОЙКИ ==================
const PAGE = 'https://seller.wildberries.ru/suppliers-mutual-settlements/reports-implementations/reports-weekly-new';
const { BOOK_URL: SHEET_URL } = require('./book');   // единая книга, см. book.js
const DYN = 'Динамика финансы';
const DIR = path.join(__dirname, 'pay');
const EXTRACTED = path.join(__dirname, 'reports', 'extracted');
// W и X — колонки владельца под этот блок («Итого к оплате ВБ, ₽» и
// «Совпадение C/ВБ, %», подписаны во ВТОРОЙ строке). Раньше здесь стояли 33/34,
// то есть AG/AH: AG — это «PnL» верхнего блока, и сверка уезжала в чужую
// колонку, а W/X с 04.08.2026 оставались пустыми.
const COL_WB = 23;   // W — итого к оплате ВБ
const COL_PCT = 24;  // X — совпадение, %
// Колонки удержаний в «Динамике» (номера, не буквы)
const COL_FINE = 12, COL_OTHER = 13, COL_ADS = 14, COL_IN = 16, COL_COMP = 17;
const PERIOD_RE = /^с \d{2}\.\d{2}\.\d{4} по \d{2}\.\d{2}\.\d{4}$/;
const LOCAL = process.argv.includes('--local');
// ===============================================

fs.mkdirSync(DIR, { recursive: true });

async function post(payload, tries = 4) {
  for (let t = 1; t <= tries; t++) {
    try {
      const r = await fetch(SHEET_URL, {
        method: 'POST', body: JSON.stringify(payload),
        signal: AbortSignal.timeout(300000),
      });
      if (!r.ok) throw new Error('код ' + r.status);
      const body = (await r.text()).trim();
      if (body !== 'ok') throw new Error('ответ: ' + body.slice(0, 80));
      return;
    } catch (e) {
      if (t === tries) throw e;
      console.log(`   попытка ${t} не удалась (${e.message}), повторяю...`);
      await new Promise(res => setTimeout(res, 3000 * t));
    }
  }
}
const read = async (sheet, a1, tries = 4) => {
  for (let t = 1; t <= tries; t++) {
    try {
      const r = await fetch(SHEET_URL, {
        method: 'POST', body: JSON.stringify({ read: { sheet, a1 } }),
        signal: AbortSignal.timeout(300000),
      });
      return JSON.parse(await r.text());
    } catch (e) {
      if (t === tries) throw e;
      await new Promise(res => setTimeout(res, 3000 * t));
    }
  }
};

// ---------- удержания из самого недельного отчёта ----------
// В отчёте они лежат в колонке «Удержания», а чем именно является строка —
// написано в «Виды логистики, штрафов и корректировок ВВ». Реклама там
// называется «Оказание услуг "WB Продвижение"», а выплаты нам («Добровольная
// выплата…») стоят со знаком минус.
function holdingsOf(reportNums) {
  const out = { ads: 0, other: 0, comp: 0, files: 0 };
  for (const num of reportNums) {
    const file = path.join(EXTRACTED, `${num}.xlsx`);
    if (!fs.existsSync(file)) continue;
    const all = XLSX.utils.sheet_to_json(
      XLSX.read(fs.readFileSync(file)).Sheets[XLSX.read(fs.readFileSync(file)).SheetNames[0]],
      { header: 1, defval: '' });
    const head = all[0].map(h => String(h).trim());
    const iHold = head.findIndex(h => /^Удержания$/i.test(h));
    const iKind = head.findIndex(h => /Виды логистики, штрафов/i.test(h));
    if (iHold < 0) continue;
    out.files++;
    for (const r of all.slice(1)) {
      const v = Number(r[iHold]) || 0;
      if (!v) continue;
      const kind = String(r[iKind] ?? '');
      if (/Продвижение/i.test(kind)) out.ads += v;
      else if (v < 0) out.comp += -v;          // выплата нам — в «Конпенсацию»
      else out.other += v;
    }
  }
  const r2 = x => Math.round(x * 100) / 100;
  return { ads: r2(out.ads), other: r2(out.other), comp: r2(out.comp), files: out.files };
}

// ---------- скачивание сводного файла ----------
async function download() {
  const before = new Set(fs.readdirSync(DIR));
  const t = await attach('reports-weekly-new', PAGE);
  console.log('вкладка:', t.url);
  await new Promise(r => setTimeout(r, 5000));

  await t.raw('Browser.setDownloadBehavior', {
    behavior: 'allow', downloadPath: DIR, eventsEnabled: true,
  });
  let state = null;
  t.on(m => {
    if (m.method === 'Browser.downloadProgress' && m.params.state !== 'inProgress') state = m.params.state;
  });

  const clicked = await t.evaluate(`(() => {
    const b = [...document.querySelectorAll('button')].find(x => /^Скачать excel$/i.test(x.innerText.trim()));
    if (!b) return 'кнопка «Скачать excel» не найдена';
    b.click(); return 'ok';
  })()`);
  if (clicked !== 'ok') throw new Error(clicked);
  console.log('нажал «Скачать excel», жду файл...');

  for (let i = 0; i < 120 && state !== 'completed'; i++) await new Promise(r => setTimeout(r, 1000));
  await new Promise(r => setTimeout(r, 2000));   // файлу дописаться
  t.close();

  const added = fs.readdirSync(DIR).filter(f => !before.has(f) && f.endsWith('.xlsx'));
  if (!added.length) throw new Error('файл не появился в ' + DIR + ' (state=' + state + ')');
  const file = path.join(DIR, added[0]);
  console.log('скачан:', added[0], Math.round(fs.statSync(file).size / 1024), 'КБ');
  return file;
}

const latestFile = () => {
  const c = fs.readdirSync(DIR).filter(f => f.endsWith('.xlsx'))
    .map(f => ({ f, t: fs.statSync(path.join(DIR, f)).mtimeMs }))
    .sort((a, b) => b.t - a.t);
  if (!c.length) { console.log('В', DIR, 'нет xlsx — запустите без --local'); process.exit(1); }
  return path.join(DIR, c[0].f);
};

(async () => {
  const file = LOCAL ? latestFile() : await download();

  // ---------- разбор ----------
  const wb = XLSX.read(fs.readFileSync(file));
  const rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, defval: '' });
  const head = rows[0];
  const iStart = head.indexOf('Дата начала');
  const iEnd = head.indexOf('Дата конца');
  const iPay = head.indexOf('Итого к оплате');
  const iType = head.indexOf('Тип отчета');
  if (iStart < 0 || iPay < 0) throw new Error('не нашёл колонки в файле');

  const ru = s => {
    const d = String(s).slice(0, 10);           // 2026-07-20T00:00:00+03:00
    const [y, m, dd] = d.split('-');
    return `${dd}.${m}.${y}`;
  };
  const iNum = head.indexOf('№ отчета');
  const iFine = head.indexOf('Общая сумма штрафов');
  // мелочь по программе лояльности: в файле идёт со знаком минус, то есть
  // это поступление нам, а не удержание — поэтому в «Прочие поступления»
  const iLoyal = head.indexOf('Стоимость участия в программе лояльности');
  const iPoints = head.indexOf('Сумма баллов, удержанных по программе лояльности');

  const byPeriod = new Map();                    // «с ... по ...» -> {sum, reports}
  for (const r of rows.slice(1)) {
    if (!String(r[iStart]).trim()) continue;
    const label = `с ${ru(r[iStart])} по ${ru(r[iEnd])}`;
    if (!byPeriod.has(label)) byPeriod.set(label, { sum: 0, n: 0, types: [], nums: [], fine: 0, income: 0 });
    const p = byPeriod.get(label);
    p.sum += Number(r[iPay]) || 0;
    p.n++;
    p.types.push(String(r[iType] || ''));
    if (iNum >= 0) p.nums.push(String(r[iNum]).trim());
    if (iFine >= 0) p.fine += Number(r[iFine]) || 0;
    if (iLoyal >= 0) p.income -= Number(r[iLoyal]) || 0;
    if (iPoints >= 0) p.income -= Number(r[iPoints]) || 0;
  }
  console.log(`\nОтчётов в файле: ${rows.length - 1}, недель: ${byPeriod.size}`);

  // ---------- строки «Динамики финансы» ----------
  const info = await read(DYN, 'A1:B200');
  const targets = [];                            // {row, period}
  info.values.forEach((v, i) => {
    const b = String((v || [])[1] ?? '').trim();
    if (PERIOD_RE.test(b) && byPeriod.has(b)) targets.push({ row: i + 1, period: b });
  });
  if (!targets.length) { console.log('Ни одна строка B не совпала с периодами файла'); process.exit(1); }

  // Заголовки НЕ пишем: они уже стоят во второй строке листа, а запись в
  // первую плодила вторую пару подписей над чужими колонками.

  console.log('\nПроставляю AG/AH:');
  for (const { row, period } of targets) {
    const p = byPeriod.get(period);
    const wbSum = Math.round(p.sum * 100) / 100;
    await post({ sheet: DYN, at: row, col: COL_WB, rows: [[wbSum]] });
    await post({
      sheet: DYN, at: row, col: COL_PCT,
      formulas: [[`=IFERROR(ROUND($C${row}/$W${row}*100;1);"")`]],
    });
    console.log(`   строка ${row}  ${period}  ВБ: ${wbSum.toLocaleString('ru-RU')} ₽` +
                `  (отчётов: ${p.n} — ${p.types.join(', ')})`);

    // Удержания ставим только там, где есть сами отчёты: разложить «прочие»
    // на рекламу и компенсацию можно лишь по ним. Для старых недель, чьих
    // файлов уже нет, колонки владельца не трогаем вообще.
    const h = holdingsOf(p.nums);
    if (!h.files) { console.log('      отчётов в reports/extracted нет — удержания пропускаю'); continue; }
    const r2 = x => Math.round(x * 100) / 100;
    await post({ sheet: DYN, at: row, col: COL_FINE, rows: [[r2(p.fine)]] });
    await post({ sheet: DYN, at: row, col: COL_OTHER, rows: [[h.other]] });
    await post({ sheet: DYN, at: row, col: COL_ADS, rows: [[h.ads]] });
    await post({ sheet: DYN, at: row, col: COL_IN, rows: [[r2(p.income)]] });
    await post({ sheet: DYN, at: row, col: COL_COMP, rows: [[h.comp]] });
    console.log(`      удержания: реклама ${h.ads.toLocaleString('ru-RU')} ₽, прочие ${h.other} ₽,` +
                ` штрафы ${r2(p.fine)} ₽, компенсация ${h.comp.toLocaleString('ru-RU')} ₽,` +
                ` поступления ${r2(p.income)} ₽`);
  }
  console.log('\nГотово. X = C/W*100: 100 — сошлось копейка в копейку.');
  process.exit(0);
})().catch(e => { console.log('\nОШИБКА:', e.message); process.exit(1); });
