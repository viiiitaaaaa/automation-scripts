// Считает ценовые сценарии по ВСЕМУ ассортименту и кладёт их листом
// «Цены — сценарии» в рабочую книгу.
//
// Источники (все в той же книге, читаются через gviz-CSV):
//   «Цены»           — наши цены: до скидки, скидка %, после скидки, СПП %, витрина;
//   «Evirma»         — выдача WB по каждому нашему артикулу (конкуренты и их цены);
//   «Юнит-экономика» — расходы на единицу за 4 недели (кладёт pricing.js).
//
// ЛОГИКА (та же, что в pricing.js):
//   цена конкурента на витрине — со СПП, комиссия WB считается от цены БЕЗ СПП,
//   поэтому competitor_без_СПП = витрина / (1 - СПП) и от неё пересчитываются
//   комиссия, налог и прибыль.
//
//   прибыль/ед = P*(1 - комиссия% - налог%) - себестоимость - логистика
//                - хранение - реклама
//   отсюда цена под заданную прибыль T:
//     P = (T + себестоимость + логистика + хранение + реклама) / (1 - к% - н%)
//
// Запуск: node price-scenarios.js

const { attach } = require('./cdp-lite');

// ================== НАСТРОЙКИ ==================
const { BOOK_URL, BOOK_ID, gvizCsv } = require('./book');   // единая книга, см. book.js
const OUT_SHEET = 'Цены — сценарии';
const OUR_BRANDS = ['zaomi', 'mitronium'];   // свои бренды в выдаче не конкуренты
// Полоса отбора конкурентов вокруг нашей витрины. Шире 0.6–2.0 в выдачу лезут
// товары другой категории (силиконовый ремешок за 285 против нашего
// металлического за 1089) и медиана уезжает вниз — тогда почти весь
// ассортимент ложно помечался «мы дороже рынка».
const LO = 0.6, HI = 2.0;
const MIN_COMP = 3;                          // меньше — статистика не показательна
// ===============================================

const num = v => {
  const n = Number(String(v).replace(/\s| |₽|%/g, '').replace(',', '.'));
  return Number.isFinite(n) ? n : 0;
};
const r0 = x => Math.round(x);
const r2 = x => Math.round(x * 100) / 100;
const median = a => {
  if (!a.length) return 0;
  const s = [...a].sort((x, y) => x - y);
  const m = s.length >> 1;
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
};

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

async function post(payload, tries = 4) {
  for (let t = 1; t <= tries; t++) {
    try {
      const r = await fetch(BOOK_URL, { method: 'POST', body: JSON.stringify(payload), signal: AbortSignal.timeout(300000) });
      return (await r.text()).trim();
    } catch (e) { if (t === tries) throw e; await new Promise(res => setTimeout(res, 3000 * t)); }
  }
}

(async () => {
  const t = await attach(BOOK_ID);
  const get = async sheet => {
    const u = gvizCsv(sheet);
    return parseCSV(await t.evaluate(`fetch(${JSON.stringify(u)}, { credentials: 'include' }).then(x => x.text())`));
  };

  const prices = await get('Цены');
  const evirma = await get('Evirma');
  const econRows = await get('Юнит-экономика');
  t.close();
  console.log(`Цены: ${prices.length - 1} | Evirma: ${evirma.length - 1} | Юнит-экономика: ${econRows.length - 1}`);

  // экономика по артикулу продавца
  const econ = new Map();
  econRows.slice(1).forEach(r => {
    if (!r[0]) return;
    econ.set(r[0].trim(), {
      qty: num(r[1]), profitU: num(r[4]), cost: num(r[5]), comm: num(r[6]),
      log: num(r[7]), stor: num(r[8]), ads: num(r[9]), tax: num(r[10]),
    });
  });

  // конкуренты по нашему nmID
  const comp = new Map();
  evirma.slice(1).forEach(r => {
    const asked = String(r[0] || '').trim();
    const brand = String(r[2] || '').toLowerCase();
    const price = num(r[9]);
    if (!asked || !price) return;
    if (OUR_BRANDS.some(b => brand.includes(b))) return;      // свой бренд
    if (!comp.has(asked)) comp.set(asked, []);
    comp.get(asked).push(price);
  });

  const out = [[
    'Артикул продавца', 'Артикул WB', 'Название',
    'Цена сейчас без СПП, ₽', 'СПП, %', 'Витрина сейчас, ₽',
    'Продано за 4 нед, шт', 'Прибыль на ед. сейчас, ₽', 'Прибыль за 4 нед сейчас, ₽',
    'Цена безубыточности без СПП, ₽', 'Витрина безубыточности, ₽',
    'Конкурентов', 'Мин. витрина конк., ₽', 'Медиана конк., ₽', 'Макс. витрина конк., ₽',
    'Сценарий: цена без СПП, ₽', 'Изменение цены, ₽', 'Сценарий: витрина, ₽',
    'Новая комиссия, ₽', 'Новая прибыль на ед., ₽', 'Δ прибыли на ед., ₽',
    'Прибыль за 4 нед по сценарию, ₽', 'Δ прибыли за 4 нед, ₽', 'Рекомендация',
  ]];

  let noEcon = 0, noComp = 0;
  for (const r of prices.slice(1)) {
    const nmId = String(r[0] || '').trim();
    const art = String(r[1] || '').trim();
    const name = String(r[3] || '').trim();
    const price = num(r[6]);          // цена после скидки продавца = наша цена без СПП
    const spp = num(r[7]);
    const shelf = num(r[8]);          // витрина
    if (!art) continue;

    const e = econ.get(art);
    if (!e) { noEcon++; }

    const k = e ? (1 - e.comm / 100 - e.tax / 100) : 0;      // доля, остающаяся с цены
    const fixed = e ? (e.cost + e.log + e.stor + e.ads) : 0; // расходы на единицу, не зависящие от цены
    const profitAt = p => (e && k > 0) ? p * k - fixed : '';
    // без цены в листе «Цены» прибыль считать НЕЛЬЗЯ: от нуля она выходит
    // равной минус расходам, и товар ложно попадает в убыточные
    const profitNow = (e && price) ? r0(profitAt(price)) : '';
    const breakEven = (e && k > 0) ? fixed / k : 0;

    const list = (comp.get(nmId) || []).filter(p => shelf ? (p >= shelf * LO && p <= shelf * HI) : true);
    if (!list.length) noComp++;
    const med = median(list);

    // сценарий: встаём в медиану конкурентов
    const newNoSpp = med ? med / (1 - spp / 100) : 0;
    const newProfit = (e && med && k > 0) ? profitAt(newNoSpp) : '';
    const newComm = (e && med) ? newNoSpp * e.comm / 100 : '';

    let rec = '';
    if (!price) rec = 'нет цены в листе «Цены» — нечего считать';
    else if (!e) rec = 'нет продаж за 4 недели — экономика неизвестна';
    else if (list.length < MIN_COMP) rec = `конкурентов мало (${list.length}) — сравнивать не с чем`;
    else if (profitNow < 0 && newProfit > 0) rec = 'ПОДНЯТЬ до медианы — выйдет из минуса';
    else if (profitNow < 0) rec = 'убыточен даже по цене конкурентов — смотреть закупку/рекламу';
    else if (newNoSpp > price * 1.15) rec = 'есть запас — можно поднять';
    else if (newNoSpp < price * 0.8) rec = 'мы заметно дороже рынка — риск потери спроса';
    else rec = 'цена в рынке';

    out.push([
      art, nmId, name,
      price, spp, shelf,
      e ? e.qty : '', profitNow, e ? r0(profitNow * e.qty) : '',
      breakEven ? r0(breakEven) : '', breakEven ? r0(breakEven * (1 - spp / 100)) : '',
      list.length, list.length ? r0(Math.min(...list)) : '', med ? r0(med) : '',
      list.length ? r0(Math.max(...list)) : '',
      newNoSpp ? r0(newNoSpp) : '', newNoSpp ? r0(newNoSpp - price) : '',
      med ? r0(med) : '',
      newComm === '' ? '' : r0(newComm),
      newProfit === '' ? '' : r0(newProfit),
      (newProfit === '' || profitNow === '') ? '' : r0(newProfit - profitNow),
      (newProfit === '' || !e) ? '' : r0(newProfit * e.qty),
      (newProfit === '' || profitNow === '' || !e) ? '' : r0((newProfit - profitNow) * e.qty),
      rec,
    ]);
  }

  console.log(`\nСтрок в сценариях: ${out.length - 1} | без экономики: ${noEcon} | без конкурентов: ${noComp}`);
  console.log(`Заливаю лист «${OUT_SHEET}»...`);
  const CH = 300;
  console.log('   ', await post({ sheet: OUT_SHEET, rows: out.slice(0, CH), clear: true }));
  for (let i = CH; i < out.length; i += CH) {
    await post({ sheet: OUT_SHEET, rows: out.slice(i, i + CH), clear: false });
  }

  // лист пересоздаётся при каждом прогоне — возвращаем оформление книги
  await post({ style: { sheets: [{ name: OUT_SHEET, body: true, freezeCols: 3 }] } });

  // краткая сводка
  // индексы считаем от шапки, а не руками: при вставке колонки они уезжают
  const H = out[0];
  const iProfitNow = H.indexOf('Прибыль на ед. сейчас, ₽');
  const iDeltaTot = H.indexOf('Δ прибыли за 4 нед, ₽');
  const iRec = H.indexOf('Рекомендация');
  const rows = out.slice(1).filter(r => typeof r[iProfitNow] === 'number');
  const loss = rows.filter(r => r[iProfitNow] < 0);
  const canRaise = out.slice(1).filter(r => String(r[iRec]).startsWith('ПОДНЯТЬ'));
  const gain = canRaise.reduce((s, r) => s + (typeof r[iDeltaTot] === 'number' ? r[iDeltaTot] : 0), 0);
  console.log(`\nУбыточных по текущей цене: ${loss.length} из ${rows.length}`);
  console.log(`Рекомендовано поднять: ${canRaise.length}`);
  console.log(`Потенциал за 4 недели: +${r0(gain).toLocaleString('ru-RU')} ₽`);
  process.exit(0);
})().catch(e => { console.log('\nОШИБКА:', e.message); process.exit(1); });
