const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0];
  const page = context.pages().find(p => p.url().includes('discount-and-prices')) || context.pages()[0];

  const info = await page.evaluate(() => {
    const labels = [...document.querySelectorAll('label')];
    const t = labels.find(l => (l.innerText || '').includes('С остатками'));
    if (!t) return { error: 'не найден' };
    const inp = t.querySelector('input');
    return {
      html: t.outerHTML.slice(0, 500),
      inputChecked: inp ? inp.checked : 'input отсутствует',
      classes: t.className,
    };
  });

  console.log(JSON.stringify(info, null, 2));
  process.exit(0);
})();