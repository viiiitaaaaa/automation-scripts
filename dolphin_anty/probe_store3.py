"""Кликнуть вкладку Products в витрине магазина и посмотреть, что там."""
import json
import sys
import time

from playwright.sync_api import sync_playwright

from dolphin import DolphinLocal, start_with_retry

SID = sys.argv[1] if len(sys.argv) > 1 else "1105480827"

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 828976678)["automation"]

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}")
    ctx = b.contexts[0] if b.contexts else b.new_context()
    page = ctx.new_page()
    page.goto(f"https://www.aliexpress.com/store/{SID}", wait_until="domcontentloaded", timeout=90_000)
    time.sleep(6)

    tab = page.locator("xpath=//*[normalize-space(text())='Products']").last
    print("вкладка Products найдена:", tab.count() > 0)
    tab.click()
    time.sleep(7)
    page.mouse.wheel(0, 4000)
    time.sleep(3)

    print("URL после клика:", page.url)
    print(json.dumps(page.evaluate("""() => {
        const txt = document.body.innerText;
        return {
            itemsLabel: (txt.match(/([\\d,]+)\\s+items?/i) || [])[1] || null,
            itemLinks: document.querySelectorAll('a[href*="/item/"]').length,
            pageNums: [...document.querySelectorAll('a')]
                .map(a => (a.innerText || '').trim())
                .filter(t => /^\\d{1,3}$/.test(t)),
            firstItems: [...document.querySelectorAll('a[href*="/item/"]')]
                .slice(0, 3).map(e => (e.innerText || '').trim().slice(0, 50))
        };
    }"""), ensure_ascii=False, indent=1))

    page.close()
    b.close()
