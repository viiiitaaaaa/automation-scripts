const { chromium } = require('playwright');
const path = require('path');

const articles = [
  213873739,
];

(async () => {
  const browser = await chromium.connectOverCDP('http://localhost:9222');
  const context = browser.contexts()[0];
  const page = await context.newPage();

  for (const art of articles) {
    console.log('Обрабатываю:', art);

    await page.goto(`https://www.wildberries.ru/catalog/${art}/detail.aspx`);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    const okBtn = page.getByRole('button', { name: 'Окей' });
    if (await okBtn.isVisible().catch(() => false)) {
      await okBtn.click();
    }

    const downloadPromise = page.waitForEvent('download');
    await page.getByRole('button', { name: 'Экспорт в Excel' }).click();
    const download = await downloadPromise;

    await download.saveAs(path.join(__dirname, 'excel', `${art}.xlsx`));
    console.log('   сохранено');

    await page.waitForTimeout(3000);
  }

  console.log('Готово!');
})();