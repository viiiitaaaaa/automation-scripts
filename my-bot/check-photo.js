const fs = require('fs');
const path = require('path');

const arts = [213900875, 213900882];
const CACHE_FILE = path.join(__dirname, 'photo-cache.json');
const cache = fs.existsSync(CACHE_FILE)
  ? JSON.parse(fs.readFileSync(CACHE_FILE, 'utf-8')) : {};

(async () => {
  for (const id of arts) {
    console.log('\n=== Артикул', id, '===');
    console.log('В кэше:', cache[id] === undefined ? 'НЕТ ЗАПИСИ' : (cache[id] || 'записан как ПУСТО'));

    const vol = Math.floor(id / 100000);
    const part = Math.floor(id / 1000);
    console.log('vol' + vol, 'part' + part);

    const found = [];
    for (let h = 1; h <= 60; h++) {
      const host = String(h).padStart(2, '0');
      const url = `https://basket-${host}.wbbasket.ru/vol${vol}/part${part}/${id}/images/c246x328/1.webp`;
      try {
        const r = await fetch(url, { method: 'HEAD' });
        if (r.ok) found.push(url);
      } catch {}
    }

    if (found.length) {
      console.log('НАЙДЕНО:', found[0]);
    } else {
      console.log('не найдено ни на одном сервере (01-60)');
      // пробуем другие форматы
      for (const sz of ['big', 'c516x688', 'tm']) {
        for (let h = 1; h <= 60; h++) {
          const host = String(h).padStart(2, '0');
          const url = `https://basket-${host}.wbbasket.ru/vol${vol}/part${part}/${id}/images/${sz}/1.webp`;
          try {
            const r = await fetch(url, { method: 'HEAD' });
            if (r.ok) { console.log('  но есть в размере', sz + ':', url); h = 99; }
          } catch {}
        }
      }
    }
  }
  process.exit(0);
})();