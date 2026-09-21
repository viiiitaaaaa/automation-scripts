const { chromium } = require('playwright');
const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

const CSV_FILE = path.join(__dirname, 'spp8.csv');
const EXCEL_DIR = path.join(__dirname, 'excel');
const CACHE_FILE = path.join(__dirname, 'color-cache.json');
const ROWS_LIMIT = 20;

let cache = {};
if (fs.existsSync(CACHE_FILE)) {
  try { cache = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf-8')); } catch {}
}
const saveCache = () => fs.writeFileSync(CACHE_FILE, JSON.stringify(cache));

async function readColors(page) {
  return await page.evaluate(() => {
    const g = [...document.querySelectorAll('.ag-root')].find(x =>
      [...x.querySelectorAll('.ag-header-cell')].some(h => h.innerText.trim() === 'Цвет'));
    if (!g) return null;

    const f = (sel, cols) => {
      const m = {};
      const c = g.querySelector(sel);
      if (!c) return m;
      [...c.querySelectorAll('.ag-row')].forEach(w => {
        const i = w.getAttribute('row-index');
        m[i] = m[i] || {};
        [...w.querySelectorAll('.ag-cell')].forEach(d => {
          const k = d.getAttribute('col-id');
          if (cols.includes(k)) m[i][k] = d.innerText.trim();
        });
      });
      return m;
    };

    const L = f('.ag-pinned-left-cols-container', ['id']);
    const C = f('.ag-center-cols-container', ['colors']);

    const found = {};
    Object.keys(L).forEach(i => {
      if (L[i].id && C[i] && C[i].colors) found[L[i].id] = C[i].colors;
    });
    return found;
  });
}

(async () => {
  const raw = fs.readFileSync(CSV_FILE, 'utf-8').replace(/^\uFEFF/, '');
  const table = raw.split(/\r?\n/).filter(l => l.trim()).map(l => l.split(';'));
  const ours = table.slice(1).filter(r => /^\d{6,12}$/.test(r[0]));

  const need = new Map();
  const all = new Set();
  for (const r of ours) {
    const art = String(r[0]);
    const f = path.join(EXCEL_DIR, `${art}.xlsx`);
    if (!fs.existsSync(f)) continue;
    const wb = XLSX.read(fs.readFileSync(f));
    const rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, defval: '' });
    const ids = [art];
    rows.slice(1, 1 + ROWS_LIMIT).forEach(e => { if (e[0]) ids.push(String(e[0])); });
    ids.forEach(i => all.add(i));
    need.set(art, ids);
  }

  const missing = [...all].filter(a => cache[a] === undefined);
  console.log('Всего артикулов:', all.size, '| в кэше:', all.size - missing.length,
              '| надо найти:', missing.length);
  if (!missing.length) { console.log('Всё уже собрано.'); process.exit(0); }

  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const page = await browser.contexts()[0].newPage();

  let done = 0;
  for (const [art, ids] of need) {
    if (ids.every(i => cache[i] !== undefined)) continue;

    try {
      await page.goto(`https://www.wildberries.ru/catalog/${art}/detail.aspx`, { timeout: 30000 });
      await page.waitForTimeout(6000);

      await page.evaluate(() => {
        const t = [...document.querySelectorAll('[class*="_tabButton_"]')]
          .find(x => x.innerText.trim() === 'Полки');
        if (t) t.click();
      });
      await page.waitForTimeout(5000);

      const found = await readColors(page);
      if (found) {
        let n = 0;
        Object.entries(found).forEach(([id, col]) => {
          if (cache[id] === undefined) n++;
          cache[id] = col;
        });
        ids.forEach(i => { if (cache[i] === undefined) cache[i] = ''; });
        console.log(`${art}: собрано ${Object.keys(found).length}, новых ${n}`);
      } else {
        console.log(`${art}: таблица mkeeper не найдена`);
      }
    } catch (e) {
      console.log(`${art}: ошибка — ${e.message.split('\n')[0]}`);
    }

    if (++done % 5 === 0) saveCache();
    await page.waitForTimeout(1500);
  }

  saveCache();
  const withColor = [...all].filter(a => cache[a]).length;
  console.log(`\nГотово. Цвет известен для ${withColor} из ${all.size}`);
  process.exit(0);
})();