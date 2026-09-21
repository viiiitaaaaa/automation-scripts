"""Разведка: открыть хэштег в Instagram через профиль Dolphin и снять скрин."""
import sys
import time

from dolphin import DolphinLocal, start_with_retry

PROFILE_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 859648353
URL = sys.argv[2] if len(sys.argv) > 2 else "https://www.instagram.com/explore/search/keyword/?q=%23plaidskirt"

api = DolphinLocal(port=DolphinLocal.discover())
data = start_with_retry(api, PROFILE_ID)
auto = data["automation"]
ws = f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}"

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(ws)
    ctx = browser.contexts[0] if browser.contexts else browser.new_context()
    page = ctx.new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    print("TITLE:", page.title())
    print("URL:", page.url)
    page.screenshot(path="C:/Users/User/Desktop/ig_probe.png", full_page=False)
    print("[ok] screenshot saved")
    browser.close()
