const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

// ================== НАСТРОЙКИ ==================
const { BOOK_URL: SHEET_URL } = require('./book');   // единая книга, см. book.js
const SHEET_NAME = 'Сравнение';
const CSV_FILE = path.join(__dirname, 'spp8.csv');
const EXCEL_DIR = path.join(__dirname, 'excel');
const CACHE_FILE = path.join(__dirname, 'photo-cache.json');
const ROWS_LIMIT = 20;
const SKIP_BRANDS = ['zaomi', 'mitronium'];
const MAX_HOST = 60;
// ===============================================

let cache = {};
if (fs.existsSync(CACHE_FILE)) {
  try { cache = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf-8')); } catch {}
}
const saveCache = () => fs.writeFileSync(CACHE_FILE, JSON.stringify(cache));

// Примерная догадка о сервере по номеру артикула — чтобы начать перебор рядом
function guessHost(vol) {
  if (vol <= 143) return 1;
  if (vol <= 287) return 2;
  if (vol <= 431) return 3;
  if (vol <= 719) return 4;
  if (vol <= 1007) return 5;
  if (vol <= 1061) return 6;
  if (vol <= 1115) return 7;
  if (vol <= 1169) return 8;
  if (vol <= 1313) return 9;
  if (vol <= 1601) return 10;
  if (vol <= 1655) return 11;
  if (vol <= 1919) return 12;
  if (vol <= 2045) return 13;
  if (vol <= 2189) return 14;
  if (vol <= 2405) return 15;
  if (vol <= 2621) return 16;
  if (vol <= 2837) return 17;
  if (vol <= 3053) return 18;
  if (vol <= 3269) return 19;
  if (vol <= 3485) return 20;
  return Math.min(MAX_HOST, 21 + Math.floor((vol - 3485) / 250));
}

async function findPhoto(art) {
  const id = parseInt(art, 10);
  if (!id) return '';
  if (cache[id] !== undefined) return cache[id];

  const vol = Math.floor(id / 100000);
  const part = Math.floor(id / 1000);

  // порядок проверки: сначала догадка и соседи, потом все остальные
  const start = guessHost(vol);
  const order = [];
  for (let d = 0; d <= MAX_HOST; d++) {
    if (start + d <= MAX_HOST) order.push(start + d);
    if (d > 0 && start - d >= 1) order.push(start - d);
  }

  for (const h of order) {
    const host = String(h).padStart(2, '0');
    const url = `https://basket-${host}.wbbasket.ru/vol${vol}/part${part}/${id}/images/c246x328/1.webp`;
    try {
      const r = await fetch(url, { method: 'HEAD' });
      if (r.ok) { cache[id] = url; return url; }
    } catch {}
  }
  cache[id] = '';
  return '';
}

const imgFormula = url => (url ? `=IMAGE("${url}")` : '');

async function toSheet(rows, clear) {
  const r = await fetch(SHEET_URL, {
    method: 'POST',
    body: JSON.stringify({ sheet: SHEET_NAME, rows, clear }),
  });
  if (!r.ok) throw new Error('Google Sheets ответил: ' + r.status);
}

(async () => {
  const raw = fs.readFileSync(CSV_FILE, 'utf-8').replace(/^\uFEFF/, '');
  const lines = raw.split(/\r?\n/).filter(l => l.trim());
  const table = lines.map(l => l.split(';'));
  const ours = table.slice(1).filter(r => /^\d{6,12}$/.test(r[0]));
  const ourIds = new Set(ours.map(r => String(r[0])));

  console.log('Наших товаров:', ours.length);

  const isOurBrand = b =>
    SKIP_BRANDS.includes(String(b || '').trim().toLowerCase());

  const pairs = [];
  const allArts = new Set();
  let noFile = 0, skipped = 0;

  for (const r of ours) {
    const art = String(r[0]);
    const file = path.join(EXCEL_DIR, `${art}.xlsx`);
    if (!fs.existsSync(file)) { noFile++; continue; }

    const wb = XLSX.read(fs.readFileSync(file));
    const ws = wb.Sheets[wb.SheetNames[0]];
    const all = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' });

    for (const e of all.slice(1, 1 + ROWS_LIMIT)) {
      const compId = String(e[0] || '');
      if (isOurBrand(e[1]) || ourIds.has(compId)) { skipped++; continue; }
      pairs.push({ our: r, comp: e });
      allArts.add(art);
      allArts.add(compId);
    }
  }

  console.log('Строк в итоге:', pairs.length);
  console.log('Отсеяно (наш бренд / наш артикул):', skipped);
  if (noFile) console.log('Без evirma-файла:', noFile, 'артикулов');

  const arts = [...allArts];
  const toFind = arts.filter(a => cache[parseInt(a, 10)] === undefined);
  console.log('Ищу фото:', toFind.length, 'новых из', arts.length);

  for (let i = 0; i < toFind.length; i += 15) {
    await Promise.all(toFind.slice(i, i + 15).map(a => findPhoto(a)));
    process.stdout.write(`   ${Math.min(i + 15, toFind.length)}/${toFind.length}\r`);
    if ((i / 15) % 10 === 0) saveCache();
  }
  saveCache();

  const withPhoto = arts.filter(a => cache[parseInt(a, 10)]).length;
  console.log('\nФото найдено для', withPhoto, 'из', arts.length);

  const header = [
    'Фото', 'Артикул продавца', 'Артикул WB', 'Бренд', 'Название',
    'Цена после скидки', 'СПП %', 'Цена после СПП',
    'Фото конкурента', 'Артикул конкурента', 'Бренд конкурента',
    'Название конкурента', 'Цена конкурента', 'Рейтинг конкурента',
  ];

  const out = [header];
  for (const { our: r, comp: e } of pairs) {
    out.push([
      imgFormula(cache[parseInt(r[0], 10)] || ''),
      r[1], r[0], r[2], r[3],
      r[6], r[7], r[8],
      imgFormula(cache[parseInt(e[0], 10)] || ''),
      e[0], e[1], e[2], e[8], e[11],
    ]);
  }

  console.log('Отправляю в Google Таблицу...');
  await toSheet(out.slice(0, 300), true);
  for (let i = 300; i < out.length; i += 300) {
    await toSheet(out.slice(i, i + 300), false);
    console.log('   отправлено', Math.min(i + 300, out.length), 'из', out.length);
  }

  console.log('Готово!');
  process.exit(0);
})();