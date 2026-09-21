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
    pg.screenshot(path="C:/Users/User/dolphin_anty/_dbg1_loaded.png")

    field.fill("")
    field.fill("https://www.aliexpress.us/item/3256810205087711.html")
    time.sleep(1)
    pg.screenshot(path="C:/Users/User/dolphin_anty/_dbg2_typed.png")

    box = field.bounding_box()
    print("input box:", box)

    # list all OK-ish buttons with positions
    info = pg.evaluate("""(inputRect) => {
        const out = [];
        for (const el of document.querySelectorAll('button, .ant-btn')) {
            const t = (el.textContent || '').replace(/\\s+/g,' ').trim();
            if (!/^ok$/i.test(t)) continue;
            const r = el.getBoundingClientRect();
            out.push({t, x:r.x, y:r.y, w:r.width, h:r.height,
                      inModal: !!el.closest('.ant-modal, [role="dialog"], .ant-drawer'),
                      disabled: el.disabled || el.classList.contains('ant-btn-disabled') || el.classList.contains('disabled')});
        }
        return {buttons: out, inputRect};
    }""", box)
    print("OK buttons found:", info)

    time.sleep(2)
    pg.screenshot(path="C:/Users/User/dolphin_anty/_dbg3_before_click.png")
    b.close()
