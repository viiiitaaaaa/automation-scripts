const { chromium } = require('playwright');

const ART = 213873739;

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const page = await browser.contexts()[0].newPage();

  await page.goto(`https://www.wildberries.ru/catalog/${ART}/detail.aspx`);
  await page.waitForTimeout(6000);

  const res = await page.evaluate(() => {
    const grids = document.querySelectorAll('.ag-root-wrapper');
    const out = { grids: grids.length, rows: [] };

    grids.forEach((g, gi) => {
      const rows = g.querySelectorAll('.ag-row, [role="row"]');
      rows.forEach((r, ri) => {
        if (ri > 12) return;
        const cells = [...r.querySelectorAll('.ag-cell, [role="gridcell"]')];
        const first = cells[0];
        const rowBg = getComputedStyle(r).backgroundColor;
        const cellInfo = cells.slice(0, 4).map(c => {
          const st = getComputedStyle(c);
          return {
            v: (c.innerText || '').trim().slice(0, 25),
            bg: st.backgroundColor,
            col: st.color,
          };
        });
        out.rows.push({ grid: gi, rowBg, cls: r.className.slice(0, 60), cells: cellInfo });
      });
    });
    return out;
  });

  console.log('Таблиц найдено:', res.grids, '\n');
  res.rows.forEach(r => {
    console.log(`grid${r.grid} | фон строки: ${r.rowBg}`);
    console.log(`   класс: ${r.cls}`);
    r.cells.forEach(c => {
      console.log(`   "${c.v}"  фон: ${c.bg}  текст: ${c.col}`);
    });
    console.log('');
  });

  process.exit(0);
})();