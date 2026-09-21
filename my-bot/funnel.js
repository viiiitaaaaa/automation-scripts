// Выгружает «Воронку продаж» интерактивного отчёта WB
// (https://seller.wildberries.ru/content-analytics/interactive-report/main)
// по неделям, с детализацией до артикула.
//
// Данные берём из того же API, что и таблица на странице:
//   POST seller-content.wildberries.ru/.../api/v1/sales-funnel/report
// с заголовками AuthorizeV3 (localStorage wb-eu-passport-v2.access-token)
// и Wb-Seller-Lk (localStorage wb-eu-portal.seller-token), изнутри вкладки.
//
// ВАЖНО: API отдаёт максимум 50 товаров за запрос и игнорирует
// page/limit/offset. Поэтому весь ассортимент запрашивается БАТЧАМИ по 50
// nmId через параметр nms (список — из my-goods.json).
//
// «Динамика суммы заказов» считается к prevPeriod — предыдущей неделе.
// «Остатки Склад WB» — текущий остаток на момент запроса, у прошлых недель
// истории нет (решение владельца: работаем с тем, что есть).
//
// Запуск:
//   node funnel.js                          — прошлая полная неделя (Пн–Вс)
//   node funnel.js 2026-07-20 2026-07-26    — конкретная неделя
//   node funnel.js --tabs                   — все недели, по которым есть вкладки

const fs = require('fs');
const path = require('path');
const { attach } = require('./cdp-lite');

// ================== НАСТРОЙКИ ==================
const PAGE = 'https://seller.wildberries.ru/content-analytics/interactive-report/main';
const API = 'https://seller-content.wildberries.ru/ns/analytics-api/content-analytics/api/v1/sales-funnel/report';
const { BOOK_URL: SHEET_URL } = require('./book');   // единая книга, см. book.js
const OUT = path.join(__dirname, 'funnel');
const DAILY = path.join(OUT, 'funnel-daily.json');
const BATCH = 50;                       // жёсткий потолок API
const PERIOD_RE = /^с \d{2}\.\d{2}\.\d{4} по \d{2}\.\d{2}\.\d{4}$/;
// ===============================================

fs.mkdirSync(OUT, { recursive: true });

const iso = d => d.toISOString().slice(0, 10);
const arg = i => (process.argv[i] || '').match(/^\d{4}-\d{2}-\d{2}$/) ? process.argv[i] : null;

function lastWeek() {
  const now = new Date();
  const d = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));
  const mon = new Date(d.getTime() - (((d.getUTCDay() + 6) % 7) + 7) * 864e5);
  return [iso(mon), iso(new Date(mon.getTime() + 6 * 864e5))];
}

const ruLabel = (from, to) => {
  const ru = s => s.split('-').reverse().join('.');
  return `с ${ru(from)} по ${ru(to)}`;
};
const shift = (ymd, days) => iso(new Date(new Date(ymd + 'T00:00:00Z').getTime() + days * 864e5));

// часы из {days, hours, mins}
const hours = t => t ? Math.round((t.days * 24 + t.hours + t.mins / 60) * 10) / 10 : 0;
const cur = f => (f && typeof f.current === 'number') ? f.current : 0;

async function fetchWeek(t, from, to, nmIds) {
  const label = ruLabel(from, to);
  const rows = [];
  for (let i = 0; i < nmIds.length; i += BATCH) {
    const body = {
      currentPeriod: { start: from, end: to },
      prevPeriod: { start: shift(from, -7), end: shift(to, -7) },
      subjects: [], brands: [], nms: nmIds.slice(i, i + BATCH), tagIds: [],
      skipDeletedNm: false,
      orderBy: { field: 'orders', mode: 'desc' },
    };
    const r = JSON.parse(await t.evaluate(`
      fetch(${JSON.stringify(API)}, {
        method: 'POST', credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'AuthorizeV3': localStorage.getItem('wb-eu-passport-v2.access-token'),
          'Wb-Seller-Lk': localStorage.getItem('wb-eu-portal.seller-token'),
        },
        body: ${JSON.stringify(JSON.stringify(body))},
      }).then(async x => JSON.stringify({ s: x.status, b: await x.text() }))
    `));
    if (r.s !== 200) throw new Error(`API вернул ${r.s}: ${r.b.slice(0, 150)}`);
    const items = ((JSON.parse(r.b).data || {}).groups || []).flatMap(g => g.itemsGroup || []);
    for (const it of items) {
      rows.push({
        period: label,
        article: String(it.vendorCode || '').trim(),
        stockWb: it.stockWbQty || 0,
        sharePct: cur(it.shareOrderPercent),          // доля в выручке, %
        openCard: cur(it.openCard),                   // перешли в карточку
        toCartPct: cur(it.openToCart),                // конверсия в корзину, %
        toOrderPct: cur(it.cartToOrder),              // конверсия в заказ, %
        orders: cur(it.orders),                       // заказали товаров, шт
        ordersSum: cur(it.ordersSum),                 // заказали на сумму, ₽
        ordersDyn: (it.ordersSum && typeof it.ordersSum.dynamics === 'number')
          ? it.ordersSum.dynamics : '',               // динамика суммы заказов, %
        buyoutPct: cur(it.buyoutPercent),             // процент выкупа, %
        avgPerDay: cur(it.avgOrderCountPerDay),       // среднее заказов в день, шт
        deliveryH: hours(it.timeToReady && it.timeToReady.current), // ср. время доставки, ч
        localPct: cur(it.localizationPercent),        // локальные заказы, %
      });
    }
    process.stdout.write(`   ${label}: получено ${rows.length} из ${nmIds.length}\r`);
  }
  console.log(`   ${label}: получено ${rows.length} из ${nmIds.length}       `);
  return rows;
}

(async () => {
  const goods = JSON.parse(fs.readFileSync(path.join(__dirname, 'my-goods.json'), 'utf-8'));
  const nmIds = goods.map(g => Number(g.id)).filter(Boolean);
  console.log('Номенклатур в my-goods.json:', nmIds.length);

  // какие недели качать
  let weeks = [];
  if (process.argv.includes('--tabs')) {
    const r = await fetch(SHEET_URL, {
      method: 'POST', body: JSON.stringify({ read: { sheet: 'Динамика финансы', a1: 'A1:A1' } }),
      signal: AbortSignal.timeout(300000),
    });
    const tabs = JSON.parse(await r.text()).sheets.filter(s => PERIOD_RE.test(s));
    weeks = tabs.map(tab => {
      const m = tab.match(/с (\d{2})\.(\d{2})\.(\d{4}) по (\d{2})\.(\d{2})\.(\d{4})/);
      return [`${m[3]}-${m[2]}-${m[1]}`, `${m[6]}-${m[5]}-${m[4]}`];
    });
  } else if (arg(2)) {
    weeks = [[arg(2), arg(3) || shift(arg(2), 6)]];
  } else {
    weeks = [lastWeek()];
  }
  console.log('Недели:', weeks.map(w => ruLabel(...w)).join('; '), '\n');

  const t = await attach('content-analytics/interactive-report', PAGE);
  const fresh = [];
  for (const [from, to] of weeks) fresh.push(...await fetchWeek(t, from, to, nmIds));
  t.close();

  // копим по периодам: свежие недели перезаписываем, остальные не трогаем
  const freshPeriods = new Set(fresh.map(r => r.period));
  const old = fs.existsSync(DAILY) ? JSON.parse(fs.readFileSync(DAILY, 'utf-8')) : [];
  const kept = old.filter(r => !freshPeriods.has(r.period));
  kept.push(...fresh);
  kept.sort((a, b) => a.period.localeCompare(b.period) || a.article.localeCompare(b.article));
  fs.writeFileSync(DAILY, JSON.stringify(kept, null, 1), 'utf-8');

  for (const p of [...freshPeriods].sort()) {
    const rows = kept.filter(r => r.period === p);
    console.log(`\n${p}: артикулов ${rows.length}, заказали ${rows.reduce((s, r) => s + r.orders, 0)} шт` +
      ` на ${Math.round(rows.reduce((s, r) => s + r.ordersSum, 0)).toLocaleString('ru-RU')} ₽,` +
      ` остатки WB ${rows.reduce((s, r) => s + r.stockWb, 0)} шт`);
  }
  console.log(`\nПериодов в базе: ${new Set(kept.map(r => r.period)).size}. Свёртка — ${path.relative(__dirname, DAILY)}`);
  console.log('Дальше: node funnel-upload.js');
  process.exit(0);
})().catch(e => { console.log('\nОШИБКА:', e.message); process.exit(1); });
