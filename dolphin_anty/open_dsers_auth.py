from __future__ import annotations
import sys
import time
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

url = sys.argv[1]

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 859648353)["automation"]
print("[ok] CDP", auto["port"])

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(
        "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = browser.contexts[0] if browser.contexts else browser.new_context()
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    pg.bring_to_front()
    pg.goto(url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(6)
    pg.screenshot(path="C:/Users/User/dolphin_anty/_dsers_auth_result.png")
    print("url now:", pg.url)
    print("title:", pg.title())
    browser.close()
