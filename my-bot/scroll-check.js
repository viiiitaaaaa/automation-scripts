const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0];
  const page = context.pages().find(p => p.url().includes('/catalog/')) || context.pages()[0];
  await page.bringToFront();

  const info = await page.evaluate(() => {
    const grids = [...document.querySelectorAll('.ag-root')];
    const g = grids.find(x =>
      [...x.querySelectorAll('.ag-header-cell')].some(h => h.innerText.trim() === 'Цвет'));
    if (!g) return { error: 'грид не найден' };

    const scrollers = [];
    g.querySelectorAll('*').forEach(el => {
      if (el.scrollWidth > el.clientWidth + 20) {
        scrollers.push({
          cls: String(el.className).slice(0, 70),
          scrollWidth: el.scrollWidth,
          clientWidth: el.clientWidth,
          scrollLeft: el.scrollLeft,
        });
      }
    });

    const firstRow = g.querySelector('.ag-row');
    const ids = firstRow
      ? [...firstRow.querySelectorAll('.ag-cell')].map(c => c.getAttribute('col-id'))
      : [];

    const containers = [...g.querySelectorAll('[class*="cols-container"], [class*="cols-viewport"]')]
      .map(c => String(c.className).slice(0, 60));

    return { scrollers, ids, containers };
  });

  if (info.error) { console.log(info.error); process.exit(1); }

  console.log('Прокручиваемые контейнеры:');
  info.scrollers.forEach(s =>
    console.log(`   ${s.cls}\n      ширина ${s.clientWidth} из ${s.scrollWidth}, сейчас ${s.scrollLeft}`));

  console.log('\nКолонки в первой строке:', info.ids.join(', '));
  console.log('\nКонтейнеры:');
  info.containers.forEach(c => console.log('   ', c));

  process.exit(0);
})();