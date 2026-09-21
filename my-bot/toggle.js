const { chromium } = require('playwright');

async function run() {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0];
  const page = context.pages().find(p => p.url().includes('discount-and-prices'))
            || context.pages()[0];

  await page.bringToFront();
  console.log('Вкладка:', page.url());

  const SEL = '[data-testid="switchers-with-leftover-test-id-switch"]';
  const label = page.locator(SEL).first();
  await label.waitFor({ state: 'visible', timeout: 20000 });

  const isOn = () => page.locator(SEL + ' input').isChecked();

  if (await isOn()) {
    console.log('Фильтр "С остатками" уже включён');
  } else {
    console.log('Включаю фильтр "С остатками"...');
    await label.click();
    await page.waitForTimeout(1000);

    if (!(await isOn())) {
      console.log('Не сработало, пробую кликнуть по input...');
      await page.locator(SEL + ' input').click({ force: true });
      await page.waitForTimeout(1000);
    }

    if (await isOn()) {
      console.log('Включён. Жду перестроения таблицы...');
    } else {
      console.log('ВНИМАНИЕ: включить не удалось, включите вручную');
      process.exit(1);
    }
  }

  // ждём, пока таблица перестанет меняться
  const height = () => page.evaluate(() => {
    const h = document.querySelector('div.ant-table-tbody-virtual-holder');
    return h ? h.scrollHeight : 0;
  });

  let prev = -1, stable = 0;
  for (let i = 0; i < 20; i++) {
    await page.waitForTimeout(1000);
    const h = await height();
    if (h === prev && h > 0) {
      if (++stable >= 3) break;
    } else {
      stable = 0;
    }
    prev = h;
  }
  console.log('Таблица готова, высота:', prev);
}

run().then(() => process.exit(0)).catch(e => {
  console.error('Ошибка:', e.message.split('\n')[0]);
  process.exit(1);
});