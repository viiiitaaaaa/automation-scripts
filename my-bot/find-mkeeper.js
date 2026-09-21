const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0];
  const pages = context.pages();
  const page = pages.find(p => p.url().includes('wildberries.ru/catalog')) || pages[0];
  await page.bringToFront();
  console.log('Вкладка:', page.url(), '\n');

  // 1. ищем текст mkeeper и характерные вкладки
  const marks = await page.evaluate(() => {
    const out = [];
    const wanted = ['mkeeper', 'SEO конструктор', 'Гео анализ', 'Мониторинг полок'];
    document.querySelectorAll('*').forEach(el => {
      if (el.children.length > 2) return;
      const t = (el.innerText || '').trim();
      if (wanted.some(w => t.toLowerCase().includes(w.toLowerCase())) && t.length < 60) {
        out.push({ tag: el.tagName.toLowerCase(), text: t.slice(0, 50),
                   cls: String(el.className).slice(0, 50) });
      }
    });
    return out.slice(0, 15);
  });
  console.log('Найдено меток mkeeper в основном документе:', marks.length);
  marks.forEach(m => console.log(`   <${m.tag}> "${m.text}"  class=${m.cls}`));

  // 2. фреймы
  console.log('\nФреймов на странице:', page.frames().length);
  for (const f of page.frames()) {
    const u = f.url();
    if (u && u !== page.url()) console.log('   фрейм:', u.slice(0, 100));
  }

  // 3. shadow DOM
  const shadows = await page.evaluate(() => {
    let n = 0; const hosts = [];
    document.querySelectorAll('*').forEach(el => {
      if (el.shadowRoot) { n++; if (hosts.length < 10) hosts.push(el.tagName.toLowerCase() + '.' + String(el.className).slice(0,30)); }
    });
    return { n, hosts };
  });
  console.log('\nЭлементов с shadow DOM:', shadows.n);
  shadows.hosts.forEach(h => console.log('   ', h));

  process.exit(0);
})();