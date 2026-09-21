"""Проверка альтернативных адресов каталога магазина."""
import json
import sys
import time

from playwright.sync_api import sync_playwright

from dolphin import DolphinLocal, start_with_retry

SID = sys.argv[1] if len(sys.argv) > 1 else "1105480827"
URLS = [
    f"https://www.aliexpress.com/store/{SID}/search/lamp.html",
    f"https://www.aliexpress.com/store/{SID}/search?SearchText=lamp",
    f"https://www.aliexpress.com/w/wholesale-lamp.html?shopId={SID}",
]

STATS = """() => ({
    itemLinks: document.querySelectorAll('a[href*="/item/"]').length,
    pageNums: [...document.querySelectorAll('a')].map(a => (a.innerText||'').trim())
        .filter(t => /^\\d{1,3}$/.test(t))
})"""

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 828976678)["automation"]

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}")
    ctx = b.contexts[0] if b.contexts else b.new_context()
    page = ctx.new_page()
    for u in URLS:
        try:
            page.goto(u, wait_until="domcontentloaded", timeout=90_000)
            time.sleep(6)
            page.mouse.wheel(0, 4000)
            time.sleep(2)
            print(f"\n{u}\n  -> {page.url[:110]}\n  {json.dumps(page.evaluate(STATS))}")
        except Exception as e:  # noqa: BLE001
            print(f"\n{u}\n  [x] {e}")
    page.close()
    b.close()
