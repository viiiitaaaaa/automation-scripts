from __future__ import annotations
import time
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 859648353)["automation"]
print("[ok] CDP", auto["port"])

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(
        "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = browser.contexts[0] if browser.contexts else browser.new_context()
    print("open tabs:", len(ctx.pages))
    pg = ctx.new_page()
    pg.goto("https://www.dsers.com/application/import_list", wait_until="domcontentloaded", timeout=60000)
    time.sleep(6)
    pg.screenshot(path="C:/Users/User/dolphin_anty/_dsers_profile3.png")
    print("url now:", pg.url)
    print("title:", pg.title())
    browser.close()
