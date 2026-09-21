const { chromium } = require('playwright');
echo (async () => {
echo   const b = await chromium.connectOverCDP('http://127.0.0.1:9222');
echo   const p = b.contexts()[0].pages().find(x => x.url().includes('/catalog/'));
echo   await p.bringToFront();
echo   const r = await p.evaluate(() => {
echo     const g = [...document.querySelectorAll('.ag-root')].find(x => [...x.querySelectorAll('.ag-header-cell')].some(h => h.innerText.trim() === '\u0426\u0432\u0435\u0442'));
echo     if (!g) return { e: 1 };
echo     const f = (sel, cols) => { const m = {}; const c = g.querySelector(sel); if (!c) return m; [...c.querySelectorAll('.ag-row')].forEach(w => { const i = w.getAttribute('row-index'); m[i] = m[i] || {}; [...w.querySelectorAll('.ag-cell')].forEach(d => { const k = d.getAttribute('col-id'); if (cols.includes(k)) m[i][k] = d.innerText.trim(); }); }); return m; };
echo     const L = f('.ag-pinned-left-cols-container', ['id']);
echo     const C = f('.ag-center-cols-container', ['colors','stocks','brand']);
echo     return { o: Object.keys(L).slice(0,12).map(i => Object.assign({idx:i}, L[i], C[i])), lc: Object.keys(L).length, cc: Object.keys(C).length };
echo   });
echo   if (r.e) { console.log('grid not found'); process.exit(1); }
echo   console.log('left rows:', r.lc, 'center rows:', r.cc);
echo   r.o.forEach(x => console.log(JSON.stringify(x)));
echo   process.exit(0);
echo })();
