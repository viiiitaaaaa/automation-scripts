const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const CACHE_FILE = path.join(__dirname, 'color-cache.json');

let cache = {};
if (fs.existsSync(CACHE_FILE)) {
  try { cache = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf-8')); } catch {}
}

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0];
  const page = context.pages().find(p => p.url().includes('card-main')) || context.pages()[0];
  await page.bringToFront();
  console.log('Вкладка:', page.url());

  const collected = new Map();
  let idle = 0;

  for (let step = 0; step < 400; step++) {
    const rows = await page.evaluate(() => {
      const t = document.querySelector('table');
      if (!t) return [];
      const out = [];
      [...t.querySelectorAll('tbody tr')].forEach(tr => {
        const img = tr.querySelector('img');
        const src = img ? (img.getAttribute('src') || '') : '';
        const m = src.match(/\/(\d{6,12})\/images\//);
        if (!m) return;
        const td = [...tr.querySelectorAll('td')].map(c => c.innerText.trim());
        out.push({
          id: m[1],
          name: (td[1] || '').split('\n')[0],
          rating: (td[2] || '').split('\n')[0],
          stock: td[3] || '',
          color: td[8] || '',
        });
      });
      return out;
    });

    const before = collected.size;
    rows.forEach(r => collected.set(r.id, r));
    const added = collected.size - before;

    // прокручиваем внутренний контейнер таблицы
    const pos = await page.evaluate(() => {
      const c = document.querySelector('[class*="Table__container__"]');
      if (!c) return null;
      c.scrollTop += c.clientHeight * 0.8;
      c.dispatchEvent(new Event('scroll', { bubbles: true }));
      return { top: Math.round(c.scrollTop), max: c.scrollHeight - c.clientHeight };
    });

    if (!pos) { console.log('\nконтейнер не найден'); break; }

    process.stdout.write(`   товаров ${collected.size} (+${added})  прокрутка ${pos.top}/${pos.max}\r`);

    idle = added === 0 ? idle + 1 : 0;
    if (idle >= 5 && pos.top >= pos.max - 5) break;
    if (idle >= 15) break;

    await page.waitForTimeout(900);
  }

  console.log(`\n\nВсего товаров: ${collected.size}`);

  let added = 0;
  for (const [id, r] of collected) {
    if (r.color && cache[id] !== r.color) { cache[id] = r.color; added++; }
  }
  fs.writeFileSync(CACHE_FILE, JSON.stringify(cache));
  console.log('Цветов записано в кэш:', added);

  const rows = [...collected.values()];
  fs.writeFileSync(path.join(__dirname, 'my-goods.json'), JSON.stringify(rows, null, 1));
  console.log('Полные данные: my-goods.json');

  console.log('\nПримеры:');
  rows.slice(0, 5).forEach(r => console.log('  ', JSON.stringify(r)));

  process.exit(0);
})();