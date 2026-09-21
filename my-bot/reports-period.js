// Заводит новый период: недельную вкладку с именем по отчёту и строку в
// «Динамика финансы» с датами в колонке B.
//
// Вкладка создаётся копией предыдущей недельной — иначе потерялись бы
// оформление, список артикулов и колонки, которых нет в отчёте.
//
// НИЧЕГО НЕ ОЧИЩАЕМ. Раньше «ручные» колонки (Q..S, W..AK) чистились, но
// теперь там ФОРМУЛЫ владельца (юнит-экономика, налоги, дни до обнуления),
// считающие от колонок своей же вкладки, — они обязаны переехать в копию.
// Очистка 31.07.2026 убила их на двух новых вкладках, пришлось
// восстанавливать копированием через UI. Не повторять.

const fs = require('fs');
const path = require('path');

const { BOOK_URL: SHEET_URL } = require('./book');   // единая книга, см. book.js
const DYN = 'Динамика финансы';
const MANIFEST = path.join(__dirname, 'reports', 'manifest.json');
const PERIOD_RE = /^с (\d{2}\.\d{2}\.\d{4}) по (\d{2}\.\d{2}\.\d{4})$/;

// НЕ чистить: в Q..S, W..AK — формулы владельца (см. шапку файла).
// U и V перепишут storage-upload.js и ads-upload.js, B и AL..AV — funnel-upload.js.
const MANUAL_RANGES = [];

const MONTHS = ['Январь','Февраль','Март','Апрель','Май','Июнь',
                'Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь'];

const post = async (payload, tries = 4) => {
  for (let t = 1; t <= tries; t++) {
    try {
      const r = await fetch(SHEET_URL, {
        method: 'POST', body: JSON.stringify(payload), signal: AbortSignal.timeout(300000),
      });
      return (await r.text()).trim();
    } catch (e) {
      if (t === tries) throw e;
      await new Promise(res => setTimeout(res, 3000 * t));
    }
  }
};
const read = async (sheet, a1) => JSON.parse(await post({ read: { sheet, a1 } }));

const toDate = s => { const [d, m, y] = s.split('.').map(Number); return new Date(y, m - 1, d); };

// месяц недели — тот, на который приходится больше дней периода
function monthOf(startStr, endStr) {
  const s = toDate(startStr), e = toDate(endStr);
  const count = {};
  for (let d = new Date(s); d <= e; d.setDate(d.getDate() + 1)) {
    const k = d.getFullYear() + '-' + d.getMonth();
    count[k] = (count[k] || 0) + 1;
  }
  const best = Object.entries(count).sort((a, b) => b[1] - a[1])[0][0];
  const [y, m] = best.split('-').map(Number);
  return { year: y, month: m };
}

(async () => {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST, 'utf-8'));
  if (!manifest.length) { console.log('manifest.json пуст'); process.exit(1); }

  // самый свежий период из выгруженных отчётов
  const period = manifest.slice().sort((a, b) => b.end.localeCompare(a.end))[0].period;
  const m = period.match(PERIOD_RE);
  if (!m) { console.log('Не разобрал период:', period); process.exit(1); }
  console.log('Актуальный период из отчёта:', period);

  const info = await read(DYN, 'A1:B200');
  const sheets = info.sheets;

  // ---------- 1. вкладка ----------
  const weekTabs = sheets.filter(s => PERIOD_RE.test(s));
  if (sheets.includes(period)) {
    console.log('Вкладка уже есть:', period);
  } else if (!weekTabs.length) {
    console.log('Нет ни одной недельной вкладки — не с чего копировать. Создайте первую вручную.');
    process.exit(1);
  } else {
    // копируем самую свежую из существующих
    const src = weekTabs.sort((a, b) => {
      const ea = a.match(PERIOD_RE)[2].split('.').reverse().join('');
      const eb = b.match(PERIOD_RE)[2].split('.').reverse().join('');
      return eb.localeCompare(ea);
    })[0];
    console.log('Создаю вкладку копией из:', src);
    console.log('   ' + await post({ dup: { from: src, to: period } }));
    if (MANUAL_RANGES.length) {
      console.log('   очищаю:', await post({ sheet: period, clearRanges: MANUAL_RANGES }));
    } else {
      console.log('   формулы владельца (Q..S, W..AK) сохранены; B,U,V,AL..AV обновят конвейеры');
    }
  }

  // ---------- 2. строка в «Динамика финансы» ----------
  const rows = info.values;
  let rowIdx = rows.findIndex(r => String(r[1] || '').trim() === period);
  if (rowIdx >= 0) {
    console.log('Строка в «' + DYN + '» уже есть:', rowIdx + 1);
  } else {
    // последняя строка с периодом — новую пишем сразу под ней
    let last = -1;
    for (let i = 0; i < rows.length; i++) if (PERIOD_RE.test(String(rows[i][1] || '').trim())) last = i;
    if (last < 0) { console.log('В «' + DYN + '» не нашёл ни одной строки с периодом'); process.exit(1); }

    const n = last + 2;                      // 1-based номер новой строки
    const { year, month } = monthOf(m[1], m[2]);

    // номер недели внутри месяца — по уже проставленным строкам этого месяца
    const prefix = MONTHS[month];
    let idx = 0;
    for (let i = 0; i <= last; i++) {
      const a = String(rows[i][0] || '').trim();
      if (a.startsWith(prefix + ' ')) idx = Math.max(idx, parseInt(a.slice(prefix.length + 1), 10) || 0);
    }
    const label = `${prefix} ${idx + 1}`;

    console.log(`Добавляю строку ${n}: «${label}» | ${period}`);
    await post({ sheet: DYN, at: n, col: 1, rows: [[label, period]] });
  }

  // ---------- 3. скользящее окно недельных вкладок ----------
  // Держим только последние 4 недели — столько же, сколько считает
  // юнит-экономика. Перед удалением старой вкладки Apps Script замораживает
  // все ссылки на неё (в «Динамике финансы» это 8 ячеек на строку): числа
  // остаются на месте, связь с листом пропадает, #REF! не возникает.
  // Сами данные никуда не деваются — «История отчетов» хранит все периоды,
  // и вкладку всегда можно пересобрать (reports-period + reports-formulas).
  const rot = JSON.parse(await post({ rotate: { keep: 4, mode: 'delete' } }));
  if (rot.rotated.length) {
    console.log('\nРотация недельных вкладок:');
    rot.rotated.forEach(s => console.log('   ' + s));
  } else {
    console.log('\nРотация не нужна: вкладок ' + rot.kept.length + ' из 4.');
  }

  console.log('\nГотово. Дальше: node reports-formulas.js и node reports-dynamics.js');
  process.exit(0);
})();
