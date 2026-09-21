# -*- coding: utf-8 -*-
"""Собрать адреса пунктов левого меню Dsers."""
import time
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
print("CDP", auto["port"])
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()
    pg.goto("https://www.dsers.com/application/my_products", wait_until="domcontentloaded", timeout=90000)
    pg.bring_to_front()
    time.sleep(10)
    links = pg.evaluate("""() => {
      const out = [];
      for (const a of document.querySelectorAll('a[href]')) {
        const t = (a.textContent || '').replace(/\\s+/g,' ').trim();
        const r = a.getBoundingClientRect();
        if (t && t.length < 40 && r.width > 10) out.push({text: t, href: a.getAttribute('href')});
      }
      return out.slice(0, 40);
    }""")
    for l in links:
        print("  %-28s %s" % (l["text"][:28], l["href"]))
    time.sleep(180)
