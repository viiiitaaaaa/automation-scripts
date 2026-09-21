// Заливает рекламные расходы (ads/ads-daily.json от ads.js) в таблицу:
//   1) лист «История рекламы» — построчно: период | дата | артикул | расход;
//   2) колонка V «Реклама» недельных вкладок — SUMIFS по артикулу И периоду.
//
// Сопоставление строгое:
//   период  — берём из имени вкладки, оно же лежит в колонке A «Истории рекламы»;
//   артикул — camp_name кампании совпадает с колонкой A вкладки один в один
//             (например «apple-magnet-42-49/бежевый»).
//
// Колонка V считается формулой, а не числом, — так же, как остальные колонки
// вкладки (см. reports-formulas.js): перезалил историю — цифры обновились сами.
// INDIRECT здесь намеренно НЕ используется: он волатилен и вешает книгу.
//
// Запуск: node ads-upload.js

const fs = require('fs');
const path = require('path');

// ================== НАСТРОЙКИ ==================
const { BOOK_URL: SHEET_URL } = require('./book');   // единая книга, см. book.js
const ADS = 'История рекламы';       // лист-источник, создаётся при первой заливке
const DAILY = path.join(__dirname, 'ads', 'ads-daily.json');
const COL_V = 22;                    // V — «Реклама» в недельных вкладках
const FIRST_ROW = 2;
const CHUNK = 300;
const PERIOD_RE = /^с \d{2}\.\d{2}\.\d{4} по \d{2}\.\d{2}\.\d{4}$/;
// --formulas: только переставить колонку V, лист-источник не перезаливать
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

const col = c => `'${ADS}'!${c}:${c}`;

(async () => {
  if (!fs.existsSync(DAILY)) {
    console.log('Нет ads/ads-daily.json — сначала запустите: node ads.js');
    process.exit(1);
  }
  const daily = JSON.parse(fs.readFileSync(DAILY, 'utf-8'));
  console.log('Строк расходов (день + артикул):', daily.length);

  // ---------- 1. лист-источник ----------
  if (ONLY_FORMULAS) {
    console.log(`\nРежим --formulas: лист «${ADS}» не трогаю.`);
  } else {
    // Колонка «Кампании» — исходные названия из кабинета. Нужна для сверки:
    // часть кампаний названа свободным текстом и приводится к артикулу
    // правилами в ads.js, по этой колонке видно, что и куда легло.
    const rows = [['Период', 'Дата', 'Артикул поставщика', 'Расход, ₽', 'Кампании']];
    for (const d of daily) rows.push([d.period, d.date, d.article, d.sum, d.camps || '']);

    console.log(`\nЗаливаю лист «${ADS}»...`);
    // wipe на первом чанке: лист перезаписывается целиком, поэтому повторный
    // запуск не задваивает строки.
    await post({ sheet: ADS, wipe: true, at: 1, rows: rows.slice(0, CHUNK) });
    for (let i = CHUNK; i < rows.length; i += CHUNK) {
      await post({ sheet: ADS, at: i + 1, rows: rows.slice(i, i + CHUNK) });
      process.stdout.write(`   строк ${Math.min(i + CHUNK, rows.length)} из ${rows.length}\r`);
    }
    console.log(`   строк ${rows.length} из ${rows.length}        `);
  }

  // ---------- 2. колонка «Реклама» в недельных вкладках ----------
  const all = await read('Динамика финансы', 'A1:A1');
  const tabs = all.sheets.filter(s => PERIOD_RE.test(s));
  console.log('\nНедельных вкладок:', tabs.length, '\n  ' + tabs.join('\n  '));

  const adsPeriods = new Set(daily.map(d => d.period));

  for (const tab of tabs) {
    const info = await read(tab, 'A1:A400');
    const totalRow = info.values.findIndex(r => String(r[0]).trim().toUpperCase() === 'ИТОГО') + 1;
    const lastData = (totalRow > 0 ? totalRow : info.lastRow + 1) - 1;

    // сверка: какие артикулы вкладки реально есть в расходах за этот период
    const tabArts = new Set();
    for (let i = FIRST_ROW - 1; i < lastData; i++) {
      const a = String((info.values[i] || [])[0] || '').trim();
      if (a) tabArts.add(a);
    }
    const inPeriod = daily.filter(d => d.period === tab);
    const spendArts = new Set(inPeriod.map(d => d.article));
    const missing = [...spendArts].filter(a => !tabArts.has(a));
    const sumPeriod = inPeriod.reduce((s, d) => s + d.sum, 0);

    console.log(`\n${tab}`);
    if (!adsPeriods.has(tab)) {
      console.log('   расходов за этот период в выгрузке нет — колонку V всё равно ставлю (будет 0)');
    } else {
      console.log(`   расход за период: ${Math.round(sumPeriod).toLocaleString('ru-RU')} ₽,` +
                  ` артикулов с рекламой: ${spendArts.size}`);
    }
    if (missing.length) {
      console.log(`   ВНИМАНИЕ: ${missing.length} артикул(ов) есть в рекламе, но нет строкой во вкладке —`);
      console.log('      ' + missing.slice(0, 10).join(', ') + (missing.length > 10 ? ' ...' : ''));
      console.log('      их расход попадёт в ИТОГО, но не в строки.');
    }

    // строки данных.
    // TRIM($A) обязателен: часть артикулов во вкладке записана с висячим
    // пробелом («huawei-8-milan-loop/розовый »), а SUMIFS сравнивает строки
    // как есть — без TRIM такие строки молча получали 0.
    const formulas = [];
    for (let n = FIRST_ROW; n <= lastData; n++) {
      formulas.push([`=SUMIFS(${col('D')};${col('C')};TRIM($A${n});${col('A')};"${tab}")`]);
    }
    await post({ sheet: tab, at: FIRST_ROW, col: COL_V, formulas });
    console.log(`   колонка V проставлена, строки ${FIRST_ROW}..${lastData}`);

    // ИТОГО: полный расход за период, а не сумма строк, — иначе реклама по
    // артикулам, которых нет во вкладке, потерялась бы из итога.
    if (totalRow) {
      await post({
        sheet: tab, at: totalRow, col: COL_V,
        formulas: [[`=SUMIFS(${col('D')};${col('A')};"${tab}")`]],
      });
      console.log(`   ИТОГО в строке ${totalRow} пересчитано`);
    }
  }

  console.log('\nГотово.');
  process.exit(0);
})().catch(e => { console.log('\nОШИБКА:', e.message); process.exit(1); });
