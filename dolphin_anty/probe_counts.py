# -*- coding: utf-8 -*-
"""Сколько товаров Dsers числит в Import list и My Products, и нет ли ошибки."""
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
    for _ in range(25):
        time.sleep(3)
        if pg.evaluate("() => document.querySelectorAll('button, input').length") > 3:
            break
    time.sleep(8)
    info = pg.evaluate(r"""() => {
      const t = document.body.innerText;
      const g = (re) => { const m = t.match(re); return m ? m[1] : '?'; };
      return {
        importList: g(/Import list\s+([\d,]+)/i),
        myProducts: g(/My Products\s+([\d,]+)/i),
        results:    g(/Results:\s*([\d,]+)/i),
        limit:      (t.match(/[^\n]*(limit|quota|upgrade|exceed)[^\n]*/i) || ['-'])[0].slice(0, 120)
      };
    }""")
    print(json.dumps(info, ensure_ascii=False, indent=1))
