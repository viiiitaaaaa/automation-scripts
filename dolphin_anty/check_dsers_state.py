from __future__ import annotations
import time
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 859648353)["automation"]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(
        "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = browser.contexts[0] if browser.contexts else browser.new_context()
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    pg.bring_to_front()
    time.sleep(8)
    pg.screenshot(path="C:/Users/User/dolphin_anty/_dsers_auth_result2.png")
    print("url now:", pg.url)
    print("title:", pg.title())
    browser.close()
