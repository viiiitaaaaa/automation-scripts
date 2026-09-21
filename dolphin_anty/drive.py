"""Управление уже поднятым браузером Dolphin (нужен работающий keeper.py).

    python drive.py --goto https://... --shot имя
    python drive.py --click "Install" --shot после-клика
    python drive.py --shot просто-посмотреть

Работает в одной вкладке, новых не плодит.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

CDP = Path(__file__).with_name("cdp.json")
SHOTS = Path(r"C:\Users\User\AppData\Local\Temp\claude\C--Users-User"
             r"\fe7d07b8-c28f-4c8f-b6c2-711eddff37f2\scratchpad\shots")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--goto")
    ap.add_argument("--click", help="текст кнопки/ссылки для клика")
    ap.add_argument("--wait", type=float, default=4)
    ap.add_argument("--shot", help="имя файла скриншота без расширения")
    ap.add_argument("--full", action="store_true", help="скрин всей страницы")
    args = ap.parse_args()

    if not CDP.exists():
        print("[x] cdp.json нет — keeper.py не запущен")
        return 1
    cdp = json.loads(CDP.read_text(encoding="utf-8"))

    from playwright.sync_api import sync_playwright
    SHOTS.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp["url"])
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()

        if args.goto:
            pg.goto(args.goto, wait_until="domcontentloaded", timeout=90_000)
        if args.click:
            # на страницах Shopify тот же текст бывает у скрытых дублей —
            # жать надо именно видимую кнопку
            done = False
            for sel in (f'button:has-text("{args.click}")',
                        f'a:has-text("{args.click}")',
                        f'text="{args.click}"'):
                loc = pg.locator(sel)
                for i in range(loc.count()):
                    item = loc.nth(i)
                    try:
                        if not item.is_visible():
                            continue
                        item.scroll_into_view_if_needed(timeout=5_000)
                        item.click(timeout=8_000)
                        print(f"[ok] клик: {sel} [{i}]")
                        done = True
                        break
                    except Exception:
                        continue
                if done:
                    break
            if not done:
                print(f"[x] не нашёл видимую: {args.click}")
        time.sleep(args.wait)

        print("URL  :", pg.url)
        print("TITLE:", pg.title())
        try:
            btns = pg.evaluate("""() => [...document.querySelectorAll('button,a[role=button],input[type=submit]')]
                .map(b => (b.innerText||b.value||'').trim()).filter(t => t && t.length < 40).slice(0, 30)""")
            print("КНОПКИ:", " | ".join(dict.fromkeys(btns)))
        except Exception:
            pass

        if args.shot:
            path = SHOTS / f"{args.shot}.png"
            pg.screenshot(path=str(path), full_page=args.full, timeout=180_000)
            print("SHOT :", path)

        # браузер держит keeper, здесь только отцепляемся
    return 0


if __name__ == "__main__":
    sys.exit(main())
