const { chromium } = require('playwright');

const arts = [213900875, 213900882];

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const page = await browser.contexts()[0].newPage();

  for (const art of arts) {
    console.log('\n=== ', art, '===');
    await page.goto(`https://www.wildberries.ru/catalog/${art}/detail.aspx`, { timeout: 30000 });
    await page.waitForTimeout(3000);

    const src = await page.evaluate(() => {
      const img = document.querySelector('.photo-zoom__preview, .slide__content img, img.photo-zoom__preview');
      if (img) return img.src;
      const any = [...document.querySelectorAll('img')]
        .map(i => i.src)
        .find(s => s && s.includes('wbbasket') && s.includes('/images/'));
      return any || null;
    });

    console.log(src || 'фото на странице не найдено');
  }
  process.exit(0);
})();