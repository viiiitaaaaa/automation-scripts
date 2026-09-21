const fs = require('fs');
const path = require('path');

const f = path.join(__dirname, 'photo-cache.json');
const cache = JSON.parse(fs.readFileSync(f, 'utf-8'));

let kept = 0, removed = 0;
const clean = {};
for (const id in cache) {
  if (cache[id]) { clean[id] = cache[id]; kept++; }
  else removed++;
}

fs.writeFileSync(f, JSON.stringify(clean));
console.log('Оставлено найденных:', kept);
console.log('Удалено пустых (будут перепроверены):', removed);
process.exit(0);