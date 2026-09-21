# -*- coding: utf-8 -*-
"""Полностраничные скрины каталога ARTMELLIO.

    py -3.13 shots_artmellio.py                     весь /collections/all
    py -3.13 shots_artmellio.py --url ССЫЛКА        другой раздел
    py -3.13 shots_artmellio.py --pages 3           только первые 3 страницы

У Shopify нумерация серверная, поэтому ?page=N работает как надо - кликать по
пагинатору, как на AliExpress, не требуется.
"""
import re
import sys
import time
from pathlib import Path

from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

PROFILE = 836461485                       # «Декор» - профиль ARTMELLIO
BASE = "https://www.artmellio.com/collections/all"
OUT = Path(r"C:\Users\User\Desktop\скрины artmellio")
MAX_PAGES = 40

url = BASE
предел = MAX_PAGES
if "--url" in sys.argv:
    url = sys.argv[sys.argv.index("--url") + 1]
if "--pages" in sys.argv:
    предел = int(sys.argv[sys.argv.index("--pages") + 1])

url = re.sub(r"[?&]page=\d+", "", url).rstrip("?&")
раздел = (url.rstrip("/").split("/")[-1] or "all").split("?")[0]
OUT.mkdir(parents=True, exist_ok=True)


def autoscroll(pg):
    """Прокрутить до низа - иначе картинки останутся ленивыми заглушками."""
    pg.evaluate("""() => new Promise(res => {
        let y = 0;
        const t = setInterval(() => {
            window.scrollBy(0, 900);
            y += 900;
            if (y >= document.body.scrollHeight) { clearInterval(t); res(); }
        }, 90);
    })""")
    pg.wait_for_timeout(1200)
    pg.evaluate("() => window.scrollTo(0, 0)")
    pg.wait_for_timeout(400)


api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, PROFILE)["automation"]
print("[ok] профиль поднят", flush=True)

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(
        "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()
    pg.set_viewport_size({"width": 1600, "height": 1000})

    снято = 0
    for n in range(1, предел + 1):
        адрес = "%s?page=%d" % (url, n)
        # вкладка на переднем плане: в фоне Chrome тормозит отрисовку,
        # и карточки не успевают появиться
        товаров = 0
        for попытка in (1, 2):
            pg.goto(адрес, wait_until="domcontentloaded", timeout=90_000)
            pg.bring_to_front()
            for _ in range(20):
                time.sleep(1.5)
                товаров = pg.evaluate(
                    """() => document.querySelectorAll("a[href*='/products/']").length""")
                if товаров:
                    break
            if товаров:
                break
            print("   стр.%d: пусто, пробую ещё раз" % n, flush=True)
        if not товаров:
            print("   стр.%d: товаров нет - конец" % n, flush=True)
            break

        autoscroll(pg)
        # ширина строго по окну: длинная лента фильтров иначе растягивает
        # скрин на несколько тысяч пикселей, и товары превращаются в точки
        ширина = pg.evaluate("() => document.documentElement.clientWidth")
        высота = pg.evaluate("() => document.body.scrollHeight")
        файл = OUT / ("%s — страница %d.png" % (раздел, n))
        pg.screenshot(path=str(файл), timeout=180_000,
                      clip={"x": 0, "y": 0, "width": ширина, "height": высота})
        снято += 1
        print("   стр.%d: товаров %d -> %s" % (n, товаров, файл.name), flush=True)

    pg.close()

print("\nГОТОВО: снято страниц %d" % снято, flush=True)
print("Папка: %s" % OUT, flush=True)
