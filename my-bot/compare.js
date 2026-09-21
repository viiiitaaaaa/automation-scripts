const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

// ================== НАСТРОЙКИ ==================
const { BOOK_URL: SHEET_URL } = require('./book');   // единая книга, см. book.js
const SHEET_NAME = 'Сравнение';
const CSV_FILE = path.join(__dirname, 'spp8.csv');
const EXCEL_DIR = path.join(__dirname, 'excel');
const CACHE_FILE = path.join(__dirname, 'photo-cache.json');
const COLOR_FILE = path.join(__dirname, 'color-cache.json');
const GOODS_FILE = path.join(__dirname, 'my-goods.json');
const KEYS_FILE = path.join(__dirname, 'keys.json');
const KEYS_DIR = path.join(__dirname, 'excel-keys');
const ROWS_LIMIT = 20;
const SKIP_BRANDS = ['zaomi', 'mitronium'];
const MIN_SIM = 0.30;
const CHUNK = 150;
const IMG_H = 150;
const IMG_W = 113; // пропорция под фото WB (246x328)
const MAX_CHEAPER = 0.30; // конкурент дешевле нашей цены после СПП более чем на 30% — считаем не той моделью
const PRICE_TOL = 0.05;      // конкурент дешевле нас не более чем на 5% — считаем это нормой
const CLR_OK = '#d9ead3';    // в пределах допуска (или дороже нас) — бледно-зеленый
const CLR_BAD = '#f4cccc';   // подрезает нас более чем на 5% — бледно-красный

// Рейтинг красим ДРУГОЙ парой цветов, чем цену: одинаковые зелёный с красным
// по всей таблице сливаются, и непонятно, про цену эта клетка или про рейтинг.
const CLR_RATE_OK = '#e7f2d3', CLR_RATE_OK_F = '#44631a';   // не выше нашего
const CLR_RATE_BAD = '#fbe1c8', CLR_RATE_BAD_F = '#8e4310'; // выше нашего
// ===============================================

const LAT = { a:'а', e:'е', o:'о', p:'р', c:'с', y:'у', x:'х', k:'к', m:'м', t:'т', h:'н', b:'в' };
function norm(s) {
  let t = String(s || '').toLowerCase().replace(/ё/g, 'е');
  t = t.replace(/[a-z]/g, (ch, i) => {
    const cyr = c => c && /[а-я]/.test(c);
    return (cyr(t[i-1]) || cyr(t[i+1])) && LAT[ch] ? LAT[ch] : ch;
  });
  return t.replace(/[^a-zа-я0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
}

const FAMILIES = [
  { key: 'mi band',      re: /mi\s*band|xiaomi\s*band|smart\s*band|ми\s*бенд/ },
  { key: 'redmi watch',  re: /redmi\s*watch|поко\s*watch/ },
  { key: 'apple watch',  re: /apple\s*watch|iwatch/ },
  { key: 'galaxy fit',   re: /galaxy\s*fit/ },
  { key: 'galaxy watch', re: /galaxy\s*watch/ },
  { key: 'huawei fit',   re: /(huawei|хуавей).*fit|watch\s*fit/ },
  { key: 'huawei band',  re: /(huawei|хуавей).*band|бенд/ },
  { key: 'amazfit',      re: /amazfit/ },
  { key: 'garmin',       re: /garmin/ },
];

const MATERIALS = [
  { key: 'металл',  re: /металлическ|металл|миланск|милан\s*петл|блочн|стальн|нержавею|сталь|магнитн/ },
  { key: 'силикон', re: /силиконов|силикон|резинов|спортивн/ },
  { key: 'ткань',   re: /нейлонов|нейлон|тканев|тканн|плетен|текстиль|тканый|из\s*ткани/ },
  { key: 'кожа',    re: /кожан|экокож|кожа/ },
];

function parse(name) {
  const t = norm(name);
  const fams = FAMILIES.filter(f => f.re.test(t)).map(f => f.key);
  const mats = MATERIALS.filter(m => m.re.test(t)).map(m => m.key);
  const nums = new Set();
  const cleaned = t.replace(/\d+\s*мм/g, ' ').replace(/\d+\s*mm/g, ' ');
  for (const m of cleaned.matchAll(/\b(\d{1,2})\b/g)) {
    const n = parseInt(m[1]);
    if (n >= 1 && n <= 12) nums.add(n);
  }
  return { fams, mats, nums, pro: /\bpro\b/.test(t) };
}

const STOP = new Set(['для','и','в','на','с','из','к','по','а','the','watch','часов','часы',
  'мм','смарт','умных','умные','ремешок','браслет','ремешки','мотивам']);
const words = t => new Set(norm(t).split(' ').filter(w => w.length > 2 && !STOP.has(w)));

function similarity(a, b) {
  const A = words(a), B = words(b);
  if (!A.size) return 1;
  let common = 0;
  for (const w of A) if (B.has(w)) common++;
  return common / A.size;
}

function keep(ourName, compName) {
  const a = parse(ourName), b = parse(compName);
  if (a.mats.length && b.mats.length) {
    if (!b.mats.some(m => a.mats.includes(m))) return false;
  }
  if (a.fams.length) {
    if (!b.fams.some(f => a.fams.includes(f))) return false;
    if (a.pro !== b.pro) return false;
    if (!a.nums.size || !b.nums.size) return true;
    for (const n of a.nums) if (b.nums.has(n)) return true;
    return false;
  }
  return similarity(ourName, compName) >= MIN_SIM;
}

const COLOR_FAMILIES = [
  { key: 'черный',       re: /черн/ },
  { key: 'белый',        re: /бел[ыо]/ },
  { key: 'серый',        re: /сер[ыо]|графит/ },
  { key: 'серебристый',  re: /серебр/ },
  { key: 'золотистый',   re: /золот|шампан/ },
  { key: 'медный',       re: /медн|медь/ },
  { key: 'перламутровый',re: /перламутр/ },
  { key: 'красный',      re: /красн|алый|вишнев|бордов/ },
  { key: 'розовый',      re: /розов|пудров|фуксия|малинов/ },
  { key: 'оранжевый',    re: /оранжев|персиков/ },
  { key: 'желтый',       re: /желт/ },
  { key: 'зеленый',      re: /зелен|изумрудн|мятн|салатов|оливков|болотн|хаки/ },
  { key: 'синий',        re: /син|голуб|индиго|бирюзов/ },
  { key: 'фиолетовый',   re: /фиолетов|сиренев|лавандов/ },
  { key: 'коричневый',   re: /коричнев|беж|безе/ },
];

function colorFamilies(s) {
  const t = String(s || '').toLowerCase();
  return COLOR_FAMILIES.filter(f => f.re.test(t)).map(f => f.key);
}

// если цвет неизвестен хотя бы у одной из сторон — не отсеиваем (нет данных для сравнения)
function colorMatch(ourColor, compColor) {
  const a = colorFamilies(ourColor), b = colorFamilies(compColor);
  if (!a.length || !b.length) return true;
  return a.some(f => b.includes(f));
}

function parsePrice(v) {
  const n = parseFloat(String(v || '').replace(/\s/g, '').replace(',', '.'));
  return Number.isFinite(n) ? n : null;
}

// конкурент дешевле нашей цены после СПП больше чем на MAX_CHEAPER — не та модель
function priceOk(ourPrice, compPrice) {
  if (ourPrice == null || compPrice == null) return true;
  return compPrice >= ourPrice * (1 - MAX_CHEAPER);
}

const load = f => { try { return JSON.parse(fs.readFileSync(f, 'utf-8')); } catch { return null; } };
const cache = load(CACHE_FILE) || {};
const colors = load(COLOR_FILE) || {};

// выдача по ключевым фразам (keywords.js): артикул нашего товара -> файл выгрузки
const keyFileByArt = {};
(load(KEYS_FILE) || []).forEach(k => k.arts.forEach(a => { keyFileByArt[String(a)] = k.file; }));

const readRows = file => {
  if (!fs.existsSync(file)) return null;
  const wb = XLSX.read(fs.readFileSync(file));
  return XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, defval: '' });
};

// Рейтинги. ОБЯЗАТЕЛЬНО числом, а не строкой: строку «4.8» Google Таблицы
// распознают как ДАТУ (4 августа) и кладут в ячейку ~46238. Внешне в колонке
// «Рейтинг» остаётся 4.8, но любое сравнение с рейтингом конкурента врёт —
// на этом 01.08.2026 сломалась подсветка: все конкуренты считались слабее нас.
const rate = v => {
  const n = Number(String(v == null ? '' : v).replace(',', '.').trim());
  return Number.isFinite(n) && n > 0 ? n : '';
};

// рейтинги наших товаров из кабинета
const myRating = {};
const goods = load(GOODS_FILE);
if (Array.isArray(goods)) goods.forEach(g => { if (g.id && g.rating) myRating[g.id] = g.rating; });

// в этой таблице формулы используют ";" как разделитель аргументов (не ",")
const imgFormula = url => (url ? `=IMAGE("${url}";4;${IMG_H};${IMG_W})` : '');

async function toSheet(payload, tries = 4) {
  for (let t = 1; t <= tries; t++) {
    try {
      const r = await fetch(SHEET_URL, {
        method: 'POST',
        body: JSON.stringify(Object.assign({ sheet: SHEET_NAME }, payload)),
        signal: AbortSignal.timeout(120000),
      });
      if (r.ok) return;
      throw new Error('код ' + r.status);
    } catch (e) {
      if (t === tries) throw e;
      console.log(`   попытка ${t} не удалась (${e.message}), повторяю...`);
      await new Promise(res => setTimeout(res, 3000 * t));
    }
  }
}

(async () => {
  const raw = fs.readFileSync(CSV_FILE, 'utf-8').replace(/^\uFEFF/, '');
  const table = raw.split(/\r?\n/).filter(l => l.trim()).map(l => l.split(';'));
  const ours = table.slice(1).filter(r => /^\d{6,12}$/.test(r[0]));
  const ourIds = new Set(ours.map(r => String(r[0])));

  console.log('Наших товаров:', ours.length, '| рейтингов из кабинета:', Object.keys(myRating).length);

  const isOurBrand = b =>
    SKIP_BRANDS.includes(String(b || '').trim().toLowerCase());

  const header = [
    'Фото', 'Артикул продавца', 'Артикул WB', 'Бренд', 'Название',
    'Цена', 'СПП %', 'Цена после СПП', 'Рейтинг', 'Цвет',
  ];

  const out = [header];
  const groups = [];
  const paint = [];
  let noFile = 0, skipBrand = 0, skipName = 0, skipColor = 0, skipPrice = 0;
  let skipDup = 0, fromKeys = 0, noKeyFile = 0, noColorMatch = 0, noPriceMatch = 0;
  let noPhoto = 0, noColor = 0;

  // node compare.js --why — разбор без записи: по каждому нашему товару видно,
  // сколько конкурентов нашлось и какой фильтр их снял. Нужен, чтобы понимать,
  // почему товар вообще не попал в «Сравнение».
  const WHY = process.argv.includes('--why');
  const why = [];

  for (const r of ours) {
    const art = String(r[0]);
    const rows = readRows(path.join(EXCEL_DIR, `${art}.xlsx`));
    if (!rows) {
      noFile++;
      if (WHY) why.push({ art, seller: r[1], name: r[3], reason: 'нет файла evirma', drop: {} });
      continue;
    }
    const dropBefore = { brand: skipBrand, name: skipName, color: skipColor, price: skipPrice, dup: skipDup };

    const ourColor = colors[art] || '';
    const ourPrice = parsePrice(r[8]);
    const comps = [];
    const seen = new Set(); // артикулы, уже попавшие в эту группу — не дублируем

    // ignoreColor — запасной проход: см. ниже, зачем он нужен
    const collect = (src, ignoreColor, ignorePrice) => {
      for (const e of src.slice(1, 1 + ROWS_LIMIT)) {
        const compId = String(e[0] || '');
        if (!compId || seen.has(compId)) { skipDup++; continue; }
        if (isOurBrand(e[1]) || ourIds.has(compId)) { skipBrand++; continue; }
        if (!keep(r[3], e[2])) { skipName++; continue; }
        if (!ignoreColor && !colorMatch(ourColor, colors[compId])) { skipColor++; continue; }
        if (!ignorePrice && !priceOk(ourPrice, parsePrice(e[8]))) { skipPrice++; continue; }
        seen.add(compId);
        comps.push(e);
      }
    };

    collect(rows);

    // добираем выдачу по ключевой фразе (keywords.js), без повторов уже найденных
    const keyFile = keyFileByArt[art];
    if (keyFile) {
      const keyRows = readRows(path.join(KEYS_DIR, keyFile));
      if (keyRows) {
        const before = comps.length;
        collect(keyRows);
        fromKeys += comps.length - before;
      } else noKeyFile++;
    }

    // Запасной проход БЕЗ фильтра по цвету. У редких цветов (медь, графит,
    // перламутр, лавандовый) конкурентов того же цвета в выдаче просто нет, и
    // группа оставалась пустой — 16 товаров из 121 вообще не попадали в лист
    // (04.08.2026). Цена от цвета не зависит, поэтому лучше показать ту же
    // модель другого цвета, чем не показать ничего.
    const keyRowsAgain = keyFile ? readRows(path.join(KEYS_DIR, keyFile)) : null;
    if (!comps.length) {
      collect(rows, true);
      if (keyRowsAgain) collect(keyRowsAgain, true);
      if (comps.length) noColorMatch++;
    }

    // Последняя попытка: снимаем ещё и фильтр «дешевле нас больше чем на 30 %».
    // Он отсекает не ту модель, но у товаров с высокой ценой (blok-redmi-w-3 —
    // 1 210 ₽ после СПП) под него попадает вся выдача, и группа пустеет.
    // Модель по-прежнему проверяется по названию, так что чужое сюда не влезет.
    if (!comps.length) {
      collect(rows, true, true);
      if (keyRowsAgain) collect(keyRowsAgain, true, true);
      if (comps.length) noPriceMatch++;
    }

    if (WHY) {
      why.push({
        art, seller: r[1], name: r[3], found: comps.length,
        reason: comps.length ? '' : 'все конкуренты отсеяны',
        drop: {
          'бренд/свой': skipBrand - dropBefore.brand,
          'название': skipName - dropBefore.name,
          'цвет': skipColor - dropBefore.color,
          'цена': skipPrice - dropBefore.price,
          'дубль': skipDup - dropBefore.dup,
        },
      });
    }

    if (!comps.length) continue;

    out.push([
      imgFormula(cache[parseInt(art, 10)] || ''),
      r[1], r[0], r[2], r[3], r[6], r[7], r[8],
      rate(myRating[art]),
      colors[art] || '',
    ]);
    const headerRow = out.length;

    for (const e of comps) {
      const cid = String(e[0]);
      if (!cache[parseInt(cid, 10)]) noPhoto++;
      if (!colors[cid]) noColor++;
      out.push([
        '',
        imgFormula(cache[parseInt(cid, 10)] || ''),
        e[0], e[1], e[2], '', '', e[8], rate(e[11]),
        colors[cid] || '',
      ]);

      // дешевле нас более чем на 5% — красный, иначе зеленый (красим только цену в колонке H)
      const compPrice = parsePrice(e[8]);
      if (ourPrice != null && compPrice != null) {
        const ok = compPrice >= ourPrice * (1 - PRICE_TOL);
        paint.push({ row: out.length, color: ok ? CLR_OK : CLR_BAD });
      }

      // Рейтинг (колонка I): у конкурента не выше нашего — травяной, выше —
      // янтарный. Красим здесь, а не условным форматированием: правило должно
      // сравнивать со СВОЕЙ группой, а формулы «взять нашу строку выше»
      // на этом листе врут (см. pricing.js — из-за такой же идиомы были
      // неверно посчитаны цены конкурентов).
      const ourRate = rate(myRating[art]), compRate = rate(e[11]);
      if (ourRate !== '' && compRate !== '') {
        const good = compRate <= ourRate;
        paint.push({
          row: out.length, col: 9,
          color: good ? CLR_RATE_OK : CLR_RATE_BAD,
          font: good ? CLR_RATE_OK_F : CLR_RATE_BAD_F,
        });
      }
    }

    groups.push({ from: headerRow, count: comps.length });
  }

  console.log('Всего строк:', out.length - 1, '| групп:', groups.length);
  console.log('Отсеяно по бренду/артикулу:', skipBrand);
  console.log('Отсеяно по названию:', skipName);
  console.log('Отсеяно по цвету:', skipColor);
  console.log('Отсеяно по цене (дешевле нашей > 30%):', skipPrice);
  console.log('Отсеяно как дубли артикулов:', skipDup);
  console.log('Добавлено из выдачи по ключевым фразам:', fromKeys);
  console.log('Групп, собранных без совпадения по цвету:', noColorMatch);
  console.log('Групп, собранных ещё и без фильтра по цене:', noPriceMatch);
  console.log('Строк конкурентов без фото:', noPhoto, '| без цвета:', noColor);
  if (noFile) console.log('Без evirma-файла:', noFile);
  if (noKeyFile) console.log('Без файла по ключевой фразе:', noKeyFile);

  if (WHY) {
    const lost = why.filter(w => w.reason);
    console.log(`\nНЕ попали в «Сравнение»: ${lost.length} из ${ours.length}\n`);
    for (const w of lost) {
      const d = Object.entries(w.drop).filter(([, v]) => v > 0)
        .map(([k, v]) => `${k}: ${v}`).join(', ');
      console.log(`${String(w.seller).padEnd(38)} ${w.art}  — ${w.reason}${d ? ' (' + d + ')' : ''}`);
      console.log(`   ${w.name}`);
    }
    process.exit(0);
  }

  console.log('Отправляю данные...');
  await toSheet({ rows: out.slice(0, CHUNK), clear: true });
  for (let i = CHUNK; i < out.length; i += CHUNK) {
    await toSheet({ rows: out.slice(i, i + CHUNK), clear: false });
    console.log('   строк', Math.min(i + CHUNK, out.length), 'из', out.length);
  }

  console.log('Подсвечиваю цены конкурентов...');
  for (let i = 0; i < paint.length; i += 200) {
    await toSheet({ rows: [], clear: false, paint: paint.slice(i, i + 200) });
    console.log('   строк', Math.min(i + 200, paint.length), 'из', paint.length);
  }

  console.log('Ставлю группировку...');
  for (let i = 0; i < groups.length; i += 15) {
    await toSheet({ rows: [], clear: false, groups: groups.slice(i, i + 15) });
    console.log('   групп', Math.min(i + 15, groups.length), 'из', groups.length);
  }

  // Флажок «Применить» у каждой строки конкурента: одним кликом отмечается
  // цена, которую надо перенести в шаблон (см. apply-prices.js). Лист при
  // каждом прогоне пересоздаётся, поэтому флажки надо ставить заново — иначе
  // после первой же пересборки отмечать станет нечем.
  console.log('Ставлю флажки «Применить»...');
  await toSheet({ rows: [['Применить']], at: 1, col: 26, clear: false });
  const marks = groups.filter(g => g.count > 0)
    .map(g => `Z${g.from + 1}:Z${g.from + g.count}`);
  for (let i = 0; i < marks.length; i += 40) {
    await toSheet({ rows: [], clear: false, checkbox: { ranges: marks.slice(i, i + 40) } });
    console.log('   групп', Math.min(i + 40, marks.length), 'из', marks.length);
  }

  console.log('Сворачиваю...');
  await toSheet({ rows: [], clear: false, collapse: true });

  console.log('Выставляю размеры строк/колонок...');
  await toSheet({ rows: [], clear: false, format: true });

  // Лист пересоздаётся при каждом прогоне (clear: true), вместе с ним слетает
  // оформление книги — возвращаем его сразу. body не трогаем: в колонке H живёт
  // подсветка цен конкурентов, её нельзя перекрывать чередованием строк.
  console.log('Возвращаю оформление...');
  await fetch(SHEET_URL, {
    method: 'POST',
    body: JSON.stringify({ style: { sheets: [{ name: 'Сравнение', body: false, freezeCols: 3 }] } }),
  });

  console.log('Готово!');
  process.exit(0);
})();