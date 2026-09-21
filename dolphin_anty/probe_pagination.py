"""Разведка: как устроена пагинация на странице магазина AliExpress."""
import json
import sys
import time

from playwright.sync_api import sync_playwright

from dolphin import DolphinLocal, start_with_retry
from shots import STORE_URL

PROFILE = int(sys.argv[1]) if len(sys.argv) > 1 else 828976678

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
data = start_with_retry(api, PROFILE)
auto = data["automation"]
print("[ok] CDP", auto["port"])

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}")
    ctx = b.contexts[0] if b.contexts else b.new_context()
    page = ctx.new_page()
    page.goto(STORE_URL, wait_until="domcontentloaded", timeout=90_000)
    time.sleep(5)
    page.mouse.wheel(0, 20000)
    time.sleep(3)

    print("URL:", page.url)

    info = page.evaluate("""() => {
        const out = {buttons: [], links: [], firstCards: []};
        // кандидаты в пагинатор: элементы с числами/стрелками внизу страницы
        document.querySelectorAll('button, a, li, div[role="button"]').forEach(el => {
            const t = (el.innerText || '').trim();
            const cls = (el.className && el.className.toString) ? el.className.toString() : '';
            if (!t || t.length > 12) return;
            if (/^(next|далее|вперед|→|>|«|»|[0-9]{1,3})$/i.test(t) ||
                /pagin|next|page/i.test(cls) || /pagin|next|page/i.test(el.getAttribute('class') || '')) {
                out.buttons.push({
                    tag: el.tagName, text: t, cls: cls.slice(0, 120),
                    aria: el.getAttribute('aria-label'), href: el.getAttribute('href'),
                    y: Math.round(el.getBoundingClientRect().top + window.scrollY)
                });
            }
        });
        // первые карточки товаров — по ним поймём, сменилась ли страница
        document.querySelectorAll('a[href*="/item/"]').forEach((el, i) => {
            if (i < 3) out.firstCards.push((el.innerText || '').trim().slice(0, 60));
        });
        out.buttons = out.buttons.slice(-40);
        return out;
    }""")
    print(json.dumps(info, ensure_ascii=False, indent=1)[:4000])
    b.close()
