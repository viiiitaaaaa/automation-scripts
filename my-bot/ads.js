// Выгружает историю рекламных расходов из кабинета WB Продвижение
// (https://cmp.wildberries.ru/campaigns/finances) и складывает их
// по дню и артикулу.
//
// Данные берём из того же API, что и сама страница «Финансы»:
//   GET https://cmp.wildberries.ru/api/v6/upd
// Запрос выполняется ИЗНУТРИ открытой вкладки кабинета (через CDP), поэтому
// куки и токен подставляются сами — отдельная авторизация не нужна.
//
// Почему не Playwright и не кнопка «Скачать в Excel»:
//   1) chromium.connectOverCDP на этом профиле виснет на подключении, а сырой
//      CDP работает — см. cdp-lite.js;
//   2) API отдаёт те же строки, что и Excel, но без разбора zip/xlsx.
//
// Запуск:
//   node ads.js              — последние 90 дней
//   node ads.js 2026-06-01   — с даты по сегодня
//   node ads.js 2026-06-01 2026-07-31
//   node ads.js --local      — пересобрать свёртку из ads/upd-raw.json, без скачивания

const fs = require('fs');
const path = require('path');
const { attach } = require('./cdp-lite');

// ================== НАСТРОЙКИ ==================
const FIN_URL = 'https://cmp.wildberries.ru/campaigns/finances';
const OUT = path.join(__dirname, 'ads');
const RAW = path.join(OUT, 'upd-raw.json');       // все строки как отдал API
const DAILY = path.join(OUT, 'ads-daily.json');   // свёрнуто по дню и артикулу
const PAGE = 500;                                 // строк за один запрос
const LOCAL = process.argv.includes('--local');   // не скачивать, взять upd-raw.json

// Кампании, названные свободным текстом вместо артикула.
// WB позволяет назвать кампанию как угодно, и тогда в выгрузке нет артикула —
// такие расходы иначе повисли бы вне строк вкладки.
// JK 577 — единственный автоматический ароматизатор в ассортименте
// (nmID 284422890, в кабинете «Ароматизатор в машину автоматический»),
// поэтому вся реклама с пометкой JK относится к нему.
// ВАЖНО: aroma-filter/4 — это ФИЛЬТРЫ для ароматизатора (nmID 412183906),
// отдельный товар; путать их нельзя.
const RULES = [
  { re: /\bJK\b|284422890/i, article: 'JK-577-aroma-avto/черный' },
];
// ===============================================

// Приводим название кампании к артикулу вкладки.
// Два регулярных шаблона имён у самого WB:
//   «neilon-20mm/бледно-розовый от 31.03.2026» — артикул + дата создания;
//   «aroma-filter/4 auto»                      — артикул + пометка автокампании.
function toArticle(campName) {
  const raw = String(campName || '').trim();
  for (const r of RULES) if (r.re.test(raw)) return r.article;

  const a = raw.replace(/\s+от\s+\d{2}\.\d{2}\.\d{4}\s*$/i, '')
               .replace(/\s+auto\s*$/i, '').trim();
  // Суффикс отрезаем, только если осталось похожее на артикул «имя/цвет».
  // Иначе «Кампания от 07.07.2026» схлопнулась бы в «Кампания», и разные
  // кампании без артикула слиплись бы в одну несуществующую строку.
  return a.includes('/') ? a : raw;
}

const arg = i => (process.argv[i] || '').match(/^\d{4}-\d{2}-\d{2}$/) ? process.argv[i] : null;
const today = new Date();
const iso = d => d.toISOString().slice(0, 10);
const FROM = arg(2) || iso(new Date(today.getTime() - 90 * 864e5));
const TO = arg(3) || iso(today);

if (!fs.existsSync(OUT)) fs.mkdirSync(OUT, { recursive: true });

// Понедельник–воскресенье: недельные вкладки в таблице названы именно так,
// поэтому по дате сразу считаем ярлык периода — тогда расход встанет в свою
// неделю даже для вкладок, которых ещё нет.
function weekLabel(ymd) {
  const [y, m, d] = ymd.split('-').map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  const shift = (dt.getUTCDay() + 6) % 7;            // Пн=0 ... Вс=6
  const mon = new Date(dt.getTime() - shift * 864e5);
  const sun = new Date(mon.getTime() + 6 * 864e5);
  const ru = x => String(x.getUTCDate()).padStart(2, '0') + '.' +
                  String(x.getUTCMonth() + 1).padStart(2, '0') + '.' + x.getUTCFullYear();
  return `с ${ru(mon)} по ${ru(sun)}`;
}

// «Дата списания» в интерфейсе кабинета — это upd_time (уже в +03:00),
// а не time: у time дата на сутки раньше, это момент оказания услуги.
// Сверено со страницей: строка neilon-20mm/черный на 142 ₽ показана как
// 30.07.26 при time=2026-07-29 и upd_time=2026-07-30.
const spendDate = u => String(u.upd_time).slice(0, 10);

// один запрос к API из контекста страницы
const fetchPage = (t, page) => {
  const url = 'https://cmp.wildberries.ru/api/v6/upd'
    + `?page_number=${page}&page_size=${PAGE}`
    + '&bid_type=%5B0%5D&attribute=all'
    + `&from=${FROM}T00:00:00%2B03:00&to=${TO}T23:59:59%2B03:00`;

  return t.evaluate(`
    fetch(${JSON.stringify(url)}, {
      credentials: 'include',
      headers: {
        accept: 'application/json, text/plain, */*',
        lang: 'ru',
        authorizev3: localStorage.getItem('access-token'),
        'x-supplierid': (document.cookie.match(/x-supplier-id-external=([^;]+)/) || [])[1],
      },
    }).then(async r => JSON.stringify({ status: r.status, body: await r.text() }))
  `).then(JSON.parse);
};

(async () => {
  console.log(`Период выгрузки: ${FROM} .. ${TO}\n`);

  const all = [];
  let total = null;

  if (LOCAL) {
    if (!fs.existsSync(RAW)) {
      console.log('Нет ads/upd-raw.json — сначала запустите node ads.js без --local');
      process.exit(1);
    }
    all.push(...JSON.parse(fs.readFileSync(RAW, 'utf-8')));
    total = all.length;
    console.log('Режим --local: беру', total, 'записей из ads/upd-raw.json\n');
  } else {
  const t = await attach('cmp.wildberries.ru', FIN_URL);
  console.log('вкладка:', t.url);

  for (let page = 1; ; page++) {
    const r = await fetchPage(t, page);
    if (r.status !== 200) {
      throw new Error(`API вернул ${r.status}: ${r.body.slice(0, 200)}`);
    }
    const data = JSON.parse(r.body);
    const rows = data.upd_info || [];
    if (total === null) {
      total = data.total_count;
      console.log('всего записей по данным API:', total);
    }
    all.push(...rows);
    process.stdout.write(`   получено ${all.length} из ${total}\r`);
    if (!rows.length || all.length >= total) break;
    if (page > 200) { console.log('\nслишком много страниц, обрываю'); break; }
  }
  t.close();
  console.log(`   получено ${all.length} из ${total}       \n`);
  }

  if (!all.length) {
    console.log('Записей нет. Кабинет открыт и залогинен?');
    process.exit(1);
  }

  if (!LOCAL) fs.writeFileSync(RAW, JSON.stringify(all, null, 1), 'utf-8');

  // ---------- свёртка по дню и артикулу ----------
  // За один день на один артикул кабинет пишет несколько списаний
  // (разные кампании, доборы бюджета) — складываем их в одну сумму.
  const agg = new Map();
  const renamed = new Map();          // исходное имя кампании -> артикул
  for (const u of all) {
    const date = spendDate(u);
    const raw = String(u.camp_name || '').trim();
    const art = toArticle(raw);
    if (raw !== art) renamed.set(raw, art);
    if (!art || !/^\d{4}-\d{2}-\d{2}$/.test(date)) continue;
    const key = date + ' ' + art;
    if (!agg.has(key)) {
      agg.set(key, { period: weekLabel(date), date, article: art, sum: 0, ops: 0, camps: new Set() });
    }
    const a = agg.get(key);
    a.sum += Number(u.upd_sum) || 0;
    a.ops++;
    a.camps.add(raw);
  }

  const daily = [...agg.values()].sort((a, b) =>
    a.date.localeCompare(b.date) || a.article.localeCompare(b.article));
  daily.forEach(d => {
    d.sum = Math.round(d.sum * 100) / 100;
    d.camps = [...d.camps].join('; ');   // исходные названия кампаний — для сверки
  });

  fs.writeFileSync(DAILY, JSON.stringify(daily, null, 1), 'utf-8');

  const grand = daily.reduce((s, d) => s + d.sum, 0);
  const merged = daily.filter(d => d.ops > 1).length;
  const byPeriod = new Map();
  for (const d of daily) byPeriod.set(d.period, (byPeriod.get(d.period) || 0) + d.sum);

  console.log(`Строк списаний: ${all.length}`);
  console.log(`После свёртки (день + артикул): ${daily.length}, из них склеено из нескольких списаний: ${merged}`);
  console.log(`Артикулов: ${new Set(daily.map(d => d.article)).size}`);
  console.log(`Общая сумма: ${grand.toLocaleString('ru-RU')} ₽\n`);
  if (renamed.size) {
    console.log('Кампании, приведённые к артикулу:');
    for (const [from, to] of [...renamed].sort())
      console.log(`   "${from}"  ->  ${to}`);
    console.log('');
  }

  console.log('По неделям:');
  for (const [p, s] of [...byPeriod].sort())
    console.log(`   ${p}  ${Math.round(s).toLocaleString('ru-RU')} ₽`);

  console.log(`\nСырьё — ${path.relative(__dirname, RAW)}, свёртка — ${path.relative(__dirname, DAILY)}`);
  console.log('Дальше: node ads-upload.js');
  process.exit(0);
})().catch(e => { console.log('\nОШИБКА:', e.message); process.exit(1); });
