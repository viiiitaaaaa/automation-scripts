const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0];
  const page = context.pages().find(p => p.url().includes('/catalog/')) || context.pages()[0];
  await page.bringToFront();

  const res = await page.evaluate(async () => {
    const sleep = ms => new Promise(r => setTimeout(r, ms));

    const grids = [...document.querySelectorAll('.ag-root')];
    const g = grids.find(x =>
      [...x.querySelectorAll('.ag-header-cell')].some(h => h.innerText.trim() === 'Цвет'));
    if (!g) return { error: 'грид не найден' };

    const vp = g.querySelector('.ag-center-cols-viewport');
    if (!vp) return { error: 'viewport не найден' };

    const data = {};

    const collect = () => {
      [...g.querySelectorAll('.ag-row')].forEach(r => {
        const idx = r.getAttribute('row-index');
        if (idx === null) return;
        if (!data[idx]) data[idx] = {};
        [...r.querySelectorAll('.ag-cell')].forEach(c => {
          const col = c.getAttribute('col-id');
          const val = (c.innerText || '').trim();
          if (val && ['id', 'colors', 'stocks', 'nmReviewRating', 'feedbacks'].includes(col)) {
            data[idx][col] = val;
          }
        });
      });
    };

    const step = Math.floor(vp.clientWidth * 0.7);
    for (let x = 0; x <= vp.scrollWidth; x += step) {
      vp.scrollLeft = x;
      vp.dispatchEvent(new Event('scroll', { bubbles: true }));
      await sleep(400);
      collect();
    }
    vp.scrollLeft = 0;

    const rows = Object.values(data).filter(d => d.id).slice(0, 10);
    return { rows, width: vp.scrollWidth, client: vp.clientWidth };
  });

  if (res.error) { console.log(res.error); process.exit(1); }

  console.log('Ширина таблицы ' + res.width + ', видно ' + res.client + '\n');
  res.rows.forEach((r, i) => console.log(i, JSON.stringify(r)));

  process.exit(0);
})();