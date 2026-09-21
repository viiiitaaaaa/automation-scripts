const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

// ================== НАСТРОЙКИ ==================
// Apps Script, привязанный к таблице «1» (12OLxU8EDwN6nJQGySGEczKe0wflJN1dr4-4Y1Dynyxw)
const { BOOK_URL: SHEET_URL } = require('./book');   // единая книга, см. book.js
// Sheet1 и сводная «Лист1 (1)» УДАЛЕНЫ из книги 31.07.2026: их полностью
// заменили недельные вкладки, считающие от «Истории отчетов». Поэтому запись
// в Sheet1 выключена — иначе скрипт создаст лист заново.
const SHEET_NAME = 'Sheet1';
const WRITE_SHEET1 = false;
// Накопительный архив. Сюда периоды дописываются, а не затираются: первой
// колонкой идёт период, дальше — те же 84 колонки отчёта.
// В Sheet1 копить нельзя: сводная считает СУММЕСЛИМН по всему листу и начала бы
// складывать разные недели вместе.
const HIST_NAME = 'История отчетов';
const EXTRACTED = path.join(__dirname, 'reports', 'extracted');
const MANIFEST = path.join(__dirname, 'reports', 'manifest.json');
const HIST_LOG = path.join(__dirname, 'reports', 'history-log.json');
const CHUNK = 300;
// какой период лить: без аргумента — самый свежий; иначе подстрока, напр. "13.07"
const WANT = (process.argv[2] || '').replace(/^--.*/, '');
// --hist: только дописать в архив, Sheet1 не трогать (для добора прошлых недель)
const HIST_ONLY = process.argv.includes('--hist');
// ===============================================

async function toSheet(payload, tries = 4) {
  for (let t = 1; t <= tries; t++) {
    try {
      const r = await fetch(SHEET_URL, {
        method: 'POST',
        body: JSON.stringify(Object.assign({ sheet: SHEET_NAME }, payload)),
        signal: AbortSignal.timeout(300000),
      });
      if (!r.ok) throw new Error('код ' + r.status);
      const body = (await r.text()).trim();
      if (body !== 'ok') throw new Error('ответ: ' + body.slice(0, 80));
      return;
    } catch (e) {
      if (t === tries) throw e;
      console.log(`   попытка ${t} не удалась (${e.message}), повторяю...`);
      await new Promise(res => setTimeout(res, 3000 * t));
    }
  }
}

(async () => {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST, 'utf-8'));
  if (!manifest.length) { console.log('manifest.json пуст — сначала запустите reports.js'); process.exit(1); }

  // группируем по периоду, свежие первыми
  const byPeriod = new Map();
  for (const m of manifest) {
    if (!byPeriod.has(m.period)) byPeriod.set(m.period, []);
    byPeriod.get(m.period).push(m);
  }
  const periods = [...byPeriod.entries()].sort((a, b) => b[1][0].end.localeCompare(a[1][0].end));

  const picked = WANT
    ? periods.find(([p]) => p.includes(WANT))
    : periods[0];
  if (!picked) { console.log('Период не найден:', WANT); process.exit(1); }

  const [period, reports] = picked;
  console.log('ПЕРИОД:', period);
  console.log('Отчётов в периоде:', reports.length,
              '—', reports.map(r => `${r.num} (${r.type})`).join(', '));

  // склеиваем: заголовок один, строки — из всех отчётов периода
  let header = null;
  const data = [];
  for (const rep of reports) {
    const file = path.join(EXTRACTED, rep.file);
    if (!fs.existsSync(file)) { console.log('   НЕТ ФАЙЛА:', rep.file); continue; }
    const wb = XLSX.read(fs.readFileSync(file));
    const rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, defval: '' });
    if (!rows.length) continue;

    if (!header) header = rows[0];
    else if (JSON.stringify(rows[0]) !== JSON.stringify(header)) {
      console.log('   ВНИМАНИЕ: заголовок в', rep.num, 'отличается — строки всё равно добавлены');
    }
    const body = rows.slice(1);
    data.push(...body);
    console.log(`   ${rep.num} (${rep.type}): ${body.length} строк`);
  }

  if (!header) { console.log('Не удалось прочитать ни один отчёт'); process.exit(1); }
  console.log(`ИТОГО: ${data.length} строк x ${header.length} колонок\n`);

  const out = [header, ...data];

  // Первый запрос чистит содержимое листа. Каждый чанк пишется по явному номеру
  // строки (at), поэтому повтор после таймаута перезапишет тот же диапазон,
  // а не добавит строки второй раз.
  if (HIST_ONLY || !WRITE_SHEET1) {
    console.log('Sheet1 не трогаю (лист удалён из книги).\n');
  } else {
    console.log('Заливаю в лист', SHEET_NAME, '...');
    await toSheet({ wipe: true, at: 1, rows: out.slice(0, CHUNK) });
    for (let i = CHUNK; i < out.length; i += CHUNK) {
      await toSheet({ at: i + 1, rows: out.slice(i, i + CHUNK) });
      console.log('   строк', Math.min(i + CHUNK, out.length), 'из', out.length);
    }
    console.log('Sheet1 готов.\n');
  }

  // ---------- накопительный архив ----------
  // Пишем по явному номеру строки, а позицию помним локально: так повтор после
  // таймаута не задваивает строки, а уже залитый период не добавляется второй раз.
  const log = fs.existsSync(HIST_LOG)
    ? JSON.parse(fs.readFileSync(HIST_LOG, 'utf-8'))
    : { periods: [], nextRow: 1 };

  if (log.periods.includes(period)) {
    console.log(`Период уже есть в «${HIST_NAME}» — повторно не добавляю.`);
    process.exit(0);
  }

  console.log(`Дописываю в «${HIST_NAME}»...`);
  if (log.nextRow === 1) {
    await toSheet({ sheet: HIST_NAME, at: 1, rows: [['Период', ...header]] });
    log.nextRow = 2;
  }

  const histRows = data.map(r => [period, ...r]);
  for (let i = 0; i < histRows.length; i += CHUNK) {
    await toSheet({ sheet: HIST_NAME, at: log.nextRow + i, rows: histRows.slice(i, i + CHUNK) });
    console.log('   строк', Math.min(i + CHUNK, histRows.length), 'из', histRows.length);
  }

  log.nextRow += histRows.length;
  log.periods.push(period);
  fs.writeFileSync(HIST_LOG, JSON.stringify(log, null, 2), 'utf-8');

  console.log(`\nГотово. В архиве периодов: ${log.periods.length}, строк: ${log.nextRow - 2}.`);
  console.log('Сводная и недельные листы пересчитаются сами.');
  process.exit(0);
})();
