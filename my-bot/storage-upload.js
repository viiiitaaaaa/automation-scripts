// Заливает платное хранение (storage/storage-daily.json от storage.js) в таблицу:
//   1) лист «История хранения» — период | дата | артикул | сумма;
//   2) колонка U «Хранение» недельных вкладок — SUMIFS по артикулу И периоду.
//
// До этого колонка U заполнялась руками: в недельном отчёте реализации
// хранение лежит строками с пустым артикулом, и разнести его по SKU оттуда
// нельзя. Источник здесь другой — отчёт по номенклатурам платного хранения.
//
// Запуск:
//   node storage-upload.js
//   node storage-upload.js --formulas   — не перезаливать лист-источник

const fs = require('fs');
const path = require('path');

// ================== НАСТРОЙКИ ==================
const { BOOK_URL: SHEET_URL } = require('./book');   // единая книга, см. book.js
const HIST = 'История хранения';
const DAILY = path.join(__dirname, 'storage', 'storage-daily.json');
const COL_U = 21;                    // U — «Хранение»
const FIRST_ROW = 2;
const CHUNK = 300;
const PERIOD_RE = /^с \d{2}\.\d{2}\.\d{4} по \d{2}\.\d{2}\.\d{4}$/;
const ONLY_FORMULAS = process.argv.includes('--formulas');
// ===============================================

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

const read = async (sheet, a1) => {
  const r = await fetch(SHEET_URL, {
    method: 'POST', body: JSON.stringify({ read: { sheet, a1 } }),
    signal: AbortSignal.timeout(300000),
  });
  return JSON.parse(await r.text());
};

const col = c => `'${HIST}'!${c}:${c}`;

(async () => {
  if (!fs.existsSync(DAILY)) {
    console.log('Нет storage/storage-daily.json — сначала запустите: node storage.js');
    process.exit(1);
  }
  const daily = JSON.parse(fs.readFileSync(DAILY, 'utf-8'));
  console.log('Строк хранения (день + артикул):', daily.length);

  if (ONLY_FORMULAS) {
    console.log(`\nРежим --formulas: лист «${HIST}» не трогаю.`);
  } else {
    const rows = [['Период', 'Дата', 'Артикул поставщика', 'Хранение, ₽']];
    for (const d of daily) rows.push([d.period, d.date, d.article, d.sum]);

    console.log(`\nЗаливаю лист «${HIST}»...`);
    await post({ sheet: HIST, wipe: true, at: 1, rows: rows.slice(0, CHUNK) });
    for (let i = CHUNK; i < rows.length; i += CHUNK) {
      await post({ sheet: HIST, at: i + 1, rows: rows.slice(i, i + CHUNK) });
      process.stdout.write(`   строк ${Math.min(i + CHUNK, rows.length)} из ${rows.length}\r`);
    }
    console.log(`   строк ${rows.length} из ${rows.length}        `);
  }

  const all = await read('Динамика финансы', 'A1:A1');
  const tabs = all.sheets.filter(s => PERIOD_RE.test(s));
  console.log('\nНедельных вкладок:', tabs.length);

  const havePeriods = new Set(daily.map(d => d.period));

  for (const tab of tabs) {
    const info = await read(tab, 'A1:A400');
    const totalRow = info.values.findIndex(r => String(r[0]).trim().toUpperCase() === 'ИТОГО') + 1;
    const lastData = (totalRow > 0 ? totalRow : info.lastRow + 1) - 1;

    const tabArts = new Set();
    for (let i = FIRST_ROW - 1; i < lastData; i++) {
      const a = String((info.values[i] || [])[0] || '').trim();
      if (a) tabArts.add(a);
    }
    const inPeriod = daily.filter(d => d.period === tab);
    const spendArts = new Set(inPeriod.map(d => d.article));
    const missing = [...spendArts].filter(a => !tabArts.has(a));
    const sum = inPeriod.reduce((s, d) => s + d.sum, 0);

    console.log(`\n${tab}`);
    if (!havePeriods.has(tab)) {
      console.log('   отчёта за этот период нет — колонка U станет нулевой,');
      console.log('   выгрузите его: node storage.js <начало> <конец>');
    } else {
      console.log(`   хранение за период: ${sum.toFixed(2)} ₽, артикулов: ${spendArts.size}`);
    }
    if (missing.length) {
      console.log(`   ВНИМАНИЕ: ${missing.length} артикул(ов) есть в хранении, но нет строкой во вкладке:`);
      console.log('      ' + missing.slice(0, 10).join(', ') + (missing.length > 10 ? ' ...' : ''));
    }

    // TRIM($A) обязателен: часть артикулов во вкладке записана с висячим
    // пробелом, а SUMIFS сравнивает строки как есть.
    const formulas = [];
    for (let n = FIRST_ROW; n <= lastData; n++) {
      formulas.push([`=SUMIFS(${col('D')};${col('C')};TRIM($A${n});${col('A')};"${tab}")`]);
    }
    await post({ sheet: tab, at: FIRST_ROW, col: COL_U, formulas });
    console.log(`   колонка U проставлена, строки ${FIRST_ROW}..${lastData}`);

    if (totalRow) {
      // полный итог периода, а не сумма строк: хранение по артикулам,
      // которых нет во вкладке, иначе выпало бы из итога
      await post({
        sheet: tab, at: totalRow, col: COL_U,
        formulas: [[`=SUMIFS(${col('D')};${col('A')};"${tab}")`]],
      });
      console.log(`   ИТОГО в строке ${totalRow} пересчитано`);
    }
  }

  console.log('\nГотово.');
  process.exit(0);
})().catch(e => { console.log('\nОШИБКА:', e.message); process.exit(1); });
