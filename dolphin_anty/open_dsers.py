# -*- coding: utf-8 -*-
"""Поднять профиль Dsers с доступом для автоматики и открыть Import list."""
import sys, time, json
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
json.dump({"port": auto["port"]}, open("cdp.json", "w"))
ws = "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"])
print("[ok] профиль поднят, порт", auto["port"], flush=True)

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(ws)
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()
    pg.goto("https://www.dsers.com/application/import_list",
            wait_until="domcontentloaded", timeout=90_000)
    pg.bring_to_front()
    for _ in range(20):
        time.sleep(3)
        n = pg.evaluate("() => document.querySelectorAll('button, input').length")
        if n > 3:
            break
    time.sleep(6)
    txt = pg.evaluate("() => (document.body.innerText.match(/Results:\s*[\d,]+/) || ['нет'])[0]")
    print("[ok] страница открыта:", txt, flush=True)
    print("ОКНО ОСТАВЛЯЮ ОТКРЫТЫМ", flush=True)
