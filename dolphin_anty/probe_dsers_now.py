# -*- coding: utf-8 -*-
"""Короткая диагностика страницы Dsers: где мы и что видно. Без чтения всей страницы."""
import sys, time, json
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()
    pg.goto("https://www.dsers.com/application/import_list",
            wait_until="domcontentloaded", timeout=90_000)
    pg.bring_to_front()
    for wait in (10, 10, 10, 10):
        time.sleep(wait)
        info = pg.evaluate("""() => ({
          url: location.href,
          title: document.title.slice(0,60),
          login: /log ?in|sign ?in|password/i.test(document.body.innerText.slice(0,3000)),
          rows: document.querySelectorAll('[class*="product"],[class*="Product"]').length,
          imgs: document.querySelectorAll('img[src*="alicdn"]').length,
          aliLinks: document.querySelectorAll('a[href*="aliexpress"]').length,
          pager: (document.querySelector('.ant-pagination')||{}).innerText || '',
          text: document.body.innerText.replace(/\s+/g,' ').slice(0,220)
        })""")
        print(json.dumps(info, ensure_ascii=False, indent=1), flush=True)
        if info["imgs"] > 5:
            break
