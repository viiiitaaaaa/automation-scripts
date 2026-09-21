// Подвязывает строки вкладки «Динамика финансы» к недельным вкладкам.
// Каждая строка периода тянет строку «ИТОГО» своей недельной вкладки, а та, в
// свою очередь, считается из «История отчетов» (см. reports-formulas.js).
//
// Раскладка взята из уже существовавшей формульной строки 112, где было
// ='1'!$H$333 и т.д. — то есть ссылки на ИТОГО недельного листа:
//   D Выручка ПРОДАЖИ      <- H333
//   E Выручка ВОЗВРАТЫ     <- I333
//   F Общая                =  D-E
//   G Себестоимость продаж <- Q333
//   H Логистика WB         <- T333
//   I Комиссия WB          <- R333
//   J Хранение WB          <- U333
//   P Налог+НДС 5%         <- Z333
//
// N «Реклама WB» здесь НЕ ставится. В «к перечислению» должна входить реклама,
// УДЕРЖАННАЯ ВБ за неделю, а во вкладке (V) лежит потраченная в кабинете —
// это разные суммы (04.08.2026: 77 173 против 81 625, остаток ВБ перенёс в
// следующий отчёт). N заполняет pay-compare.js прямо из отчётов ВБ.
//   C, S                   считаются от них же
//
// Строки, для которых недельной вкладки нет, не трогаются вообще.

const { BOOK_URL: SHEET_URL } = require('./book');   // единая книга, см. book.js
const DYN = 'Динамика финансы';

// Строку «ИТОГО» ищем в самой вкладке, а не задаём числом. Здесь была
// константа 333 из старой книги, тогда как на нынешних вкладках ИТОГО стоит
// в строке 302 — запуск с ней переписал бы «Динамику» ссылками на пустую
// строку и обнулил все недели. Так же ищет её и reports-formulas.js.
async function totalRowOf(tab) {
  const info = await read(tab, 'A1:A400');
  const i = info.values.findIndex(r => String(r[0]).trim().toUpperCase() === 'ИТОГО');
  return i >= 0 ? i + 1 : null;
}

const post = async (payload, tries = 4) => {
  for (let t = 1; t <= tries; t++) {
    try {
      const r = await fetch(SHEET_URL, {
        method: 'POST', body: JSON.stringify(payload), signal: AbortSignal.timeout(300000),
      });
      const b = (await r.text()).trim();
      if (b !== 'ok') throw new Error(b.slice(0, 80));
      return;
    } catch (e) {
      if (t === tries) throw e;
      await new Promise(res => setTimeout(res, 3000 * t));
    }
  }
};

const read = async (sheet, a1) => {
  const r = await fetch(SHEET_URL, {
    method: 'POST', body: JSON.stringify({ read: { sheet, a1 } }),
    signal: AbortSignal.timeout(180000),
  });
  return JSON.parse(await r.text());
};

(async () => {
  const info = await read(DYN, 'A1:S200');
  const tabs = new Set(info.sheets);

  let done = 0, skipped = 0;
  for (let i = 0; i < info.values.length; i++) {
    const period = String(info.values[i][1] || '').trim();
    if (!/^с \d{2}\.\d{2}\.\d{4} по \d{2}\.\d{2}\.\d{4}$/.test(period)) continue;

    if (!tabs.has(period)) { skipped++; continue; }   // нет недельной вкладки — не трогаем

    const totalRow = await totalRowOf(period);
    if (!totalRow) {
      console.log(`   ${period}: строки ИТОГО нет — пропускаю, чтобы не сбить формулы`);
      skipped++;
      continue;
    }

    const n = i + 1;
    const ref = c => `='${period}'!$${c}$${totalRow}`;
    // Раскладка сверена с живыми формулами листа 01.08.2026. Здесь были
    // смещены три ячейки: налог уезжал в «Прочие поступления» (16 вместо 15),
    // прибыль — в «Итог месяц» (19 вместо 18), а C ссылалась на R (прибыль)
    // вместо P. Колонки K и S — за владельцем, L,M,N,P,Q ставит pay-compare.js
    // из отчётов ВБ; здесь их не трогаем.
    const cells = {
      3:  `=F${n}-SUM(H${n}:N${n})+P${n}+Q${n}`,   // C Итого к перечислению
      4:  ref('H'),                                 // D Продажи
      5:  ref('I'),                                 // E Возвраты
      6:  `=D${n}-E${n}`,                           // F Общая
      7:  ref('Q'),                                 // G Себестоимость продаж
      8:  ref('T'),                                 // H Логистика WB
      9:  ref('R'),                                 // I Комиссия WB
      10: ref('U'),                                 // J Хранение WB
      15: ref('Z'),                                 // O Налог+НДС 5%
      18: `=F${n}-SUM(G${n}:O${n})+P${n}+Q${n}`,    // R Итого Прибыль
    };

    for (const col of Object.keys(cells).map(Number)) {
      await post({ sheet: DYN, at: n, col, formulas: [[cells[col]]] });
    }
    console.log(`   строка ${n}: ${period} -> подвязана (ИТОГО в строке ${totalRow})`);
    done++;
  }

  console.log(`\nПодвязано строк: ${done}. Пропущено (нет недельной вкладки): ${skipped}.`);
  process.exit(0);
})();
