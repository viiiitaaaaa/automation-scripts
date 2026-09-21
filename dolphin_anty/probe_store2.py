"""Найти, где у магазина лежит полный каталог: смотрим навигацию главной страницы."""
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
    time.sleep(7)

    print("URL:", page.url)
    print(json.dumps(page.evaluate("""() => ({
        // все ссылки внутри магазина: там и разделы каталога
        storeLinks: [...document.querySelectorAll('a[href*="/store/"]')]
            .map(a => ({t: (a.innerText || '').trim().slice(0, 40), h: a.href.slice(0, 140)}))
            .filter(x => x.h)
            .slice(0, 40),
        iframes: [...document.querySelectorAll('iframe')].map(f => (f.src || '').slice(0, 120)),
        // подписи разделов витрины
        sections: [...document.querySelectorAll('[class*="tab" i], [class*="nav" i]')]
            .map(e => (e.innerText || '').trim().replace(/\\s+/g, ' ').slice(0, 60))
            .filter(Boolean).slice(0, 20)
    })"""), ensure_ascii=False, indent=1))

    page.close()
    b.close()
