import sys
import time

from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

PROFILE_ID = 859648353
URL = sys.argv[1] if len(sys.argv) > 1 else "https://www.instagram.com/p/DGLOHrHOz6f/"

api = DolphinLocal(port=DolphinLocal.discover())
data = start_with_retry(api, PROFILE_ID)
auto = data["automation"]
ws = f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(ws)
    ctx = browser.contexts[0] if browser.contexts else browser.new_context()
    page = ctx.new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    try:
        page.wait_for_selector("main article, main", timeout=20000)
    except Exception:
        pass
    time.sleep(4)
    text = page.inner_text("body")
    with open("C:/Users/User/Desktop/ig_post_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    page.screenshot(path="C:/Users/User/Desktop/ig_post_debug.png")
    print("[ok] saved text + screenshot")
    browser.close()
