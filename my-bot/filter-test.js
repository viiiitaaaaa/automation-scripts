const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

const CSV_FILE = path.join(__dirname, 'spp8.csv');
const EXCEL_DIR = path.join(__dirname, 'excel');
const ROWS_LIMIT = 20;

// --- нормализация
const norm = s => String(s || '').toLowerCase()
  .replace(/ё/g, 'е').replace(/[^a-zа-я0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();

const STOP = new Set(['для','и','в','на','с','из','к','по','а','the','watch','часов','часы',
  'мм','смарт','умных','умные','ремешок','браслет','ремешки']);

// --- модели устройств: если есть у нас, должна быть и у конкурента
const MODELS = [
  { key: 'redmi watch 3', re: /redmi\s*watch\s*3/ },
  { key: 'redmi watch 4', re: /redmi\s*watch\s*4/ },
  { key: 'redmi watch 2', re: /redmi\s*watch\s*2/ },
  { key: 'mi band',       re: /mi\s*band|xiaomi\s*band|smart\s*band/ },
  { key: 'apple watch',   re: /apple\s*watch|iwatch/ },
  { key: 'amazfit',       re: /amazfit/ },
  { key: 'huawei',        re: /huawei/ },
  { key: 'samsung',       re: /samsung|galaxy\s*watch/ },
  { key: 'garmin',        re: /garmin/ },
];

const modelOf = t => MODELS.filter(m => m.re.test(t)).map(m => m.key);

const words = t => new Set(norm(t).split(' ').filter(w => w.length > 2 && !STOP.has(w)));

function similarity(a, b) {
  const A = words(a), B = words(b);
  if (!A.size) return 1;
  let common = 0;
  for (const w of A) if (B.has(w)) common++;
  return common / A.size;
}

const MIN_SIM = 0.34;   // порог совпадения по словам

function keep(ourName, compName) {
  const om = modelOf(norm(ourName));
  const cm = modelOf(norm(compName));

  if (om.length) {
    // у нас указана модель — у конкурента должна быть та же
    return cm.some(m => om.includes(m));
  }
  // модели нет — сравниваем по словам
  return similarity(ourName, compName) >= MIN_SIM;
}

// --- прогон
const raw = fs.readFileSync(CSV_FILE, 'utf-8').replace(/^\uFEFF/, '');
const table = raw.split(/\r?\n/).filter(l => l.trim()).map(l => l.split(';'));
const ours = table.slice(1).filter(r => /^\d{6,12}$/.test(r[0]));

let kept = 0, dropped = 0;
for (const r of ours.slice(0, 5)) {
  const f = path.join(EXCEL_DIR, `${r[0]}.xlsx`);
  if (!fs.existsSync(f)) continue;
  console.log('\n############ НАШ:', r[3]);
  const wb = XLSX.read(fs.readFileSync(f));
  const rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, defval: '' });
  for (const e of rows.slice(1, 1 + ROWS_LIMIT)) {
    const ok = keep(r[3], e[2]);
    if (ok) kept++; else dropped++;
    console.log(ok ? '  ОК  ' : '  --  ', String(e[2]).slice(0, 65));
  }
}
console.log('\nОставлено:', kept, '| удалено:', dropped);
process.exit(0);