"""
Просто открыть ссылки вкладками в профиле Dolphin{anty}. Без скринов.

Браузер Dolphin гаснет вскоре после завершения процесса, который его запустил,
поэтому скрипт после открытия вкладок ОСТАЁТСЯ РАБОТАТЬ и держит окно живым.
Останови его (Ctrl+C или закрытие фоновой задачи), когда закончишь с вкладками.

    python open_links.py --file links.txt
    python open_links.py --url ССЫЛКА1 --url ССЫЛКА2
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

from dolphin import DolphinLocal, start_with_retry
from shots import MAX_TABS, close_extra_tabs


def to_desktop(url: str) -> str:
    """Мобильную версию — в десктопную страницу со списком всех товаров.

    Короткие ссылки a.aliexpress.com разворачиваются в m.aliexpress.com/store/<id>,
    а нужна браузерная версия: там привычная вёрстка и пагинация.
    """
    m = re.search(r"m\.aliexpress\.com/store/(\d+)", url)
    if not m:
        return url
    return (f"https://www.aliexpress.com/store/{m.group(1)}/pages/all-items.html"
            f"?sortType=bestmatch_sort&shop_sortType=bestmatch_sort")


def main() -> int:
    ap = argparse.ArgumentParser(description="Открыть ссылки вкладками (без скринов)")
    ap.add_argument("--profile", type=int, default=828976678)
    ap.add_argument("--url", action="append", default=[])
    ap.add_argument("--file", type=Path, help="файл со ссылками (по одной в строке)")
    ap.add_argument("--hours", type=float, default=6, help="сколько часов держать браузер открытым")
    args = ap.parse_args()

    urls = list(args.url)
    if args.file:
        urls += re.findall(r"https?://\S+", args.file.read_text("utf-8", errors="replace"))
    if not urls:
        print("[x] не заданы ссылки")
        return 1
    if len(urls) > MAX_TABS:
        print(f"[x] {len(urls)} ссылок — больше лимита {MAX_TABS} вкладок")
        return 1

    from playwright.sync_api import sync_playwright

    api = DolphinLocal(port=DolphinLocal.discover() or 3001)
    print(f"[..] поднимаю профиль {args.profile} …")
    auto = start_with_retry(api, args.profile)["automation"]
    print(f"[ok] профиль поднят, CDP {auto['port']}")

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}")
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        close_extra_tabs(ctx)   # убрать вкладки от прошлой работы

        for i, u in enumerate(urls, 1):
            pg = ctx.new_page()
            try:
                pg.goto(u, wait_until="domcontentloaded", timeout=90_000)
                time.sleep(1.5)
                pg.goto(to_desktop(pg.url), wait_until="domcontentloaded", timeout=90_000)
                time.sleep(1.5)
                # сколько товаров видит страница — сразу понятно, весь ли ассортимент
                cnt = pg.evaluate("""() => {
                    const m = document.body.innerText.match(/([\\d,]+)\\s+items?/i);
                    return m ? m[1] : null;
                }""")
                print(f"{i:>3}. {pg.title()[:55]}  — товаров: {cnt or '?'}")
            except Exception as e:  # noqa: BLE001
                print(f"{i:>3}. [x] {u} — {e}")

        # первая вкладка была пустой заглушкой профиля
        if ctx.pages and not ctx.pages[0].url.startswith("http"):
            ctx.pages[0].close()

        print(f"\n[ok] открыто вкладок: {len(ctx.pages)}")
        print(f"[i] держу браузер открытым {args.hours} ч. Останови задачу, когда закончишь.")
        try:
            time.sleep(args.hours * 3600)
        except KeyboardInterrupt:
            pass
        browser.close()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[i] остановлено")
        sys.exit(130)
    except Exception as e:  # noqa: BLE001
        print(f"[x] {e}")
        sys.exit(1)
