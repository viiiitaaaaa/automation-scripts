const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

const CSV_FILE = path.join(__dirname, 'spp8.csv');
const EXCEL_DIR = path.join(__dirname, 'excel');

const raw = fs.readFileSync(CSV_FILE, 'utf-8').replace(/^\uFEFF/, '');
const table = raw.split(/\r?\n/).filter(l => l.trim()).map(l => l.split(';'));
const ours = table.slice(1).filter(r => /^\d{6,12}$/.test(r[0]));

// показываем 3 наших товара и по 8 конкурентов к каждому
for (const r of ours.slice(0, 3)) {
  const f = path.join(EXCEL_DIR, `${r[0]}.xlsx`);
  if (!fs.existsSync(f)) continue;
  console.log('\n############ НАШ:', r[3]);
  const wb = XLSX.read(fs.readFileSync(f));
  const rows = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]], { header: 1, defval: '' });
  rows.slice(1, 9).forEach(e => console.log('   -', e[2]));
}
process.exit(0);