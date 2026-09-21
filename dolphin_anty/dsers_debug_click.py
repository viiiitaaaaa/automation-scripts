from __future__ import annotations
import time
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

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

    field.fill("")
    field.fill("https://www.aliexpress.us/item/3256810205087711.html")
    time.sleep(1)

    ok_btn = pg.locator("button:has-text('OK'), .ant-btn:has-text('OK')").first
    ok_btn.click()
    print("clicked OK, waiting...")

    for i in range(10):
        time.sleep(2)
        pg.screenshot(path=f"C:/Users/User/dolphin_anty/_dbg_after_click_{i}.png")
        msg = pg.evaluate("""() => {
            const el = document.querySelector('.ant-message, .ant-notification, .ant-message-notice-content');
            return el ? el.textContent.trim().slice(0,200) : null;
        }""")
        if msg:
            print(f"t+{i*2}s message:", msg)
    b.close()
