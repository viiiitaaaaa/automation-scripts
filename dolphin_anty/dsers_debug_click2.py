from __future__ import annotations
import time
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

LINKS = [
    "https://www.aliexpress.us/item/3256810205087711.html",
    "https://www.aliexpress.us/item/3256801296510720.html",
]

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 859648353)["automation"]

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()
    pg.goto("https://www.dsers.com/application/import_list", wait_until="domcontentloaded", timeout=90000)
    pg.bring_to_front()
    field = pg.locator("input[placeholder*='Please enter the product link']")
    field.wait_for(timeout=90000)
    time.sleep(3)

    for i, link in enumerate(LINKS, 1):
        field.fill("")
        field.fill(link)
        time.sleep(1)
        ok_btn = pg.locator("button:has-text('OK'), .ant-btn:has-text('OK')").first
        ok_btn.click()
        print(f"[{i}] clicked OK for {link}")
        time.sleep(2)

        confirm = pg.locator("button:has-text('CONFIRM'), .ant-btn:has-text('CONFIRM')").first
        if confirm.count() and confirm.is_visible():
            confirm.click()
            print(f"[{i}] clicked CONFIRM (Import Language dialog appeared)")
        else:
            print(f"[{i}] no Import Language dialog this time")

        time.sleep(3)
        pg.screenshot(path=f"C:/Users/User/dolphin_anty/_dbg2_after_{i}.png")

        cards = pg.evaluate("() => document.querySelectorAll('.ant-checkbox-input').length")
        print(f"[{i}] cards on page now: {cards}")

    b.close()
