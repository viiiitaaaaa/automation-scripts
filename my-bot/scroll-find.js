const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0];
  const page = context.pages().find(p => p.url().includes('card-main')) || context.pages()[0];
  await page.bringToFront();

  const res = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('*').forEach(el => {
      if (el.scrollHeight > el.clientHeight + 50 && el.clientHeight > 200) {
        out.push({
          tag: el.tagName.toLowerCase(),
          cls: String(el.className).slice(0, 55),
          testid: el.getAttribute('data-testid') || '',
          scrollH: el.scrollHeight,
          clientH: el.clientHeight,
          top: el.scrollTop,
        });
      }
    });
    return {
      scrollers: out.slice(0, 12),
      windowScroll: { y: window.scrollY, h: document.body.scrollHeight, inner: window.innerHeight },
    };
  });

  console.log('Окно: прокрутка', res.windowScroll.y, 'из', res.windowScroll.h,
              '| видно', res.windowScroll.inner, '\n');
  console.log('Прокручиваемые контейнеры:');
  res.scrollers.forEach(s => {
    console.log(`   <${s.tag}> ${s.cls}`);
    if (s.testid) console.log(`      testid: ${s.testid}`);
    console.log(`      высота ${s.clientH} из ${s.scrollH}, сейчас ${s.top}`);
  });

  process.exit(0);
})();