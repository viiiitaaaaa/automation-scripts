const { chromium } = require('playwright');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// ================== НАСТРОЙКИ ==================
const LIST_URL = 'https://seller.wildberries.ru/suppliers-mutual-settlements/reports-implementations/reports-weekly-new';
const OUT = path.join(__dirname, 'reports');            // сюда падают zip-архивы
const EXTRACTED = path.join(OUT, 'extracted');          // сюда распакованные xlsx
const MANIFEST = path.join(OUT, 'manifest.json');
// Сколько последних недельных периодов забирать (на каждый период — 2 отчёта:
// «Основной» и «По выкупам»). По умолчанию 1 — только актуальный период.
// Больше: node reports.js 2
const PERIODS = parseInt(process.argv[2] || '1', 10);
// ===============================================

for (const d of [OUT, EXTRACTED]) if (!fs.existsSync(d)) fs.mkdirSync(d, { recursive: true });

// WB отдаёт zip, внутри которого лежит один настоящий xlsx
function extractInner(zipPath, outPath) {
  const ps = [
    'Add-Type -AssemblyName System.IO.Compression.FileSystem;',
    `$z=[System.IO.Compression.ZipFile]::OpenRead('${zipPath}');`,
    '$e=$z.Entries[0];',
    `[System.IO.Compression.ZipFileExtensions]::ExtractToFile($e,'${outPath}',$true);`,
    '$z.Dispose()',
  ].join(' ');
  execSync(`powershell -NoProfile -Command "${ps}"`, { stdio: 'pipe' });
}

const ruToISO = d => d.split('.').reverse().join('-');   // 20.07.2026 -> 2026-07-20

(async () => {
  const browser = await chromium.connectOverCDP('http://127.0.0.1:9222');
  const page = await browser.contexts()[0].newPage();

  await page.goto(LIST_URL, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForTimeout(12000);

  // строка таблицы: номер | продавец | «с ... по ...» | дата формирования | тип | суммы
  const rows = await page.evaluate(() => {
    const out = [];
    document.querySelectorAll('[class*="Reports-table-row"]').forEach(el => {
      const parts = (el.innerText || '').split(/\n+/).map(s => s.trim()).filter(Boolean);
      const num = parts.find(p => /^\d{6,12}$/.test(p));
      const per = parts.find(p => /^с \d{2}\.\d{2}\.\d{4} по \d{2}\.\d{2}\.\d{4}$/.test(p));
      const type = parts.find(p => /^(Основной|По выкупам)$/.test(p));
      if (num && per) out.push({ num, period: per, type: type || '' });
    });
    return out;
  });

  if (!rows.length) {
    console.log('Не нашёл ни одной строки отчётов. Кабинет открыт и залогинен?');
    process.exit(1);
  }

  // группируем по периоду, самые свежие — первыми
  const byPeriod = new Map();
  for (const r of rows) {
    const m = r.period.match(/с (\S+) по (\S+)/);
    const start = ruToISO(m[1]), end = ruToISO(m[2]);
    if (!byPeriod.has(r.period)) byPeriod.set(r.period, { period: r.period, start, end, reports: [] });
    byPeriod.get(r.period).reports.push({ num: r.num, type: r.type });
  }
  const periods = [...byPeriod.values()].sort((a, b) => b.end.localeCompare(a.end));

  const now = new Date();
  const curMonth = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
  console.log('Сегодня:', now.toISOString().slice(0, 10), '| текущий месяц:', curMonth);
  console.log('Периодов на странице:', periods.length, '\n');

  const take = periods.slice(0, PERIODS);
  console.log('БЕРУ:');
  for (const p of take) {
    const mark = p.end.startsWith(curMonth) ? 'текущий месяц' : 'ДРУГОЙ МЕСЯЦ';
    console.log(`   ${p.period}  [${mark}]  отчёты: ` +
                p.reports.map(r => `${r.num}${r.type ? ' (' + r.type + ')' : ''}`).join(', '));
  }
  console.log('');

  const manifest = [];
  let ok = 0, fail = 0;

  for (const p of take) {
    for (const rep of p.reports) {
      const zipPath = path.join(OUT, `${rep.num}.zip`);
      const xlsxPath = path.join(EXTRACTED, `${rep.num}.xlsx`);
      const entry = { num: rep.num, type: rep.type, period: p.period, start: p.start, end: p.end,
                      file: `${rep.num}.xlsx` };

      if (fs.existsSync(xlsxPath)) {
        console.log('SKIP  ', rep.num, '(уже скачан)');
        manifest.push(entry);
        continue;
      }

      try {
        console.log('КАЧАЮ ', rep.num, rep.type);
        await page.goto(`${LIST_URL}/report/${rep.num}`, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await page.waitForTimeout(6000);

        const btn = page.getByRole('button', { name: 'Скачать Excel' }).first();
        await btn.waitFor({ state: 'visible', timeout: 30000 });

        const [dl] = await Promise.all([
          page.waitForEvent('download', { timeout: 180000 }),
          btn.click(),
        ]);
        await dl.saveAs(zipPath);

        extractInner(zipPath, xlsxPath);
        const kb = Math.round(fs.statSync(xlsxPath).size / 1024);
        console.log('   распакован:', path.basename(xlsxPath), kb, 'КБ');

        manifest.push(entry);
        ok++;
      } catch (e) {
        fail++;
        console.log('   ОШИБКА:', e.message.split('\n')[0].slice(0, 80));
      }
      await page.waitForTimeout(2000);
    }
  }

  fs.writeFileSync(MANIFEST, JSON.stringify(manifest, null, 2), 'utf-8');
  console.log(`\nСкачано ${ok}, ошибок ${fail}. Список — reports/manifest.json`);
  process.exit(0);
})();
