// Сканер магазина 1688 (страница shopXXX.1688.com/page/offerlist.htm?sortType=tradenumdown&pageNum=N, с расширением
// 1688官方采购助手). Запускать через javascript_tool на открытой странице. Возвращает строки-кандидаты.
// Листание: параметр pageNum в адресе НЕ работает — жать кнопку «下一页 >», потом снова запускать сканер.
// sortType=tradenumdown — по продажам (берём 3 стр. = 90 хитов); sortType=timedown — сначала новые.
// Правила (её): цена 35–70 ¥; выложено ≤ DAYS дней назад; без брюк/мини/комплектов; сортировка по 月代销.
(async () => {
  const DAYS = 60, PMIN = 35, PMAX = 70;
  for (let i = 0; i < 6; i++) { window.scrollBy(0, 1500); await new Promise(r => setTimeout(r, 600)); }
  const L = document.body.innerText.split('\n').map(s => s.trim()).filter(Boolean);
  const today = new Date();
  const mv = s => { const m = (s || '').match(/(\d+)/); if (!m) return 0; return /以内/.test(s) ? 0 : +m[1]; };
  const rows = [];
  for (let k = 0; k < L.length; k++) {
    if (L[k] !== '采购助手') continue;
    const pre = L.slice(Math.max(0, k - 12), k);
    const t = pre.filter(x => x.length > 12 && /[裙裤衫衣套装肩]/.test(x) && !/已售|新人价|¥/.test(x)).pop() || '';
    const pm = pre.join('|').match(/¥\|?(\d+)(\|?\.\d+)?/) || [];
    const price = parseFloat((pm[1] || '0') + ((pm[2] || '').replace('|', '')));
    const blk = L.slice(k, k + 16).join('|');
    const g = r => (blk.match(r) || [])[1] || '';
    const date = g(/上架日期:\|(\d{4}-\d\d-\d\d)/), month = g(/月代销:\|([^|]+)/), year = g(/年销量:\|([^|]+)/), cat = g(/类目:\|女装 > ([^|]+)/);
    const age = date ? Math.round((today - new Date(date)) / 864e5) : 999;
    const bad = /裤|套装|两件套|三件套|短裙|超短/.test(t) && !/裙裤/.test(t) || /裤/.test(cat);
    if (price >= PMIN && price <= PMAX && age <= DAYS && !bad)
      rows.push({ t: t.slice(0, 34), price, month, m: mv(month), year, date, cat });
  }
  rows.sort((a, b) => b.m - a.m);
  return rows.map(r => `${r.t} | ${r.price}¥ | мес:${r.month} | год:${r.year} | ${r.date} | ${r.cat}`).join('\n');
})()
