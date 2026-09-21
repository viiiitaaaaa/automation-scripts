const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const context = await chromium.launchPersistentContext(
    path.join(__dirname, 'profile'),
    {
      channel: 'chrome',
      headless: false,
      viewport: null,
      ignoreDefaultArgs: ['--enable-automation'],
      args: ['--disable-blink-features=AutomationControlled']
    }
  );
  const page = await context.newPage();
  await page.goto('https://seller.wildberries.ru/');
  await page.pause();
})();