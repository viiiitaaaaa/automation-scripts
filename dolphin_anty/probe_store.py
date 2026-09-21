"""Разведка страницы магазина: сколько товаров, есть ли пагинация, какие разделы.

    python probe_store.py 1105480827
"""
import json
import sys
import time

from playwright.sync_api import sync_playwright

from dolphin import DolphinLocal, start_with_retry

SID = sys.argv[1] if len(sys.argv) > 1 else "1105480827"
URLS = [
    f"https://www.aliexpress.com/store/{SID}/pages/all-items.html"
    f"?sortType=bestmatch_sort&shop_sortType=bestmatch_sort",
    f"https://www.aliexpress.com/store/{SID}",
]

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 828976678)["automation"]

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}")
    ctx = b.contexts[0] if b.contexts else b.new_context()
    page = ctx.new_page()

    for url in URLS:
        print("\n" + "=" * 60)
        print("Открываю:", url)
        page.goto(url, wait_until="domcontentloaded", timeout=90_000)
        time.sleep(6)
        print("Итоговый URL:", page.url)
        print("Заголовок:", page.title()[:70])

        print(json.dumps(page.evaluate("""() => {
            const txt = document.body.innerText;
            return {
                itemsLabel: (txt.match(/([\\d,]+)\\s+items?/i) || [])[1] || null,
                itemLinks: document.querySelectorAll('a[href*="/item/"]').length,
                pageNums: [...document.querySelectorAll('a')]
                    .map(a => (a.innerText || '').trim())
                    .filter(t => /^\\d{1,3}$/.test(t)),
                tabs: [...document.querySelectorAll('a, [role="tab"]')]
                    .map(e => (e.innerText || '').trim())
                    .filter(t => t && t.length < 25).slice(0, 25),
                allItemsLinks: [...document.querySelectorAll('a')]
                    .filter(a => /all-items|allItems|category/i.test(a.href || ''))
                    .slice(0, 10).map(a => a.href.slice(0, 120))
            };
        }"""), ensure_ascii=False, indent=1))

    page.close()
    b.close()
