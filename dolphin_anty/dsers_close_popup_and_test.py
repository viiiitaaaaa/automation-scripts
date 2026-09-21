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
    time.sleep(8)

    # close the promo modal if present: look for a close/X icon, or the chevron collapse icon
    closed = pg.evaluate("""() => {
        // try common close icon selectors first
        const closeSel = ['.ant-modal-close', '[aria-label="close"]', '[aria-label="Close"]',
                           '.close-icon', '.icon-close'];
        for (const sel of closeSel) {
            const el = document.querySelector(sel);
            if (el) { el.click(); return {ok:true, via: sel}; }
        }
        return {ok:false};
    }""")
    print("close attempt:", closed)
    time.sleep(2)
    pg.screenshot(path="C:/Users/User/dolphin_anty/_dsers_popup_check.png")

    field = pg.locator("input[placeholder*='Please enter the product link']")
    print("field visible:", field.is_visible() if field.count() else "not found")
    b.close()
