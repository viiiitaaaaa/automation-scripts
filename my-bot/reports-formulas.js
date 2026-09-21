// Проставляет в недельных вкладках формулы, тянущие данные из листа
// «История отчетов» строго за период этой вкладки.
//
// Раскладка «Истории»: колонка A — период, дальше все 84 колонки отчёта,
// то есть каждая колонка отчёта сдвинута на одну вправо относительно Sheet1.
//   A  Период
//   G  Артикул поставщика          (в Sheet1 F)
//   L  Обоснование для оплаты      (K)   — «Продажа» / «Возврат»
//   O  Кол-во                      (N)
//   P  Цена розничная              (O)
//   Q  Вайлдберриз реализовал      (P)
//   U  Цена розн. с уч. соглас. скидки (T)
//   AI К перечислению Продавцу     (AH)
//   AL Услуги по доставке          (AK)
//   BI Хранение                    (BH)

const { BOOK_URL: SHEET_URL } = require('./book');   // единая книга, см. book.js
const HIST = 'История отчетов';
const FIRST_ROW = 2;

// недельные вкладки находим сами по имени: оно же и есть период в колонке A «Истории»
const PERIOD_RE = /^с \d{2}\.\d{2}\.\d{4} по \d{2}\.\d{2}\.\d{4}$/;

// Прямая ссылка, БЕЗ INDIRECT. INDIRECT волатилен: пересчитывается при любом
// изменении в книге и не кэшируется. На ~8000 формул по листу в 14 тыс. строк
// это вешает таблицу намертво. Прямые ссылки пересчитываются только когда
// меняется сам источник.
const ind = c => `'${HIST}'!${c}:${c}`;

function build(period, n) {
  // SUMIFS по артикулу + периоду, при необходимости с фильтром по обоснованию
  const S = (col, basis) => basis
    ? `SUMIFS(${ind(col)};${ind('G')};$A${n};${ind('L')};"${basis}";${ind('A')};"${period}")`
    : `SUMIFS(${ind(col)};${ind('G')};$A${n};${ind('A')};"${period}")`;

  return {
    5:  `=${S('O', 'Продажа')}`,                               // E Кол-во ПРОДАЖИ
    6:  `=${S('O', 'Возврат')}`,                               // F Кол-во ВОЗВРАТЫ
    7:  `=E${n}-F${n}`,                                        // G Кол-во ПРОДАЖИ-ВОЗВРАТЫ
    8:  `=${S('P', 'Продажа')}`,                               // H Выручка ПРОДАЖИ
    9:  `=${S('P', 'Возврат')}`,                               // I Выручка ВОЗВРАТЫ
    10: `=${S('U', 'Продажа')}-${S('U', 'Возврат')}`,          // J Выручка с уч. скидки
    11: `=${S('Q', 'Продажа')}`,                               // K Реализ ПРОДАЖА
    12: `=${S('Q', 'Возврат')}`,                               // L Реализ ВОЗВРАТ
    13: `=K${n}-L${n}`,                                        // M Реализ СУММ
    14: `=${S('AI', 'Продажа')}`,                              // N К перечисл ПРОДАЖА
    15: `=${S('AI', 'Возврат')}`,                              // O К перечисл ВОЗВРАТ
    16: `=N${n}-O${n}`,                                        // P К перечисл СУММА
    20: `=${S('AL')}`,                                         // T Логистика
    // U «Хранение» НЕ трогаем: в отчёте хранение идёт отдельными строками
    // с пустым артикулом (10 строк на период), разнести его по SKU нельзя.
    // Сумма в отчёте — 8 637 ₽ за период, а во вкладке 16 834 ₽, то есть
    // источник у этой колонки другой.
  };
}

async function post(payload, tries = 4) {
  for (let t = 1; t <= tries; t++) {
    try {
      const r = await fetch(SHEET_URL, {
        method: 'POST', body: JSON.stringify(payload),
        signal: AbortSignal.timeout(300000),
      });
      const body = (await r.text()).trim();
      if (body !== 'ok') throw new Error(body.slice(0, 80));
      return;
    } catch (e) {
      if (t === tries) throw e;
      console.log(`   попытка ${t}: ${e.message}, повторяю...`);
      await new Promise(res => setTimeout(res, 3000 * t));
    }
  }
}

const read = async (sheet, a1) => {
  const r = await fetch(SHEET_URL, {
    method: 'POST', body: JSON.stringify({ read: { sheet, a1 } }),
    signal: AbortSignal.timeout(180000),
  });
  return JSON.parse(await r.text());
};

// колонки, которым в строке «ИТОГО» ставим сумму по столбцу
// (U считаем тоже — сами данные там не наши, но итог по столбцу корректен)
const TOTAL_COLS = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 20, 21];
const letter = c => (c <= 26 ? '' : String.fromCharCode(64 + Math.floor((c - 1) / 26))) +
                    String.fromCharCode(65 + ((c - 1) % 26));

(async () => {
  const all = await read('Динамика финансы', 'A1:A1');
  const TABS = all.sheets.filter(s => PERIOD_RE.test(s));
  console.log('Недельных вкладок найдено:', TABS.length, '\n  ' + TABS.join('\n  '));

  for (const tab of TABS) {
    const info = await read(tab, 'A1:A400');
    // последняя строка данных — та, что перед «ИТОГО»
    const totalRow = info.values.findIndex(r => String(r[0]).trim().toUpperCase() === 'ИТОГО') + 1;
    const lastData = (totalRow > 0 ? totalRow : info.lastRow + 1) - 1;

    const rows = [];
    for (let n = FIRST_ROW; n <= lastData; n++) rows.push(build(tab, n));

    console.log(`\n${tab}: данные ${FIRST_ROW}..${lastData}` +
                (totalRow ? `, ИТОГО в строке ${totalRow}` : ', строки ИТОГО нет'));

    for (const col of Object.keys(rows[0]).map(Number)) {
      await post({ sheet: tab, at: FIRST_ROW, col, formulas: rows.map(r => [r[col]]) });
      process.stdout.write(`   колонка ${col} готова\r`);
    }
    console.log('   колонки данных проставлены       ');

    if (totalRow) {
      for (const col of TOTAL_COLS) {
        const L = letter(col);
        // T (логистика): берём полный итог периода, а не сумму строк.
        // Часть логистики висит на служебной строке «неопознанный товар» без
        // артикула — в разрезе SKU её показать негде, но в итог она входит,
        // иначе цифра не сойдётся с «Динамика финансы».
        const f = col === 20
          ? `=SUMIFS(${ind('AL')};${ind('A')};"${tab}")`
          : `=SUM(${L}${FIRST_ROW}:${L}${lastData})`;
        await post({ sheet: tab, at: totalRow, col, formulas: [[f]] });
      }
      console.log('   строка ИТОГО пересчитана');
    }
  }
  console.log('\nГотово.');
  process.exit(0);
})();
