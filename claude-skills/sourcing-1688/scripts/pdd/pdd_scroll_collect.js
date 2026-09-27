// Pinduoduo, страница выдачи mobile.pinduoduo.com/search_result.html — ОДИН запуск через javascript_tool.
// Листает медленно (3–5 с на шаг, как человек), до 60 шагов; стоп на капче, «没有更多», или если 4 раза подряд
// внизу не прибавилось карточек (PDD притормаживает — не давить). Потом сам скачивает pdd_itemsN.json в «Загрузки»
// и складывает номера товаров (goods_id) в window.__ids — их читать ОТДЕЛЬНО (pdd_goods_ids.js), пока вкладка открыта.
// Поменять имя файла (FILE) под номер поиска. Ждать файл: until ls ~/Downloads/pdd_itemsN*.json; do sleep 5; done
const FILE = 'pdd_items.json';
window.__sc = {done: false, steps: 0, why: ''};
(async () => {
  const sl = ms => new Promise(r => setTimeout(r, ms));
  let stuck = 0, lastN = 0;
  await sl(3000);
  while (window.__sc.steps < 60) {
    window.scrollBy({top: 400 + Math.random() * 300, behavior: 'smooth'});
    window.__sc.steps++;
    await sl(3000 + Math.random() * 2000);
    const txt = document.body.innerText.slice(-400), n = document.querySelectorAll('div._1unt3Js-').length;
    if (/验证|captcha|滑块/i.test(document.title + txt)) { window.__sc.why = 'captcha'; break; }
    if (/没有更多|到底了|已经到底|暂无更多/.test(txt)) { window.__sc.why = 'end'; break; }
    if (window.scrollY + innerHeight >= document.documentElement.scrollHeight - 50) {
      if (n === lastN) { if (++stuck >= 4) { window.__sc.why = 'stuck'; break; } } else stuck = 0;
      lastN = n;
    }
  }
  // карточка товара = div._1unt3Js- (класс может смениться — тогда искать div с img pddpic и «¥»)
  const cards = [...document.querySelectorAll('div._1unt3Js-')];
  const out = cards.map((c, i) => {
    const im = [...c.querySelectorAll('img')].map(x => x.currentSrc || x.src || x.dataset.src || '')
      .find(u => /pddpic|yangkeduo/.test(u) && !/icon|tag|label/.test(u)) || '';
    const lines = c.innerText.split('\n').map(s => s.trim()).filter(Boolean);
    const pi = lines.indexOf('¥');
    const price = pi >= 0 ? parseFloat(lines[pi + 1] + (lines[pi + 2] && lines[pi + 2].startsWith('.') ? lines[pi + 2] : '')) : null;
    const title = lines.filter(s => s.length > 12 && !/已拼|已售|¥|发货$/.test(s)).sort((a, b) => b.length - a.length)[0]
      || lines.find(s => s.length > 8) || '';
    const sales = lines.find(s => /已拼|已售|万\+?件|件$/.test(s)) || '';
    return {n: i + 1, title, price, sales, img: im,
            tags: lines.filter(s => s !== title && s !== sales && s !== '¥' && !/^\.?\d+$/.test(s)).join(' | ')};
  });
  // goods_id из React-свойств карточки (ссылка: https://mobile.yangkeduo.com/goods.html?goods_id=ID)
  const gid = card => {
    const k = Object.keys(card).find(x => x.startsWith('__reactFiber'));
    let f = card[k];
    for (let i = 0; f && i < 30; i++, f = f.return) {
      const p = f.memoizedProps;
      if (!p || typeof p !== 'object') continue;
      for (const v of [p, p.item, p.data, p.goods, p.itemData, p.goodsInfo])
        if (v && typeof v === 'object' && (v.goodsID || v.goods_id)) return String(v.goodsID || v.goods_id);
    }
    return null;
  };
  window.__ids = cards.map(gid);
  const b = new Blob([JSON.stringify(out)], {type: 'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(b); a.download = FILE;
  document.body.appendChild(a); a.click(); a.remove();
  window.__sc.done = true; window.__sc.n = out.length; window.scrollTo(0, 0);
})();
'started';
