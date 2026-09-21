const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const context = browser.contexts()[0];

  // ищем вкладку с таблицей цен среди всех открытых
  const pages = context.pages();
  const page = pages.find(p => p.url().includes('discount-and-prices')) || pages[0];
  console.log('Смотрю вкладку:', page.url(), '\n');

  const found = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('input[type="checkbox"], [role="switch"], [class*="switch" i], [class*="toggle" i]').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width === 0 && r.height === 0) return;
      if (r.width > 400 || r.height > 100) return;
      const parent = el.closest('label') || el.parentElement?.parentElement || el.parentElement;
      out.push({
        tag: el.tagName.toLowerCase(),
        cls: (typeof el.className === 'string' ? el.className : '').slice(0, 50),
        checked: el.checked ?? el.getAttribute('aria-checked'),
        text: (parent?.innerText || '').trim().slice(0, 60).replace(/\n/g, ' | '),
      });
    });
    return out;
  });

  console.log('Найдено переключателей:', found.length, '\n');
  found.forEach((f, i) => {
    console.log(`[${i}] <${f.tag}> состояние: ${f.checked}`);
    console.log(`    класс: ${f.cls}`);
    console.log(`    текст рядом: "${f.text}"\n`);
  });

  process.exit(0);
})();