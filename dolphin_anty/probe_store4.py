"""Где у магазина полный каталог: вкладка акции vs поиск внутри магазина."""
import json
import sys
import time

from playwright.sync_api import sync_playwright

from dolphin import DolphinLocal, start_with_retry

SID = sys.argv[1] if len(sys.argv) > 1 else "1105480827"

STATS = """() => {
    const txt = document.body.innerText;
    return {
        itemsLabel: (txt.match(/([\\d,]+)\\s+items?|([\\d,]+)\\s+results?/i) || [])[0] || null,
        itemLinks: document.querySelectorAll('a[href*="/item/"]').length,
        pageNums: [...document.querySelectorAll('a')]
            .map(a => (a.innerText || '').trim())
            .filter(t => /^\\d{1,3}$/.test(t))
    };
}"""

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 828976678)["automation"]

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}")
    ctx = b.contexts[0] if b.contexts else b.new_context()
    page = ctx.new_page()

    # 1. вкладка акции
    page.goto(f"https://www.aliexpress.com/store/{SID}", wait_until="domcontentloaded", timeout=90_000)
    time.sleep(6)
    promo = page.locator("xpath=//*[normalize-space(text())='Back to school']").last
    if promo.count():
        promo.click()
        time.sleep(7)
        page.mouse.wheel(0, 5000)
        time.sleep(3)
        print("\n--- вкладка акции")
        print("URL:", page.url[:120])
        print(json.dumps(page.evaluate(STATS), ensure_ascii=False))

    # 2. поиск внутри магазина
    page.goto(f"https://www.aliexpress.com/store/{SID}", wait_until="domcontentloaded", timeout=90_000)
    time.sleep(6)
    box = page.locator('input[placeholder*="store" i], input[placeholder*="Search" i]').last
    print("\n--- поиск в магазине, поле найдено:", box.count() > 0)
    if box.count():
        box.click()
        box.fill("a")
        box.press("Enter")
        time.sleep(8)
        page.mouse.wheel(0, 5000)
        time.sleep(3)
        print("URL:", page.url[:150])
        print(json.dumps(page.evaluate(STATS), ensure_ascii=False))

    page.close()
    b.close()
