const { chromium } = require('playwright');
const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

const CACHE_FILE = path.join(__dirname, 'photo-cache.json');
const BACKUP_FILE = path.join(__dirname, 'photo-cache.backup.json');
const COLOR_FILE = path.join(__dirname, 'color-cache.json');
const COLOR_BACKUP = path.join(__dirname, 'color-cache.backup.json');
const CSV_FILE = path.join(__dirname, 'spp8.csv');
const EXCEL_DIR = path.join(__dirname, 'excel');
const KEYS_DIR = path.join(__dirname, 'excel-keys');
const ROWS_LIMIT = 20;

let cache = {};
if (fs.existsSync(CACHE_FILE)) {
  try {
    cache = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf-8'));
    fs.copyFileSync(CACHE_FILE, BACKUP_FILE);
  } catch {
    if (fs.existsSync(BACKUP_FILE)) cache = JSON.parse(fs.readFileSync(BACKUP_FILE, 'utf-8'));
  }
}
// цвета: тот же кэш, что заполняет colors.js по таблице mkeeper.
// здесь только дозаполняем пустые — уже собранные значения не трогаем
let colors = {};
if (fs.existsSync(COLOR_FILE)) {
  try {
    colors = JSON.parse(fs.readFileSync(COLOR_FILE, 'utf-8'));
    fs.copyFileSync(COLOR_FILE, COLOR_BACKUP);
  } catch {
    if (fs.existsSync(COLOR_BACKUP)) colors = JSON.parse(fs.readFileSync(COLOR_BACKUP, 'utf-8'));
  }
}

const saveCache = () => {
  fs.writeFileSync(CACHE_FILE, JSON.stringify(cache));
  fs.writeFileSync(COLOR_FILE, JSON.stringify(colors));
};

(async () => {
  const raw = fs.readFileSync(CSV_FILE, 'utf-8').replace(/^\uFEFF/, '');
  const table = raw.split(/\r?\n/).filter(l => l.trim()).map(l => l.split(';'));
  const ours = table.slice(1).filter(r => /^\d{6,12}$/.test(r[0]));

  const addFrom = (file, set) => {
    if (!fs.existsSync(file)) return;
    const wb = XLSX.read(fs.readFileSync(file));
    const rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, defval: '' });
    for (const e of rows.slice(1, 1 + ROWS_LIMIT)) if (e[0]) set.add(String(e[0]));
  };

  const all = new Set();
  for (const r of ours) {
    const art = String(r[0]);
    all.add(art);
    addFrom(path.join(EXCEL_DIR, `${art}.xlsx`), all);
  }

  // конкуренты из выдачи по ключевым фразам (keywords.js)
  if (fs.existsSync(KEYS_DIR)) {
    for (const f of fs.readdirSync(KEYS_DIR).filter(n => n.endsWith('.xlsx'))) {
      addFrom(path.join(KEYS_DIR, f), all);
    }
  }

  const arr = [...all];
  const needPhoto = a => !cache[parseInt(a, 10)];
  const needColor = a => !colors[a];              // undefined или пустая строка
  const missing = arr.filter(a => needPhoto(a) || needColor(a));

  console.log('Всего артикулов:', arr.length);
  console.log('Фото уже в кэше:', arr.length - arr.filter(needPhoto).length, '(не перезаписываются)');
  console.log('Цвет уже в кэше:', arr.length - arr.filter(needColor).length, '(не перезаписывается)');
  console.log('Нужно открыть карточек:', missing.length);
  if (!missing.length) { console.log('Всё на месте.'); process.exit(0); }

  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const page = await browser.contexts()[0].newPage();

  // цвет берём из card.json, который страница грузит сама — это значение продавца
  // (внутренний API отдаёт нормализованный цвет WB, он не бьётся с данными mkeeper)
  let colorHit = null;
  page.on('response', async r => {
    if (!/\/info\/ru\/card\.json$/.test(r.url())) return;
    try {
      const j = await r.json();
      const opt = (j.options || []).find(o => /^цвет$/i.test((o.name || '').trim()));
      if (opt && opt.value) colorHit = String(opt.value).trim();
    } catch {}
  });

  let foundPhoto = 0, foundColor = 0;
  for (let i = 0; i < missing.length; i++) {
    const art = missing[i];
    colorHit = null;
    try {
      await page.goto(`https://www.wildberries.ru/catalog/${art}/detail.aspx`,
                      { waitUntil: 'domcontentloaded', timeout: 30000 });

      // ждём, пока появится картинка товара
      await page.waitForFunction(() =>
        [...document.querySelectorAll('img')].some(x =>
          x.src && (x.src.includes('wbbasket') || x.src.includes('geobasket')) && x.src.includes('/images/')),
        { timeout: 15000 }).catch(() => {});

      const src = await page.evaluate(() => {
        const i = [...document.querySelectorAll('img')]
          .map(x => x.src)
          .find(s => s && (s.includes('wbbasket') || s.includes('geobasket')) && s.includes('/images/'));
        return i || null;
      });

      if (src && needPhoto(art)) { cache[parseInt(art, 10)] = src; foundPhoto++; }

      // card.json может прийти позже картинки
      if (!colorHit) await page.waitForTimeout(2000);
      if (needColor(art)) {
        if (colorHit) { colors[art] = colorHit; foundColor++; }
        else if (colors[art] === undefined) colors[art] = ''; // помечаем, чтобы не долбиться каждый раз
      }
    } catch {}
    if (i % 10 === 0) saveCache();
    process.stdout.write(`   ${i + 1}/${missing.length}  фото ${foundPhoto}, цвет ${foundColor}\r`);
  }
  saveCache();
  console.log('\nГотово. Добавлено фото:', foundPhoto, '| цветов:', foundColor);
  process.exit(0);
})();