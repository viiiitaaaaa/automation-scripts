// Заливает воронку продаж (funnel/funnel-daily.json от funnel.js) в таблицу:
//   1) лист «История воронки» — период | артикул | остатки + 11 метрик;
//   2) недельные вкладки, всё формулами SUMIFS по артикулу И периоду:
//        B  Итого по складам ВБ   <- Остатки «Склад WB»
//        AL..AV — метрики воронки (заголовки ставятся в строку 1).
//
// Формулы, а не числа: перезалил историю — вкладки пересчитались сами.
// Период зашит именем вкладки, поэтому новая неделя старые не трогает.
// TRIM($A) — часть артикулов во вкладках с висячим пробелом.
//
// Запуск:
//   node funnel-upload.js
//   node funnel-upload.js --formulas   — не перезаливать лист-источник

const fs = require('fs');
const path = require('path');

// ================== НАСТРОЙКИ ==================
const { BOOK_URL: SHEET_URL } = require('./book');   // единая книга, см. book.js
const HIST = 'История воронки';
const DAILY = path.join(__dirname, 'funnel', 'funnel-daily.json');
const FIRST_ROW = 2;
const CHUNK = 300;
const PERIOD_RE = /^с \d{2}\.\d{2}\.\d{4} по \d{2}\.\d{2}\.\d{4}$/;
const ONLY_FORMULAS = process.argv.includes('--formulas');

// поле в json -> колонка «Истории воронки» -> колонка вкладки -> заголовок
//
// 01.08.2026 из вкладок убраны пять колонок воронки (перешли в карточку,
// заказали товаров, заказали на сумму, среднее кол-во заказов в день, среднее
// время доставки) — владельцу они мешали. Остались пять показательных.
// «История воронки» по-прежнему хранит ВСЕ метрики: убрано только отображение,
// данные не потеряны и колонки можно вернуть.
//
// Номера колонок сверены с живой вкладкой. До этого карта была смещена на
// единицу (воронка считалась начинающейся с AL, хотя начинается с AK), и
// запуск переписал бы весь блок на колонку правее.
const METRICS = [
  ['stockWb',    'C', 2,  null],                          // B, заголовок уже есть
  ['sharePct',   'D', 37, 'Доля в выручке, %'],           // AK
  ['toCartPct',  'F', 38, 'Конверсия в корзину, %'],      // AL
  ['toOrderPct', 'G', 39, 'Конверсия в заказ, %'],        // AM
  ['orders',     'H', 40, 'Заказали товаров, шт'],        // AN — на ней держится
  ['ordersDyn',  'J', 41, 'Динамика суммы заказов, %'],   // AO   «Дней до обнуления»
  ['buyoutPct',  'K', 42, 'Процент выкупа, %'],           // AP
  ['localPct',   'N', 43, 'Локальные заказы, %'],         // AQ
];
// в ИТОГО имеют смысл только счётные колонки (суммы), не проценты/средние
const TOTAL_FIELDS = new Set(['stockWb', 'orders']);
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
    console.log('Нет funnel/funnel-daily.json — сначала: node funnel.js');
    process.exit(1);
  }
  const daily = JSON.parse(fs.readFileSync(DAILY, 'utf-8'));
  const periods = [...new Set(daily.map(d => d.period))].sort();
  console.log('Периоды в базе:', periods.join('; '));

  // ---------- 1. лист-источник ----------
  if (ONLY_FORMULAS) {
    console.log(`\nРежим --formulas: лист «${HIST}» не трогаю.`);
  } else {
    const rows = [[
      'Период', 'Артикул поставщика', 'Остатки «Склад WB», шт',
      'Доля в выручке, %', 'Перешли в карточку', 'Конверсия в корзину, %',
      'Конверсия в заказ, %', 'Заказали товаров, шт', 'Заказали на сумму, ₽',
      'Динамика суммы заказов, %', 'Процент выкупа, %',
      'Среднее кол-во заказов в день, шт', 'Среднее время доставки, ч', 'Локальные заказы, %',
    ]];
    for (const d of daily) {
      rows.push([d.period, d.article, d.stockWb, d.sharePct, d.openCard, d.toCartPct,
                 d.toOrderPct, d.orders, d.ordersSum, d.ordersDyn, d.buyoutPct,
                 d.avgPerDay, d.deliveryH, d.localPct]);
    }
    console.log(`\nЗаливаю лист «${HIST}»...`);
    await post({ sheet: HIST, wipe: true, at: 1, rows: rows.slice(0, CHUNK) });
    for (let i = CHUNK; i < rows.length; i += CHUNK) {
      await post({ sheet: HIST, at: i + 1, rows: rows.slice(i, i + CHUNK) });
      process.stdout.write(`   строк ${Math.min(i + CHUNK, rows.length)} из ${rows.length}\r`);
    }
    console.log(`   строк ${rows.length} из ${rows.length}        `);
  }

  // ---------- 2. недельные вкладки ----------
  const all = await read('Динамика финансы', 'A1:A1');
  const tabs = all.sheets.filter(s => PERIOD_RE.test(s));
  console.log('\nНедельных вкладок:', tabs.length);

  for (const tab of tabs) {
    if (!periods.includes(tab)) {
      console.log(`\n${tab}: данных воронки нет — пропускаю (выгрузите: node funnel.js)`);
      continue;
    }
    const info = await read(tab, 'A1:A400');
    const totalRow = info.values.findIndex(r => String(r[0]).trim().toUpperCase() === 'ИТОГО') + 1;
    const lastData = (totalRow > 0 ? totalRow : info.lastRow + 1) - 1;

    const inPeriod = daily.filter(d => d.period === tab);
    const tabArts = new Set();
    for (let i = FIRST_ROW - 1; i < lastData; i++) {
      const a = String((info.values[i] || [])[0] || '').trim();
      if (a) tabArts.add(a);
    }
    const missing = inPeriod.filter(d => (d.orders || d.stockWb) && !tabArts.has(d.article));

    console.log(`\n${tab}: строки ${FIRST_ROW}..${lastData}, артикулов с данными: ${inPeriod.length}`);
    if (missing.length) {
      console.log(`   ВНИМАНИЕ: с данными, но без строки во вкладке: ` +
        missing.map(d => d.article).slice(0, 8).join(', ') + (missing.length > 8 ? ' ...' : ''));
    }

    for (const [field, histCol, tabCol, header] of METRICS) {
      if (header) {
        await post({ sheet: tab, at: 1, col: tabCol, rows: [[header]] });
      }
      const formulas = [];
      for (let n = FIRST_ROW; n <= lastData; n++) {
        formulas.push([`=SUMIFS(${col(histCol)};${col('B')};TRIM($A${n});${col('A')};"${tab}")`]);
      }
      await post({ sheet: tab, at: FIRST_ROW, col: tabCol, formulas });

      // ИТОГО ставим только счётным колонкам; проценты и средние по столбцу
      // складывать бессмысленно — их ячейки ИТОГО не трогаем
      if (totalRow && TOTAL_FIELDS.has(field)) {
        await post({
          sheet: tab, at: totalRow, col: tabCol,
          formulas: [[`=SUMIFS(${col(histCol)};${col('A')};"${tab}")`]],
        });
      }
      process.stdout.write(`   колонка ${tabCol} (${field}) готова   \r`);
    }
    console.log('   все колонки проставлены              ');
  }

  console.log('\nГотово.');
  process.exit(0);
})().catch(e => { console.log('\nОШИБКА:', e.message); process.exit(1); });
