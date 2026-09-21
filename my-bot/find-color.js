const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0];
  const page = context.pages().find(p => p.url().includes('/catalog/')) || context.pages()[0];
  await page.bringToFront();
  console.log('Вкладка:', page.url(), '\n');

  const res = await page.evaluate(() => {
    const out = { colorHeaders: [], colorCells: [], tables: [] };

    // 1. элементы с текстом ровно "Цвет"
    document.querySelectorAll('*').forEach(el => {
      if (el.children.length) return;
      const t = (el.innerText || '').trim();
      if (t === 'Цвет') {
        let p = el, path = [];
        for (let i = 0; i < 6 && p; i++) {
          path.push(p.tagName.toLowerCase() + (p.className ? '.' + String(p.className).split(' ')[0] : ''));
          p = p.parentElement;
        }
        out.colorHeaders.push(path.join(' < '));
      }
      if (['черный','серый','коричневый','бежевый','голубой'].includes(t.toLowerCase())) {
        if (out.colorCells.length < 5) {
          out.colorCells.push({
            text: t,
            tag: el.tagName.toLowerCase(),
            cls: String(el.className).slice(0, 40),
            parentCls: String(el.parentElement?.className || '').slice(0, 40),
          });
        }
      }
    });

    // 2. все таблицы на странице
    document.querySelectorAll('table, [role="table"], [class*="table" i], [class*="grid" i]').forEach(t => {
      const cls = String(t.className).slice(0, 45);
      const rows = t.querySelectorAll('tr, [role="row"], [class*="row" i]').length;
      if (rows > 3 && out.tables.length < 12) {
        out.tables.push({ tag: t.tagName.toLowerCase(), cls, rows });
      }
    });

    return out;
  });

  console.log('Заголовков "Цвет":', res.colorHeaders.length);
  res.colorHeaders.forEach(h => console.log('   ', h));

  console.log('\nЯчеек с названием цвета:', res.colorCells.length);
  res.colorCells.forEach(c => console.log(`    "${c.text}" <${c.tag}> class=${c.cls} | родитель=${c.parentCls}`));

  console.log('\nТаблицы на странице:');
  res.tables.forEach(t => console.log(`   <${t.tag}> строк ${t.rows}  class=${t.cls}`));

  process.exit(0);
})();