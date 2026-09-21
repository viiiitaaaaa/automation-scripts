const { chromium } = require('playwright');

const URL = 'https://seller.wildberries.ru/suppliers-mutual-settlements/reports-implementations/reports-weekly-new';

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const page = await browser.contexts()[0].newPage();

  await page.goto(URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(10000);

  console.log('=== СПИСОК ОТЧЁТОВ ===');
  let btns = await page.evaluate(() =>
    [...document.querySelectorAll('button, a, [role="button"]')]
      .map(b => (b.innerText || '').trim().replace(/\n/g, ' | '))
      .filter(t => t && t.length < 45)
      .slice(0, 30));
  btns.forEach(b => console.log('   "' + b + '"'));

  // открываем первый отчёт
  const num = await page.evaluate(() => {
    const m = document.body.innerText.match(/\b\d{9}\b/);
    return m ? m[0] : null;
  });
  console.log('\nОткрываю отчёт', num);
  await page.getByText(num, { exact: true }).first().click({ timeout: 15000 }).catch(e =>
    console.log('клик не прошёл:', e.message.split('\n')[0]));
  await page.waitForTimeout(8000);

  console.log('\n=== ВНУТРИ ОТЧЁТА ===');
  console.log('URL:', page.url());
  btns = await page.evaluate(() =>
    [...document.querySelectorAll('button, a, [role="button"]')]
      .map(b => ({
        text: (b.innerText || '').trim().replace(/\n/g, ' | ').slice(0, 40),
        testid: b.getAttribute('data-testid') || '',
      }))
      .filter(x => x.text || x.testid)
      .slice(0, 40));
  btns.forEach(b => console.log(`   "${b.text}"  testid=${b.testid}`));

  process.exit(0);
})();