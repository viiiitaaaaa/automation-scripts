// Заливает apps-script/book.gs в редактор Apps Script книги и публикует
// новую версию развёртывания.
//
// Порядок ровно такой, каким он работает вручную:
//   monaco setValue -> Ctrl+S -> дождаться «Сохранено на Диске»
//   -> Развернуть -> Управление развертываниями -> карандаш -> Новая версия
//   -> Развернуть.
//
// Три способа молча оставить в проде старый код (все ловятся здесь):
//   1) Ctrl+S не сработал, а публикация пошла дальше — поэтому ждём текст
//      «Сохранено на Диске» и падаем на «Несохраненные изменения»;
//   2) вкладка редактора зависает и Runtime.evaluate отваливается по таймауту
//      — лечится закрытием вкладки через /json/close и открытием свежей;
//   3) меню развёртывания не реагирует на el.click() — нужны настоящие
//      Input.dispatchMouseEvent по центру элемента.
//
// Проверять результат надо ЗАПРОСОМ новой команды, а не сообщением об успехе.
//
// Запуск: node deploy-gs.js

const fs = require('fs');
const path = require('path');
const { attach, httpJson } = require('./cdp-lite');

const SCRIPT_URL = 'https://script.google.com/home/projects/1eLiR9T4TRklcHFhd8sTpGzSiXXJAim2VHWvY0fgkR9O09H5Mw8VkQn90/edit';
const FILE = path.join(__dirname, 'apps-script', 'book.gs');
const sleep = ms => new Promise(r => setTimeout(r, ms));

// Текст кнопок Apps Script содержит служебные глифы иконок (символ из
// приватной зоны Unicode после переноса строки), поэтому сравнивать строку
// целиком нельзя — сверяем только начало и берём самый компактный элемент,
// иначе клик уходит в контейнер во всю ширину шапки.
async function clickByText(t, texts, what) {
  const box = await t.evaluate(`(() => {
    const want = ${JSON.stringify(texts)};
    let best = null;
    document.querySelectorAll('div,span,button,a,li').forEach(e => {
      const s = (e.innerText || '').replace(/\\s+/g, ' ').trim();
      if (!want.some(w => s.startsWith(w))) return;
      const r = e.getBoundingClientRect();
      if (r.width < 20 || r.height < 10 || r.width > 600) return;
      const area = r.width * r.height;
      if (!best || area < best.area) best = { area, x: r.left + r.width / 2, y: r.top + r.height / 2 };
    });
    return best;
  })()`);
  if (!box) throw new Error('не нашёл на странице: ' + what);
  for (const type of ['mousePressed', 'mouseReleased']) {
    await t.send('Input.dispatchMouseEvent', { type, x: box.x, y: box.y, button: 'left', clickCount: 1 });
  }
  await sleep(1500);
}

(async () => {
  const code = fs.readFileSync(FILE, 'utf8');
  console.log('book.gs:', code.length, 'символов');

  const t = await attach('script.google.com', SCRIPT_URL);
  await t.send('Page.bringToFront');
  await sleep(3000);

  // ---------- 1. подменяем код ----------
  const set = await t.evaluate(`(() => {
    if (!window.monaco || !monaco.editor.getModels().length) return 'нет редактора monaco';
    monaco.editor.getModels()[0].setValue(${JSON.stringify(code)});
    return 'ok';
  })()`);
  if (set !== 'ok') throw new Error(set);
  console.log('код подставлен в редактор');
  await sleep(1500);

  // ---------- 2. сохраняем ----------
  await t.send('Input.dispatchKeyEvent', { type: 'rawKeyDown', modifiers: 2, key: 's', code: 'KeyS', windowsVirtualKeyCode: 83 });
  await t.send('Input.dispatchKeyEvent', { type: 'keyUp', modifiers: 2, key: 's', code: 'KeyS', windowsVirtualKeyCode: 83 });

  let saved = false;
  for (let i = 0; i < 40 && !saved; i++) {
    await sleep(1000);
    const txt = await t.evaluate(`document.body.innerText`);
    if (/Сохранено на Диске/i.test(txt)) saved = true;
  }
  if (!saved) throw new Error('редактор не показал «Сохранено на Диске» — код НЕ сохранён');
  console.log('сохранено на Диске');

  // ---------- 3. новая версия развёртывания ----------
  // Сначала закрываем всё, что могло остаться открытым с прошлого запуска:
  // при открытом окне первый же клик уходит в него, а не в меню шапки.
  for (let i = 0; i < 2; i++) {
    await t.send('Input.dispatchKeyEvent', { type: 'rawKeyDown', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    await t.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 });
    await sleep(1000);
  }

  await clickByText(t, ['Начать развертывание', 'Развернуть'], 'кнопку «Начать развертывание»');
  await clickByText(t, ['Управление развертываниями'], 'пункт «Управление развертываниями»');
  await sleep(2000);

  const pencil = await t.evaluate(`(() => {
    const el = [...document.querySelectorAll('[aria-label="Редактировать"],[aria-label="Изменить"],[aria-label="Edit"]')]
      .find(e => e.getBoundingClientRect().width > 0);
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  })()`);
  if (!pencil) throw new Error('не нашёл карандаш «Изменить» в развертываниях');
  for (const type of ['mousePressed', 'mouseReleased']) {
    await t.send('Input.dispatchMouseEvent', { type, x: pencil.x, y: pencil.y, button: 'left', clickCount: 1 });
  }
  await sleep(1500);

  // Список версий. Если в нём стоит «Версия N», надо ОТКРЫТЬ его и выбрать
  // «Новая версия»: иначе публикуется старая версия кода, а скрипт при этом
  // честно рапортует «развертывание обновлено». Именно так 04.08.2026 дважды
  // уехал в прод предыдущий код.
  const currentVersion = () => t.evaluate(`(() => {
    const el = [...document.querySelectorAll('span,div')].find(e => {
      const s = (e.innerText || '').replace(/\\s+/g, ' ').trim();
      const r = e.getBoundingClientRect();
      return /^(Новая версия|Версия \\d+)/.test(s) && r.width > 100 && r.height < 60;
    });
    return el ? (el.innerText || '').replace(/\\s+/g, ' ').trim().slice(0, 40) : null;
  })()`);

  let ver = await currentVersion();
  console.log('в списке версий:', ver);
  if (ver && !/^Новая версия/.test(ver)) {
    await clickByText(t, [ver.slice(0, 12)], 'список версий');           // открыть список
    await clickByText(t, ['Новая версия'], 'пункт «Новая версия»');
    ver = await currentVersion();
    console.log('после выбора:', ver);
  }
  if (!ver || !/^Новая версия/.test(ver)) {
    throw new Error('не удалось выбрать «Новая версия» — публикацию отменяю, чтобы не выкатить старый код');
  }

  // Кнопка подтверждения называется так же, как та, что открывала меню, но она
  // именно <button> внутри окна, а в шапке — <div>. Ищем строго button, иначе
  // клик уходит обратно в шапку и окно остаётся висеть.
  const confirm = await t.evaluate(`(() => {
    const el = [...document.querySelectorAll('button')].find(e =>
      (e.innerText || '').replace(/\\s+/g, ' ').trim().startsWith('Начать развертывание') &&
      e.getBoundingClientRect().width > 20);
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
  })()`);
  if (!confirm) throw new Error('не нашёл кнопку подтверждения в окне развертывания');
  for (const type of ['mousePressed', 'mouseReleased']) {
    await t.send('Input.dispatchMouseEvent', { type, x: confirm.x, y: confirm.y, button: 'left', clickCount: 1 });
  }
  await sleep(10000);

  const done = /Развертывание обновлено|обновлено/i.test(await t.evaluate(`document.body.innerText`));
  console.log(done ? 'развертывание обновлено' : 'ВНИМАНИЕ: подтверждения не увидел — проверьте запросом');
  t.close();
  process.exit(0);
})().catch(async e => {
  console.error('ОШИБКА:', e.message);
  // Зависшую вкладку редактора лечим закрытием: переоткрытие URL не помогает.
  if (/CDP не ответил|websocket/i.test(e.message)) {
    const list = await httpJson('/json/list').catch(() => []);
    const tab = list.find(x => x.url && x.url.includes('script.google.com'));
    if (tab) { await httpJson('/json/close/' + tab.id).catch(() => {}); console.error('вкладка редактора закрыта — запустите ещё раз'); }
  }
  process.exit(1);
});
