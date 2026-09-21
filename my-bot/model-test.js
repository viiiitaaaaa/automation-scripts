const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

const CSV_FILE = path.join(__dirname, 'spp8.csv');
const EXCEL_DIR = path.join(__dirname, 'excel');
const ROWS_LIMIT = 20;

const LAT = { a:'а', e:'е', o:'о', p:'р', c:'с', y:'у', x:'х', k:'к', m:'м', t:'т', h:'н', b:'в' };
function norm(s) {
  let t = String(s || '').toLowerCase().replace(/ё/g, 'е');
  t = t.replace(/[a-z]/g, (ch, i) => {
    const cyr = c => c && /[а-я]/.test(c);
    return (cyr(t[i-1]) || cyr(t[i+1])) && LAT[ch] ? LAT[ch] : ch;
  });
  return t.replace(/[^a-zа-я0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
}

// семейства устройств
const FAMILIES = [
  { key: 'mi band',      re: /mi\s*band|xiaomi\s*band|smart\s*band|ми\s*бенд/ },
  { key: 'redmi watch',  re: /redmi\s*watch|поко\s*watch/ },
  { key: 'apple watch',  re: /apple\s*watch|iwatch/ },
  { key: 'galaxy fit',   re: /galaxy\s*fit/ },
  { key: 'galaxy watch', re: /galaxy\s*watch/ },
  { key: 'huawei fit',   re: /(huawei|хуавей).*fit|watch\s*fit/ },
  { key: 'huawei band',  re: /(huawei|хуавей).*band|бенд/ },
  { key: 'amazfit',      re: /amazfit/ },
  { key: 'garmin',       re: /garmin/ },
];

// вытаскиваем: семейство + номера + признак pro
function parse(name) {
  const t = norm(name);
  const fams = FAMILIES.filter(f => f.re.test(t)).map(f => f.key);
  const nums = new Set();
  // числа рядом с названием семейства (не размеры в мм)
  const cleaned = t.replace(/\d+\s*мм/g, ' ').replace(/\d+\s*mm/g, ' ');
  for (const m of cleaned.matchAll(/\b(\d{1,2})\b/g)) {
    const n = parseInt(m[1]);
    if (n >= 1 && n <= 12) nums.add(n);
  }
  return { fams, nums, pro: /\bpro\b/.test(t) };
}

function keepModel(our, comp) {
  const a = parse(our), b = parse(comp);
  if (!a.fams.length) return null;                 // модели нет — решает similarity
  if (!b.fams.some(f => a.fams.includes(f))) return false;  // другое семейство
  if (a.pro !== b.pro) return false;               // Pro / не Pro — разные
  if (!a.nums.size || !b.nums.size) return true;   // номеров нет — оставляем
  for (const n of a.nums) if (b.nums.has(n)) return true;
  return false;                                     // номера не пересеклись
}

const raw = fs.readFileSync(CSV_FILE, 'utf-8').replace(/^\uFEFF/, '');
const table = raw.split(/\r?\n/).filter(l => l.trim()).map(l => l.split(';'));
const ours = table.slice(1).filter(r => /^\d{6,12}$/.test(r[0]));

// показываем только товары, где есть модель
let shown = 0;
for (const r of ours) {
  if (!parse(r[3]).fams.length) continue;
  const f = path.join(EXCEL_DIR, `${r[0]}.xlsx`);
  if (!fs.existsSync(f)) continue;
  console.log('\n######', r[3]);
  const wb = XLSX.read(fs.readFileSync(f));
  const rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, defval: '' });
  for (const e of rows.slice(1, 1 + ROWS_LIMIT)) {
    const k = keepModel(r[3], e[2]);
    if (k === false) continue;   // не показываем отсеянное, чтобы не засорять
    console.log('  ОК  ', String(e[2]).slice(0, 62));
  }
  if (++shown >= 6) break;
}
process.exit(0);