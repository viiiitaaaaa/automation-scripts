from __future__ import annotations
import sys
import time
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

profile = int(sys.argv[1]) if len(sys.argv) > 1 else 859648353
url = sys.argv[2] if len(sys.argv) > 2 else "https://console.apify.com/actors/dky0rE40JOyXui6TR/input"

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, profile)["automation"]
print("[ok] CDP", auto["port"])

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(
        "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = browser.contexts[0] if browser.contexts else browser.new_context()
    pg = ctx.new_page()
    pg.goto(url, wait_until="domcontentloaded", timeout=60000)
    pg.bring_to_front()
    time.sleep(6)
    pg.screenshot(path="C:/Users/User/dolphin_anty/_apify_check.png")
    print("url now:", pg.url)
    print("title:", pg.title())
    browser.close()
