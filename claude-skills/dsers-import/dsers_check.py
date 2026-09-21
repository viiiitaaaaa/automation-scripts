# -*- coding: utf-8 -*-
"""Сколько сейчас товаров в Import list (после перезагрузки страницы)."""
import time, sys
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

SHOT = r"C:\Users\User\AppData\Local\Temp\claude\C--Users-User\01751d72-549c-49dc-8269-5150f5435db9\scratchpad\dsers_after.png"

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()
    pg.goto("https://www.dsers.com/application/import_list", wait_until="domcontentloaded", timeout=90000)
    pg.bring_to_front()
    for _ in range(20):
        time.sleep(3)
        if pg.evaluate("() => document.querySelectorAll('button, input').length") > 3:
            break
    time.sleep(5)
    info = pg.evaluate("""() => {
      let cnt = null;
      for (const el of document.querySelectorAll('a[href*="import_list"], li, span')) {
        const m = (el.textContent || '').replace(/\\s+/g,' ').trim().match(/^Import list\\s*(\\d+)$/i);
        if (m) { cnt = m[1]; break; }
      }
      const titles = [];
      for (const el of document.querySelectorAll('a[href*="/item/"], .product-title, h3, .ant-input')) {
        const t = (el.value || el.textContent || '').trim();
        if (t && t.length > 15 && t.length < 90) titles.push(t);
      }
      return {count: cnt, total: document.body.innerText.match(/(\\d+)\\s*\\/\\s*page/i)?.[0] || null,
              titles: [...new Set(titles)].slice(0, 12)};
    }""")
    print("Import list счётчик:", info["count"])
    print("на странице:", info["total"])
    print("товары:")
    for t in info["titles"]:
        print("   -", t[:80])
    pg.screenshot(path=SHOT)
    print("скриншот:", SHOT)
