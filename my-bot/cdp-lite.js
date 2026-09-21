// Минимальный клиент Chrome DevTools Protocol.
//
// Playwright (chromium.connectOverCDP) на этом профиле виснет на подключении:
// он цепляется сразу ко всем таргетам браузера и не отпускает. Сырой CDP,
// подключённый к ОДНОЙ нужной вкладке, работает мгновенно — поэтому здесь
// свой маленький клиент вместо Playwright.
//
// Chrome должен быть запущен с --remote-debugging-port=9222.

const http = require('http');

const httpJson = urlPath => new Promise((res, rej) => {
  http.get({ host: '127.0.0.1', port: 9222, path: urlPath }, r => {
    let d = '';
    r.on('data', c => d += c);
    r.on('end', () => { try { res(JSON.parse(d)); } catch (e) { rej(e); } });
  }).on('error', () => rej(new Error(
    'Chrome не отвечает на 127.0.0.1:9222. Запустите его с --remote-debugging-port=9222.')));
});

/**
 * Подключается к вкладке, чей URL содержит urlPart.
 * Если такой вкладки нет и передан openUrl — открывает её.
 */
async function attach(urlPart, openUrl) {
  const { webSocketDebuggerUrl } = await httpJson('/json/version');
  const ws = new WebSocket(webSocketDebuggerUrl);
  await new Promise((res, rej) => {
    ws.onopen = res;
    ws.onerror = () => rej(new Error('не удалось открыть websocket CDP'));
  });

  let id = 0;
  const pend = new Map();
  const listeners = [];
  ws.onmessage = e => {
    const m = JSON.parse(e.data);
    if (m.id && pend.has(m.id)) {
      const { res, rej } = pend.get(m.id);
      pend.delete(m.id);
      m.error ? rej(new Error(m.error.message)) : res(m.result);
    } else if (m.method) {
      for (const fn of listeners) fn(m);
    }
  };

  const raw = (method, params = {}, sessionId) => new Promise((res, rej) => {
    const m = ++id;
    pend.set(m, { res, rej });
    ws.send(JSON.stringify({ id: m, method, params, ...(sessionId ? { sessionId } : {}) }));
    setTimeout(() => {
      if (pend.has(m)) { pend.delete(m); rej(new Error('CDP не ответил на ' + method)); }
    }, 120000);
  });

  const findTarget = async () => (await raw('Target.getTargets')).targetInfos
    .find(x => x.type === 'page' && x.url.includes(urlPart));

  let target = await findTarget();
  if (!target && openUrl) {
    await raw('Target.createTarget', { url: openUrl });
    for (let i = 0; i < 30 && !target; i++) {
      await new Promise(r => setTimeout(r, 1000));
      target = await findTarget();
    }
    await new Promise(r => setTimeout(r, 5000));   // дать странице догрузиться
  }
  if (!target) throw new Error('вкладка не найдена: ' + urlPart);

  const { sessionId } = await raw('Target.attachToTarget', { targetId: target.targetId, flatten: true });
  const send = (method, params) => raw(method, params, sessionId);

  // выполнить выражение в странице; промисы дожидаются
  const evaluate = async expression => {
    const r = await send('Runtime.evaluate', {
      expression, awaitPromise: true, returnByValue: true,
    });
    if (r.exceptionDetails) {
      throw new Error(r.exceptionDetails.exception?.description
        || r.exceptionDetails.text || 'ошибка JS на странице');
    }
    return r.result.value;
  };

  return {
    raw, send, evaluate, sessionId,
    targetId: target.targetId,
    url: target.url,
    on: fn => listeners.push(fn),
    close: () => ws.close(),
  };
}

module.exports = { attach, httpJson };
