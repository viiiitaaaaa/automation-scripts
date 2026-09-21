# -*- coding: utf-8 -*-
"""Как устроены галочки на карточках и кнопка Push to Store. Ничего не нажимаем."""
import sys, time, json
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
ws = "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"])

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(ws)
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()
    pg.goto("https://www.dsers.com/application/import_list",
            wait_until="domcontentloaded", timeout=90_000)
    pg.bring_to_front()
    for _ in range(25):
        time.sleep(3)
        if pg.evaluate("() => document.querySelectorAll('button, input').length") > 3:
            break
    time.sleep(8)

    info = pg.evaluate(r"""() => {
      const boxes = [...document.querySelectorAll('input[type="checkbox"]')];
      // ищем контейнер карточки: поднимаемся от галочки вверх, пока не найдём номер Dsers
      let cardInfo = null;
      for (const cb of boxes) {
        let el = cb;
        for (let i = 0; i < 8 && el; i++) {
          const h = el.outerHTML || '';
          const m = h.match(/\b(2\d{18})\b/);
          if (m) {
            cardInfo = {
              level: i,
              tag: el.tagName,
              cls: (typeof el.className === 'string' ? el.className : '').slice(0, 80),
              dsersId: m[1],
              head: h.slice(0, 300)
            };
            break;
          }
          el = el.parentElement;
        }
        if (cardInfo) break;
      }
      const push = [...document.querySelectorAll('button,div,span')]
        .filter(e => /push to store/i.test((e.innerText || '').trim()) &&
                     (e.innerText || '').length < 40)
        .map(e => ({tag: e.tagName,
                    cls: (typeof e.className === 'string' ? e.className : '').slice(0, 70),
                    dis: e.disabled === true}));
      return {checkboxes: boxes.length, card: cardInfo, push: push.slice(0, 4)};
    }""")
    print(json.dumps(info, ensure_ascii=False, indent=1)[:2000])
