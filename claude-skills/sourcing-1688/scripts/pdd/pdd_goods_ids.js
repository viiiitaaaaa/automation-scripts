// Pinduoduo: номера товаров (goods_id) с УЖЕ открытой и пролистанной страницы выдачи — без новых запросов к сайту.
// Второй раз файл Chrome часто не скачивает, поэтому номера читаются из ответа, по 50 штук (длинный ответ обрезается):
//   1) window.__ids.slice(0,50).join(',')      2) window.__ids.slice(50).join(',')
// Порядок = порядок карточек = поле n в pdd_items.json. Сверка: первые 14 символов карточек 1, 50, 100 должны
// совпасть с title в json. Номера сохранить строкой через запятую в <папка>/pdd_ids.txt — svod_pdd.py сам сделает ссылки.
// Если window.__ids нет (страницу перезагружали) — вычислить заново:
window.__ids = window.__ids || [...document.querySelectorAll('div._1unt3Js-')].map(card => {
  const k = Object.keys(card).find(x => x.startsWith('__reactFiber'));
  let f = card[k];
  for (let i = 0; f && i < 30; i++, f = f.return) {
    const p = f.memoizedProps;
    if (!p || typeof p !== 'object') continue;
    for (const v of [p, p.item, p.data, p.goods, p.itemData, p.goodsInfo])
      if (v && typeof v === 'object' && (v.goodsID || v.goods_id)) return String(v.goodsID || v.goods_id);
  }
  return null;
});
const c = [...document.querySelectorAll('div._1unt3Js-')];
[window.__ids.filter(Boolean).length, [0, 49, 99].map(i => c[i] && c[i].innerText.replace(/\s+/g, '').slice(0, 14)).join(' / ')];
