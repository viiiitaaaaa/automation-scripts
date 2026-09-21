const { chromium } = require('playwright');

(async () => {
  const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const p = b.contexts()[0].pages().find(x => x.url().includes('/catalog/'));
  await p.bringToFront();

  const r = await p.evaluate(() => {
    const g = [...document.querySelectorAll('.ag-root')].find(x =>
      [...x.querySelectorAll('.ag-header-cell')].some(h => h.innerText.trim() === 'Цвет'));
    if (!g) return { e: 1 };

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
    const C = f('.ag-center-cols-container', ['colors', 'stocks', 'brand']);

    return {
      o: Object.keys(L).slice(0, 12).map(i => Object.assign({ idx: i }, L[i], C[i])),
      lc: Object.keys(L).length,
      cc: Object.keys(C).length,
    };
  });

  if (r.e) { console.log('грид не найден'); process.exit(1); }
  console.log('строк слева:', r.lc, '| в центре:', r.cc);
  r.o.forEach(x => console.log(JSON.stringify(x)));
  process.exit(0);
})();