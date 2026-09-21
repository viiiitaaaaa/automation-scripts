# -*- coding: utf-8 -*-
"""
Сохранить ссылки со всех открытых вкладок AliExpress в текстовый файл (по одной
в строке) — без кликов, без Dsers. Если вкладка "пустая" после падения браузера
от перегруза памятью, перезагружает её, чтобы вернуть адрес.

    python save_open_tabs.py --profile 859648353 --out links_from_tabs.txt
"""
import argparse
import sys
import time
from pathlib import Path

from dolphin import DolphinLocal, start_with_retry


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    api = DolphinLocal(port=DolphinLocal.discover() or 3001)
    print("[..] подключаюсь к профилю %d …" % args.profile)
    auto = start_with_retry(api, args.profile)["automation"]
    print("[ok] CDP %s" % auto["port"])

    urls = []
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(
            "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()

        pages = list(ctx.pages)
        print("[ok] всего вкладок: %d" % len(pages))

        for i, pg in enumerate(pages, 1):
            try:
                pg.bring_to_front()
                if not (pg.url or ""):
                    pg.reload(wait_until="domcontentloaded", timeout=30_000)
                    time.sleep(4)
                u = pg.url or ""
            except Exception as e:
                print("%3d. [x] не смогла прочитать вкладку: %s" % (i, e))
                continue

            if "aliexpress" in u and "/item/" in u:
                urls.append(u)
                print("%3d. [ok] %s" % (i, u[:100]))
            else:
                print("%3d. [-] не товар: %s" % (i, u[:100] if u else "(пусто)"))

    args.out.write_text("\n".join(urls) + "\n", encoding="utf-8")
    print("\n[ok] сохранено ссылок: %d -> %s" % (len(urls), args.out))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[i] остановлено")
        sys.exit(130)
