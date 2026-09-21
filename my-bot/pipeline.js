const { chromium } = require('playwright');
const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

// ================== НАСТРОЙКИ ==================
// Раньше «Цены» и «Evirma» лежали в отдельной книге и у каждого листа был свой
// /exec. Теперь всё в одной книге — адрес один, различаются только имена листов.
const { BOOK_URL } = require('./book');

const CSV_FILE = path.join(__dirname, 'spp8.csv');
const ROWS_LIMIT = 20;
const PAUSE_MS = 4000;
// По умолчанию догружаем только недостающие артикулы. С флагом --full
// выгрузка идёт заново и лист «Evirma» сначала очищается: без этого строки
// дописываются к прошлому прогону, и в листе копятся старые цены вперемешку
// со свежими (так там и оказалось 4880 строк вместо 2420).
const SKIP_DONE = !process.argv.includes('--full');
// ===============================================

// Apps Script периодически отдаёт 404 или рвёт соединение просто от нагрузки:
// в прогоне 04.08.2026 так отвалилось 18 артикулов из 121, хотя xlsx у них
// скачался нормально. Поэтому отправка повторяется с нарастающей паузой.
async function toSheet(url, sheet, rows, clear, tries = 4) {
  for (let t = 1; t <= tries; t++) {
    try {
      const r = await fetch(url, {
        method: 'POST',
        body: JSON.stringify({ sheet, rows, clear }),
      });
      if (r.ok) return;
      if (t === tries) throw new Error('Google Sheets ответил: ' + r.status);
    } catch (e) {
      if (t === tries) throw e;
    }
    await new Promise(res => setTimeout(res, 3000 * t));
  }
}

(async () => {
  const raw = fs.readFileSync(CSV_FILE, 'utf-8').replace(/^\uFEFF/, '');
  const lines = raw.split(/\r?\n/).filter(l => l.trim());
  const table = lines.map(l => l.split(';'));

  console.log('Загружаю цены с СПП...');
  await toSheet(BOOK_URL, 'Цены', table, true);
  console.log('   строк:', table.length - 1);

  const articles = table.slice(1).map(r => r[0]).filter(a => /^\d{6,12}$/.test(a));
  console.log('Артикулов:', articles.length);

  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0];
  const page = await context.newPage();

  if (!SKIP_DONE) await toSheet(BOOK_URL, 'Evirma', [], true);
  let headerSent = SKIP_DONE;

  let ok = 0;
  const failed = [];

  for (const art of articles) {
    console.log('Обрабатываю:', art);

    const file = path.join(__dirname, 'excel', `${art}.xlsx`);
    if (SKIP_DONE && fs.existsSync(file)) {
      console.log('   уже есть, пропускаю');
      continue;
    }

    try {
      await page.goto(`https://www.wildberries.ru/catalog/${art}/detail.aspx`);
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(2500);

      const okBtn = page.getByRole('button', { name: 'Окей' });
      if (await okBtn.isVisible().catch(() => false)) await okBtn.click();

      // Блок Evirma на карточке теперь свёрнут по умолчанию, и кнопки
      // «Экспорт в Excel» в DOM просто нет, пока блок не развернут.
      // Без этого клика скрипт падал на таймауте по КАЖДОМУ артикулу.
      await page.evaluate(() => {
        const b = [...document.querySelectorAll('button, a, div[role="button"], span')]
          .find(e => /показать блок/i.test((e.innerText || '').trim()));
        if (b) b.click();
      });
      await page.waitForTimeout(3000);

      // Блок Evirma подгружается неровно: 04.08.2026 при таймауте 20 с падало
      // 9–15 артикулов из 16, а с 45 с те же карточки отдавали файл с первого
      // раза. Ждём дольше — это дешевле, чем повторные прогоны.
      const btn = page.getByRole('button', { name: 'Экспорт в Excel' });
      await btn.waitFor({ state: 'visible', timeout: 45000 });

      const [download] = await Promise.all([
        page.waitForEvent('download', { timeout: 30000 }),
        btn.click(),
      ]);

      await download.saveAs(file);

      const wb = XLSX.read(fs.readFileSync(file));
      const ws = wb.Sheets[wb.SheetNames[0]];
      const all = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' });

      const header = ['Запрошенный артикул', ...all[0]];
      const dataRows = all.slice(1, 1 + ROWS_LIMIT).map(r => [art, ...r]);

      const send = headerSent ? dataRows : [header, ...dataRows];
      headerSent = true;
      await toSheet(BOOK_URL, 'Evirma', send, false);

      ok++;
      console.log('   отправлено строк:', dataRows.length);
    } catch (e) {
      failed.push(art);
      console.log('   ОШИБКА, пропускаю:', e.message.split('\n')[0]);
    }

    await page.waitForTimeout(PAUSE_MS);
  }

  console.log('\n==============================');
  console.log('Готово. Обработано:', ok, '| ошибок:', failed.length);
  if (failed.length) console.log('Не получилось:', failed.join(', '));
  process.exit(0);
})();