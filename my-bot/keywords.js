const { chromium } = require('playwright');
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

// ================== НАСТРОЙКИ ==================
const CSV_FILE = path.join(__dirname, 'spp8.csv');
const OUT_DIR = path.join(__dirname, 'excel-keys');
const KEYS_FILE = path.join(__dirname, 'keys.json');
const PAUSE_MS = 4000;
const SKIP_DONE = true;
const LIMIT = parseInt(process.argv[2] || '0', 10); // для теста: node keywords.js 2
// ===============================================

// материал и свойства выкидываем из названия — ищем по «голому» ключу
// \w в JS не покрывает кириллицу — окончания перечисляем через [а-яё]
const MILAN = /миланск[а-яё]*\s*петл[а-яё]*/gi;
const MATERIALS =
  /(металлическ[а-яё]*|металл[а-яё]*|силиконов[а-яё]*|силикон|тканев[а-яё]*|тканн[а-яё]*|тканы[а-яё]*|нейлонов[а-яё]*|нейлон|кожан[а-яё]*|экокож[а-яё]*|магнитн[а-яё]*|блочн[а-яё]*|стальн[а-яё]*|нержавеющ[а-яё]*|плетен[а-яё]*|плетён[а-яё]*|резинов[а-яё]*|спортивн[а-яё]*|миланск[а-яё]*)/gi;

// в названиях встречается латиница вместо кириллицы («Cиликоновый» через латинскую C).
// меняем латинскую букву на кириллическую только если рядом стоит кириллица — бренды не трогаем
const LAT = { a:'а', e:'е', o:'о', p:'р', c:'с', y:'у', x:'х', k:'к', m:'м', t:'т', h:'н', b:'в',
              A:'А', E:'Е', O:'О', P:'Р', C:'С', Y:'У', X:'Х', K:'К', M:'М', T:'Т', H:'Н', B:'В' };
function fixLatin(s) {
  const cyr = c => c && /[а-яёА-ЯЁ]/.test(c);
  return s.replace(/[a-zA-Z]/g, (ch, i) =>
    (cyr(s[i - 1]) || cyr(s[i + 1])) && LAT[ch] ? LAT[ch] : ch);
}

function keyPhrase(name) {
  const s = fixLatin(String(name || '').trim());
  // товары не про ремешки (например ароматизатор) оставляем как есть
  if (!/ремеш|браслет/i.test(s)) return s;
  return s
    .replace(MILAN, ' ')
    .replace(MATERIALS, ' ')
    .replace(/\s*,\s*/g, ', ')
    .replace(/\s+/g, ' ')
    .replace(/^[\s,]+|[\s,]+$/g, '')
    .trim();
}

const slug = phrase =>
  phrase.toLowerCase().replace(/[^a-zа-я0-9]+/gi, '_').replace(/^_+|_+$/g, '').slice(0, 60) +
  '_' + crypto.createHash('md5').update(phrase).digest('hex').slice(0, 6);

(async () => {
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR);

  const raw = fs.readFileSync(CSV_FILE, 'utf-8').replace(/^﻿/, '');
  const table = raw.split(/\r?\n/).filter(l => l.trim()).map(l => l.split(';'));
  const ours = table.slice(1).filter(r => /^\d{6,12}$/.test(r[0]));

  // один ключ может быть у нескольких наших артикулов — качаем по разу
  const keys = new Map();
  for (const r of ours) {
    const phrase = keyPhrase(r[3]);
    if (!phrase) continue;
    if (!keys.has(phrase)) keys.set(phrase, { phrase, file: slug(phrase) + '.xlsx', arts: [] });
    keys.get(phrase).arts.push(r[0]);
  }

  const list = [...keys.values()];
  fs.writeFileSync(KEYS_FILE, JSON.stringify(list, null, 2), 'utf-8');
  console.log('Наших товаров:', ours.length, '| уникальных ключей:', list.length);
  console.log('Список ключей сохранен в keys.json');

  const todo = LIMIT ? list.slice(0, LIMIT) : list;

  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const context = browser.contexts()[0];
  const page = await context.newPage();

  let ok = 0, skipped = 0;
  const failed = [];

  for (const k of todo) {
    const file = path.join(OUT_DIR, k.file);
    if (SKIP_DONE && fs.existsSync(file)) {
      skipped++;
      console.log('SKIP  ', k.phrase);
      continue;
    }

    console.log('ИЩУ   ', k.phrase);
    try {
      await page.goto(
        'https://www.wildberries.ru/catalog/0/search.aspx?search=' + encodeURIComponent(k.phrase),
        { waitUntil: 'domcontentloaded' }
      );
      await page.waitForTimeout(3000);

      const okBtn = page.getByRole('button', { name: 'Окей' });
      if (await okBtn.isVisible().catch(() => false)) await okBtn.click();

      // кнопка живет в блоке Evirma «Реклама на странице»
      const btn = page.getByRole('button', { name: 'Экспорт в Excel' }).first();
      await btn.waitFor({ state: 'visible', timeout: 30000 });
      await page.waitForTimeout(1500);

      const [download] = await Promise.all([
        page.waitForEvent('download', { timeout: 30000 }),
        btn.click(),
      ]);
      await download.saveAs(file);

      ok++;
      console.log('   сохранено:', k.file);
    } catch (e) {
      failed.push(k.phrase);
      console.log('   ОШИБКА:', e.message.split('\n')[0]);
    }

    await page.waitForTimeout(PAUSE_MS);
  }

  console.log('\n==============================');
  console.log('Готово. Скачано:', ok, '| было раньше:', skipped, '| ошибок:', failed.length);
  if (failed.length) console.log('Не получилось:', failed.join(' | '));
  process.exit(0);
})();
