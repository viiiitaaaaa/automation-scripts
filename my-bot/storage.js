// Выгружает отчёт по платному хранению с детализацией до артикула
// (https://seller.wildberries.ru/analytics-reports/paid-storage/nomenclature-report)
// и сворачивает его по дню и артикулу.
//
// Зачем: в недельном отчёте реализации хранение идёт отдельными строками
// с ПУСТЫМ артикулом, разнести его по SKU оттуда нельзя. Этот отчёт —
// единственный источник хранения в разрезе артикулов.
//
// Порядок работы на сайте (повторяем ровно его):
//   период -> «Создать Excel» -> модалка с именем файла -> «Сформировать»
//   -> ждём статус SUCCESS в списке -> «Скачать» -> клик по размеру файла.
//
// Файл приходит zip-ом, внутри один xlsx (как и у недельных отчётов).
//
// Прямое скачивание по downloadUrl НЕ работает: домен downloads-content-analytics
// отдаёт 403 и на куки, и на токены AuthorizeV3/Wb-Seller-Lk. Поэтому файл
// забирает сам Chrome через Browser.setDownloadBehavior.
//
// Запуск:
//   node storage.js                        — прошлая полная неделя (Пн–Вс)
//   node storage.js 2026-07-20 2026-07-26  — конкретный период
//   node storage.js --local                — только пересобрать свёртку из storage/

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const XLSX = require('xlsx');
const { attach } = require('./cdp-lite');

// ================== НАСТРОЙКИ ==================
const PAGE = 'https://seller.wildberries.ru/analytics-reports/paid-storage/nomenclature-report';
const LIST_API = 'https://seller-content.wildberries.ru/ns/analytics-api/content-analytics/api/v1/file-manager/downloads?report_types=PAID_STORAGE_NM_REPORT';
const DIR = path.join(__dirname, 'storage');
const DAILY = path.join(DIR, 'storage-daily.json');
const SHEET = 'Детальная информация';
const LOCAL = process.argv.includes('--local');
// ===============================================

const iso = d => d.toISOString().slice(0, 10);
const arg = i => (process.argv[i] || '').match(/^\d{4}-\d{2}-\d{2}$/) ? process.argv[i] : null;

// прошлая полная неделя Пн–Вс
function lastWeek() {
  const now = new Date();
  const d = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));
  const shift = (d.getUTCDay() + 6) % 7;                 // Пн=0
  const mon = new Date(d.getTime() - (shift + 7) * 864e5);
  return [iso(mon), iso(new Date(mon.getTime() + 6 * 864e5))];
}

// ярлык недели в том же виде, что и имена вкладок таблицы
function weekLabel(ymd) {
  const [y, m, dd] = ymd.split('-').map(Number);
  const dt = new Date(Date.UTC(y, m - 1, dd));
  const mon = new Date(dt.getTime() - ((dt.getUTCDay() + 6) % 7) * 864e5);
  const sun = new Date(mon.getTime() + 6 * 864e5);
  const ru = x => String(x.getUTCDate()).padStart(2, '0') + '.' +
                  String(x.getUTCMonth() + 1).padStart(2, '0') + '.' + x.getUTCFullYear();
  return `с ${ru(mon)} по ${ru(sun)}`;
}

const [FROM, TO] = arg(2) ? [arg(2), arg(3) || arg(2)] : lastWeek();

function unzip(zipPath, outPath) {
  const ps = [
    'Add-Type -AssemblyName System.IO.Compression.FileSystem;',
    `$z=[System.IO.Compression.ZipFile]::OpenRead('${zipPath}');`,
    `[System.IO.Compression.ZipFileExtensions]::ExtractToFile($z.Entries[0],'${outPath}',$true);`,
    '$z.Dispose()',
  ].join(' ');
  execSync(`powershell -NoProfile -Command "${ps}"`, { stdio: 'pipe' });
}

// ---------- скачивание отчёта с сайта ----------
async function download(from, to) {
  const name = `hranenie ${from}_${to}`;
  const before = new Set(fs.readdirSync(DIR));
  const t = await attach('analytics-reports/paid-storage', PAGE);
  console.log('вкладка:', t.url);

  await t.raw('Browser.setDownloadBehavior', {
    behavior: 'allow', downloadPath: DIR, eventsEnabled: true,
  });
  let dlState = null;
  t.on(m => {
    if (m.method === 'Browser.downloadProgress' && m.params.state !== 'inProgress') {
      dlState = m.params.state;
    }
  });

  const ru = s => s.split('-').reverse().join('.');
  const period = `${ru(from)} - ${ru(to)}`;

  // 1. период. Инпут под управлением React — нужен нативный сеттер + событие input
  const set = await t.evaluate(`(() => {
    const el = document.querySelector('input[type=text]');
    if (!el) return 'инпут периода не найден';
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    el.focus();
    setter.call(el, ${JSON.stringify(period)});
    el.dispatchEvent(new Event('input', { bubbles: true }));
    el.dispatchEvent(new Event('change', { bubbles: true }));
    return el.value;
  })()`);
  if (set !== period) throw new Error(`период не выставился: "${set}" вместо "${period}"`);
  console.log('период выставлен:', period);

  // 2. «Создать Excel» -> модалка -> имя -> «Сформировать»
  await t.evaluate(`(() => {
    const b = [...document.querySelectorAll('button')].find(x => x.innerText.trim() === 'Создать Excel');
    if (b) b.click();
  })()`);
  await new Promise(r => setTimeout(r, 3000));

  const named = await t.evaluate(`(() => {
    const dlg = [...document.querySelectorAll('[role=dialog],[class*=odal]')]
      .find(d => /Название файла/.test(d.innerText || ''));
    if (!dlg) return 'модалка не открылась';
    const inp = dlg.querySelector('input');
    const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    inp.focus();
    setter.call(inp, ${JSON.stringify(name)});
    inp.dispatchEvent(new Event('input', { bubbles: true }));
    inp.dispatchEvent(new Event('change', { bubbles: true }));
    return inp.value;
  })()`);
  if (named !== name) throw new Error('не удалось задать имя файла: ' + named);

  await new Promise(r => setTimeout(r, 1000));
  await t.evaluate(`(() => {
    const b = [...document.querySelectorAll('button')].find(x => x.innerText.trim() === 'Сформировать');
    if (b && !b.disabled) b.click();
  })()`);
  console.log('отчёт заказан:', name);

  // 3. ждём готовности в списке
  let ready = null;
  for (let i = 0; i < 40 && !ready; i++) {
    await new Promise(r => setTimeout(r, 3000));
    const raw = await t.evaluate(`
      fetch(${JSON.stringify(LIST_API)}, { credentials: 'include', headers: {
        'AuthorizeV3': localStorage.getItem('wb-eu-passport-v2.access-token'),
        'Wb-Seller-Lk': localStorage.getItem('wb-eu-portal.seller-token'),
      }}).then(r => r.text())
    `);
    const list = (JSON.parse(raw).data || {}).downloads || [];
    ready = list.find(d => d.name === name && d.status === 'SUCCESS');
    process.stdout.write(`   жду готовности... ${i * 3}с\r`);
  }
  if (!ready) throw new Error('отчёт не сформировался за 2 минуты');
  console.log(`\nготов: ${ready.name}, ${Math.round(ready.size / 1024)} КБ`);

  // 4. «Скачать» -> клик по размеру в строке нашего отчёта.
  // Прямой переход по ready.downloadUrl даёт 403 — качаем именно кликом.
  await t.evaluate(`(() => {
    const b = [...document.querySelectorAll('button')].find(x => x.innerText.trim() === 'Скачать');
    if (b) b.click();
  })()`);
  await new Promise(r => setTimeout(r, 6000));

  const clicked = await t.evaluate(`(() => {
    const sizes = [...document.querySelectorAll('*')].filter(e =>
      /^\\d+([.,]\\d+)?\\s*(КБ|МБ)$/.test((e.innerText || '').trim()) && e.children.length === 0);
    if (!sizes.length) return 'список загрузок пуст';
    const want = ${JSON.stringify(name)};
    const pick = sizes.find(s => {
      let p = s;
      for (let i = 0; i < 6 && p; i++) {
        p = p.parentElement;
        if (p && (p.innerText || '').includes(want)) return true;
      }
      return false;
    });
    if (!pick) return 'строка отчёта не найдена в списке';
    (pick.closest('button,[role=button]') || pick).click();
    return 'ok ' + pick.innerText.trim();
  })()`);
  if (!clicked.startsWith('ok')) throw new Error(clicked);
  console.log('качаю:', clicked.slice(3));

  for (let i = 0; i < 120 && !dlState; i++) await new Promise(r => setTimeout(r, 1000));
  t.close();
  if (dlState !== 'completed') throw new Error('загрузка не завершилась: ' + dlState);

  const added = fs.readdirSync(DIR).filter(f => !before.has(f));
  const zip = added.find(f => f.endsWith('.zip'));
  if (!zip) throw new Error('zip не появился в ' + DIR);

  const xlsx = path.join(DIR, `hranenie-${from}_${to}.xlsx`);
  unzip(path.join(DIR, zip), xlsx);
  fs.unlinkSync(path.join(DIR, zip));
  console.log('распакован:', path.basename(xlsx), Math.round(fs.statSync(xlsx).size / 1024), 'КБ');
}

// ---------- свёртка всех отчётов в storage/ ----------
function aggregate() {
  const files = fs.readdirSync(DIR).filter(f => f.endsWith('.xlsx') && !f.startsWith('~$'));
  if (!files.length) { console.log('в', DIR, 'нет ни одного xlsx'); process.exit(1); }

  const agg = new Map();
  for (const f of files) {
    const wb = XLSX.read(fs.readFileSync(path.join(DIR, f)));
    if (!wb.SheetNames.includes(SHEET)) { console.log('  пропуск (нет листа):', f); continue; }
    const rows = XLSX.utils.sheet_to_json(wb.Sheets[SHEET], { header: 1, defval: '' });
    // первая строка — заголовок отчёта «Платное хранение», шапка ниже
    const hi = rows.findIndex(r => r.includes('Артикул продавца'));
    if (hi < 0) { console.log('  пропуск (нет шапки):', f); continue; }
    const iArt = rows[hi].indexOf('Артикул продавца');
    const iSum = rows[hi].indexOf('Сумма хранения, руб');
    const iDate = rows[hi].indexOf('Дата');

    let n = 0, sum = 0;
    for (const r of rows.slice(hi + 1)) {
      const art = String(r[iArt] || '').trim();
      const date = String(r[iDate] || '').slice(0, 10);
      if (!art || !/^\d{4}-\d{2}-\d{2}$/.test(date)) continue;
      const key = date + ' ' + art;
      if (!agg.has(key)) agg.set(key, { period: weekLabel(date), date, article: art, sum: 0, rows: 0 });
      const a = agg.get(key);
      a.sum += Number(r[iSum]) || 0;
      a.rows++;
      n++; sum += Number(r[iSum]) || 0;
    }
    console.log(`  ${f}: ${n} строк, ${sum.toFixed(2)} ₽`);
  }

  const daily = [...agg.values()].sort((a, b) =>
    a.date.localeCompare(b.date) || a.article.localeCompare(b.article));
  daily.forEach(d => { d.sum = Math.round(d.sum * 100) / 100; });
  fs.writeFileSync(DAILY, JSON.stringify(daily, null, 1), 'utf-8');

  const byPeriod = new Map();
  for (const d of daily) byPeriod.set(d.period, (byPeriod.get(d.period) || 0) + d.sum);

  console.log(`\nПосле свёртки (день + артикул): ${daily.length} строк`);
  console.log(`Артикулов: ${new Set(daily.map(d => d.article)).size}`);
  console.log(`Всего хранение: ${daily.reduce((s, d) => s + d.sum, 0).toFixed(2)} ₽\n`);
  console.log('По неделям:');
  for (const [p, s] of [...byPeriod].sort()) console.log(`   ${p}  ${s.toFixed(2)} ₽`);
  console.log(`\nСвёртка — ${path.relative(__dirname, DAILY)}`);
  console.log('Дальше: node storage-upload.js');
}

(async () => {
  fs.mkdirSync(DIR, { recursive: true });
  if (!LOCAL) {
    console.log(`Период выгрузки: ${FROM} .. ${TO}\n`);
    await download(FROM, TO);
    console.log('');
  } else {
    console.log('Режим --local: сайт не трогаю.\n');
  }
  aggregate();
  process.exit(0);
})().catch(e => { console.log('\nОШИБКА:', e.message); process.exit(1); });
