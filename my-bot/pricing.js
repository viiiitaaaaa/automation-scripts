// Сводит таблицу сравнения с конкурентами и юнит-экономику из основной книги.
//
// Что делает:
//   1) читает 4 недельные вкладки книги «1» и считает по каждому артикулу
//      юнит-экономику за 4 недели;
//   2) кладёт её отдельным листом «Юнит-экономика» в книгу сравнения;
//   3) вставляет в лист «Сравнение» колонки K..V — формулы, которые тянут
//      эту экономику и считают сценарий «встали в цену конкурента».
//
// ЛОГИКА СЦЕНАРИЯ (главное):
//   Цена конкурента на витрине УЖЕ со скидкой СПП, как и наша. Сравнивать
//   витрины напрямую нельзя — комиссия WB считается от цены БЕЗ СПП.
//   Поэтому: цена конкурента без СПП = его витрина / (1 - СПП).
//   Наша новая цена без СПП = она же, и от неё пересчитывается комиссия,
//   налог и прибыль. Это и есть поправка, которой не хватало в ручном
//   расчёте: при подъёме цены комиссия растёт, и прибыль уже другая.
//
// Формула прибыли сверена с книгой (JK-577, 4 недели, расхождение 0,2 ₽):
//   прибыль = выручка со скидкой - себестоимость - комиссия - логистика
//             - хранение - реклама - (НДС+УСН)
//
// Почему вставка через буфер обмена: Apps Script книги сравнения умеет
// только дописывать строки (ни адресной записи, ни формул), а переписать
// лист целиком нельзя — в колонке A лежат вставленные картинки.
//
// Запуск: node pricing.js

const fs = require('fs');
const path = require('path');
const { attach } = require('./cdp-lite');

// ================== НАСТРОЙКИ ==================
// Недельные вкладки и «Сравнение» теперь в ОДНОЙ книге (слиты 01.08.2026),
// поэтому и читаем, и пишем по одному адресу — см. book.js.
const { BOOK_URL, BOOK_ID, gvizCsv } = require('./book');
const CMP = 'Сравнение';
const ECON = 'Юнит-экономика';
const PERIOD_RE = /^с \d{2}\.\d{2}\.\d{4} по \d{2}\.\d{2}\.\d{4}$/;
const FIRST_COL = 11;                       // K — с неё начинается наш блок
// ===============================================

const num = v => {
  const n = Number(String(v).replace(/\s| |₽|%/g, '').replace(',', '.'));
  return Number.isFinite(n) ? n : 0;
};
const r2 = x => Math.round(x * 100) / 100;

// Apps Script время от времени отвечает 404 и отдаёт HTML-страницу Google
// вместо ответа (04.08.2026: примерно один запрос из пяти). Раньше повтор был
// только на сетевую ошибку, а такой ответ уходил дальше и валил скрипт на
// JSON.parse — на середине прогона, уже переписав часть колонок. Теперь
// HTML-ответ и любой не-200 тоже считаются поводом повторить.
async function post(url, payload, tries = 6) {
  for (let t = 1; t <= tries; t++) {
    try {
      const r = await fetch(url, { method: 'POST', body: JSON.stringify(payload), signal: AbortSignal.timeout(300000) });
      const txt = (await r.text()).trim();
      if (r.ok && !txt.startsWith('<')) return txt;
      if (t === tries) throw new Error('Google Sheets ответил: ' + r.status + (txt.startsWith('<') ? ' (HTML вместо ответа)' : ''));
    } catch (e) {
      if (t === tries) throw e;
    }
    await new Promise(res => setTimeout(res, 3000 * t));
  }
}
const read1 = async (sheet, a1) => JSON.parse(await post(BOOK_URL, { read: { sheet, a1 } }));

// колонки недельной вкладки (0-based)
const C = { art: 0, costUnit: 3, qty: 6, revDisc: 9, cost: 16, comm: 17,
            commPct: 18, log: 19, stor: 20, ads: 21, tax: 25, profit: 26 };

(async () => {
  // ---------- 1. юнит-экономика за 4 недели ----------
  const info = await read1('Динамика финансы', 'A1:A1');
  // порядок ВАЖЕН: процент комиссии и себестоимость берём из последней
  // обработанной недели, поэтому сортируем по дате конца, а не по алфавиту
  // («с 29.06…» лексикографически больше «с 20.07…», это давало старый тариф)
  const endKey = s => s.match(/по (\d{2})\.(\d{2})\.(\d{4})/).slice(1).reverse().join('');
  const tabs = info.sheets.filter(s => PERIOD_RE.test(s))
    .sort((a, b) => endKey(a).localeCompare(endKey(b)));
  console.log('Недельных вкладок:', tabs.length, '\n  ' + tabs.join('\n  '));

  const agg = new Map();
  for (const tab of tabs) {
    const j = await read1(tab, 'A1:AK302');
    j.values.slice(1, 301).forEach(r => {
      const art = String(r[C.art] ?? '').trim();
      if (!art) return;
      if (!agg.has(art)) {
        agg.set(art, { art, qty: 0, rev: 0, cost: 0, comm: 0, log: 0, stor: 0,
                       ads: 0, tax: 0, profit: 0, costUnit: 0, commPct: 0 });
      }
      const a = agg.get(art);
      a.qty += num(r[C.qty]);      a.rev += num(r[C.revDisc]);
      a.cost += num(r[C.cost]);    a.comm += num(r[C.comm]);
      a.log += num(r[C.log]);      a.stor += num(r[C.stor]);
      a.ads += num(r[C.ads]);      a.tax += num(r[C.tax]);
      a.profit += num(r[C.profit]);
      // себестоимость и процент комиссии берём из САМОЙ СВЕЖЕЙ недели:
      // тарифы меняются, для сценария нужен текущий процент, а не средний
      a.costUnit = num(r[C.costUnit]) || a.costUnit;
      const p = num(r[C.commPct]);
      if (p) a.commPct = p;
    });
    console.log('   прочитана', tab);
  }

  const econRows = [[
    'Артикул поставщика', 'Продано за 4 нед, шт', 'Выручка за 4 нед, ₽',
    'Выручка на ед., ₽', 'Прибыль на ед. (факт), ₽', 'Себестоимость на ед., ₽',
    'Комиссия, %', 'Логистика на ед., ₽', 'Хранение на ед., ₽',
    'Реклама на ед., ₽', 'Налог+НДС, %',
  ]];
  const econ = new Map();
  for (const a of [...agg.values()].sort((x, y) => x.art.localeCompare(y.art))) {
    const per = v => (a.qty ? r2(v / a.qty) : 0);
    // процент комиссии: из свежей недели, иначе средний за период
    const commPct = a.commPct || (a.rev ? r2(100 * a.comm / a.rev) : 0);
    const taxPct = a.rev ? r2(100 * a.tax / a.rev) : 0;
    const row = {
      art: a.art, qty: a.qty, rev: r2(a.rev), revU: per(a.rev), profitU: per(a.profit),
      costU: a.costUnit || per(a.cost), commPct, logU: per(a.log),
      storU: per(a.stor), adsU: per(a.ads), taxPct,
    };
    econ.set(a.art, row);
    econRows.push([row.art, row.qty, row.rev, row.revU, row.profitU, row.costU,
                   row.commPct, row.logU, row.storU, row.adsU, row.taxPct]);
  }
  console.log(`\nАртикулов с экономикой: ${econRows.length - 1}`);

  console.log(`Заливаю лист «${ECON}»...`);
  const CH = 300;
  console.log('   ', await post(BOOK_URL, { sheet: ECON, rows: econRows.slice(0, CH), clear: true }));
  for (let i = CH; i < econRows.length; i += CH) {
    await post(BOOK_URL, { sheet: ECON, rows: econRows.slice(i, i + CH), clear: false });
  }

  // ---------- 2. читаем «Сравнение», чтобы понять раскладку строк ----------
  // Читаем ЧЕРЕЗ ENDPOINT, а не gviz: gviz отдаёт кэш и занижал длину листа,
  // из-за чего блок формул строился короче реального и хвост оставался пустым.
  // Здесь же берём формулы колонки B — по ним отличаем наши строки от строк
  // конкурента (у конкурента в B формула =IMAGE, у нас — текстовый артикул).
  const cmpInfo = JSON.parse(await post(BOOK_URL, { read: { sheet: CMP, a1: 'A1:C1000' } }));
  const LAST = cmpInfo.lastRow;

  // Для каждой строки конкурента — номер строки НАШЕГО товара выше по группе.
  const ownerRow = [];
  let cur = 0;
  for (let n = 2; n <= LAST; n++) {
    const i = n - 1;
    const bVal = (cmpInfo.values[i] || [])[1];
    const bFormula = (cmpInfo.formulas[i] || [])[1] || '';
    const isOur = bVal && !bFormula.startsWith('=IMAGE');
    if (isOur) cur = n;
    ownerRow[n] = cur;
  }
  const ourRows = ownerRow.filter((v, i) => v === i).length;
  console.log(`Лист «${CMP}»: строк ${LAST}, наших ${ourRows}`);

  // ---------- 3. блок формул K..V ----------
  // рядом с каждой цифрой «на единицу» — сумма за 4 недели: на единице
  // разница может выглядеть копеечной, а на обороте в сотни штук это деньги
  const HEAD = [
    'Продано за 4 нед, шт', 'Выручка за 4 нед, ₽', 'Выручка на ед. (факт), ₽',
    'Прибыль на ед. (факт), ₽', 'Прибыль за 4 нед (факт), ₽',
    'Прибыль на ед. при текущей цене, ₽', 'Прибыль за 4 нед при текущей цене, ₽',
    'Комиссия, %',
    'Цена конкурента без СПП, ₽', 'Изменение нашей цены, ₽', 'Новая цена после СПП, ₽',
    'Новая комиссия, ₽', 'Новая прибыль на ед., ₽', 'Новая прибыль за 4 нед, ₽',
  ];
  const block = [HEAD];
  const EMPTY_OUR = ['', '', '', '', '', '', '', ''];   // 8 колонок блока конкурента
  const EMPTY_CMP = ['', '', '', '', '', '', '', ''];   // 8 колонок блока нашего товара

  // Формулы ОДИНАКОВЫ для всех строк и сами решают, наша это строка или
  // конкурента. Раньше ветвление делалось в JS по снимку листа, и стоило
  // «Сравнению» подрасти, как блок уезжал вниз и колонки пустели.
  //
  // Признак строки — ISTEXT($B). Проверять «$B=""» НЕЛЬЗЯ: у наших строк
  // фото лежит в колонке A, а у строк конкурента — в B (формула =IMAGE),
  // то есть B у конкурента не пустая. В CSV картинка отдаётся пустой
  // строкой, поэтому по выгрузке подвох незаметен — видно только в самой
  // ячейке. Текст в B бывает только у наших артикулов.
  console.log(`Блок формул строится до строки ${LAST}`);
  for (let n = 2; n <= LAST; n++) {
    // TRIM: часть артикулов записана с висячим пробелом — без него
    // VLOOKUP не находит строку и колонка молча остаётся пустой
    const V = col => `VLOOKUP(TRIM($B${n});'${ECON}'!$A:$K;${col};0)`;
    const cost = V(6), comm = V(7), log = V(8), stor = V(9), ads = V(10), tax = V(11);
    const perUnitNow = `$F${n}*(1-${comm}/100-${tax}/100)-${cost}-${log}-${stor}-${ads}`;
    const our = f => `=IF(NOT(ISTEXT($B${n}));"";IFERROR(${f};""))`;

    // Значения из строки НАШЕГО товара, к которому относится этот конкурент.
    //
    // Здесь была идиома LOOKUP(2;1/ARRAYFORMULA(ISTEXT($B$2:$Bn));...). Она
    // выглядит правильной, но на этом листе возвращает ПЕРВУЮ нашу строку, а
    // не ближайшую сверху: все 315 строк конкурентов считались по СПП первого
    // товара (15,8 % у JK-577), хотя у остальных СПП 0–0,2 %. Цена конкурента
    // без СПП завышалась на 18,8 %, а за ней комиссия и вся новая прибыль.
    // Поэтому — прямая ссылка на строку группы: номер известен из чтения листа.
    const m = ownerRow[n] || 2;
    const up = c => `$${c}$${m}`;
    const A = `TRIM($B$${m})`;
    const E = c => `VLOOKUP(${A};'${ECON}'!$A:$K;${c};0)`;
    const noSpp = `$H${n}/(1-${up('G')}/100)`;
    const newU = `${noSpp}*(1-${E(7)}/100-${E(11)}/100)-${E(6)}-${E(8)}-${E(9)}-${E(10)}`;
    const cmp = f => `=IF(OR(ISTEXT($B${n});$C${n}="");"";IFERROR(${f};""))`;

    block.push([
      our(V(2)),
      our(V(3)),
      our(V(4)),
      our(V(5)),
      our(`ROUND(${V(5)}*${V(2)};0)`),
      our(`ROUND(${perUnitNow};0)`),
      our(`ROUND((${perUnitNow})*${V(2)};0)`),
      our(comm),
      cmp(`ROUND(${noSpp};0)`),
      cmp(`ROUND(${noSpp}-${up('F')};0)`),
      cmp(`$H${n}`),
      cmp(`ROUND(${noSpp}*${E(7)}/100;0)`),
      cmp(`ROUND(${newU};0)`),
      cmp(`ROUND((${newU})*${up('K')};0)`),
    ]);
  }

  // ---------- 4. запись блока K..X ----------
  // Пишем формулы напрямую через endpoint. Раньше блок вставлялся из буфера
  // обмена (клик по полю имени + Ctrl+V), потому что скрипт книги сравнения
  // умел только дописывать строки. После слияния книг единый скрипт принимает
  // {formulas, at, col} — и вся возня с буфером, фокусом окна и скрытыми
  // строками стала не нужна.
  // Блок заканчивается на X. Колонки Y и Z («Δ прибыли на ед.» и «Δ прибыли
  // за 4 нед») убраны по просьбе владельца: они только путали и всё равно
  // удалялись из таблицы руками. Не возвращать.
  const COLS = 'KLMNOPQRSTUVWX'.split('');
  const PART = 200;                               // формулы длинные — пишем частями
  for (let ci = 0; ci < COLS.length; ci++) {
    const colIdx = 11 + ci;                       // K = 11

    // Заголовок пишем ЗНАЧЕНИЕМ, а не формулой: setFormulas на обычном тексте
    // («Продано за 4 нед, шт») даёт в ячейке #ERROR! — Таблицы пытаются
    // разобрать его как формулу.
    await post(BOOK_URL, { sheet: CMP, at: 1, col: colIdx, rows: [[block[0][ci]]] });

    const column = block.slice(1).map(r => [r[ci]]);
    for (let i = 0; i < column.length; i += PART) {
      await post(BOOK_URL, {
        sheet: CMP, at: i + 2, col: colIdx, formulas: column.slice(i, i + PART),
      });
    }
    process.stdout.write(`   колонка ${COLS[ci]} готова (${ci + 1} из ${COLS.length})   \r`);
  }
  console.log(`   все ${COLS.length} колонок записаны, строк ${block.length}      `);

  // вернуть оформление и подсветку листа
  await post(BOOK_URL, { style: { sheets: [{ name: CMP, body: true, freezeCols: 3 }] } });

  console.log('\nГотово. Проверьте лист «Сравнение», колонки K..X.');
  process.exit(0);
})().catch(e => { console.log('\nОШИБКА:', e.message); process.exit(1); });

function parseCSV(text) {
  const rows = []; let row = [], cur = '', q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"' && text[i + 1] === '"') { cur += '"'; i++; }
      else if (c === '"') q = false;
      else cur += c;
    } else if (c === '"') q = true;
    else if (c === ',') { row.push(cur); cur = ''; }
    else if (c === '\n') { row.push(cur); rows.push(row); row = []; cur = ''; }
    else if (c !== '\r') cur += c;
  }
  if (cur || row.length) { row.push(cur); rows.push(row); }
  return rows;
}
