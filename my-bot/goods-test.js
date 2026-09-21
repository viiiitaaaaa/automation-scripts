const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0];
  const page = context.pages().find(p => p.url().includes('card-main')) || context.pages()[0];
  await page.bringToFront();

  const res = await page.evaluate(() => {
    const t = document.querySelector('table');
    const first = t.querySelector('tbody tr');
    if (!first) return { error: 'нет строк' };

    // весь HTML первой строки, обрезанный
    const html = first.outerHTML.slice(0, 2500);

    // все атрибуты строки и её потомков, где встречается длинное число
    const attrs = [];
    const scan = el => {
      [...el.attributes].forEach(a => {
        if (/\d{6,12}/.test(a.value) && a.value.length < 120) {
          attrs.push(`<${el.tagName.toLowerCase()}> ${a.name}="${a.value.slice(0, 80)}"`);
        }
      });
      [...el.children].forEach(scan);
    };
    scan(first);

    return { html, attrs: attrs.slice(0, 15) };
  });

  if (res.error) { console.log(res.error); process.exit(1); }

  console.log('Атрибуты с числами:');
  res.attrs.forEach(a => console.log('   ' + a));
  console.log('\n--- HTML первой строки ---');
  console.log(res.html);

  process.exit(0);
})();