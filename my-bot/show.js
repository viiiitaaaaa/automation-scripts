const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0];
  const pages = context.pages();
  const page = pages.find(p => p.url().includes('wildberries.ru/catalog')) || pages[0];
  await page.bringToFront();
  console.log('Вкладка:', page.url());
  await page.pause();   // откроется Playwright Inspector
})();