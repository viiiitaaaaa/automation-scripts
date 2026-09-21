"""Показать все вкладки живого профиля и снять активную.

    python tabs.py                 — список вкладок
    python tabs.py --shot имя      — скрин последней вкладки
    python tabs.py --pick N --shot имя --click "Текст"
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
    ap.add_argument("--pick", type=int, help="номер вкладки (по умолчанию последняя)")
    ap.add_argument("--click")
    ap.add_argument("--shot")
    ap.add_argument("--wait", type=float, default=5)
    args = ap.parse_args()

    cdp = json.loads(CDP.read_text(encoding="utf-8"))
    from playwright.sync_api import sync_playwright
    SHOTS.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp["url"])
        ctx = browser.contexts[0]
        pages = ctx.pages
        print(f"Вкладок: {len(pages)}")
        for i, pg in enumerate(pages):
            try:
                print(f"  [{i}] {pg.title()[:50]:<50} {pg.url[:90]}")
            except Exception as e:
                print(f"  [{i}] (нет доступа) {e}")

        if args.click or args.shot:
            pg = pages[args.pick if args.pick is not None else len(pages) - 1]
            pg.bring_to_front()
            if args.click:
                loc = pg.locator(f'button:has-text("{args.click}"), a:has-text("{args.click}")')
                for i in range(loc.count()):
                    try:
                        if loc.nth(i).is_visible():
                            loc.nth(i).click(timeout=8_000)
                            print(f"[ok] клик [{i}]: {args.click}")
                            break
                    except Exception:
                        continue
                else:
                    print(f"[x] не нашёл: {args.click}")
            time.sleep(args.wait)
            print("АКТИВНАЯ:", pg.url)
            btns = pg.evaluate("""() => [...document.querySelectorAll('button,a[role=button]')]
                .filter(b => b.offsetParent !== null)
                .map(b => (b.innerText||'').trim()).filter(t => t && t.length < 40).slice(0, 25)""")
            print("КНОПКИ:", " | ".join(dict.fromkeys(btns)))
            if args.shot:
                pg.screenshot(path=str(SHOTS / f"{args.shot}.png"), timeout=180_000)
                print("SHOT :", SHOTS / f"{args.shot}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
