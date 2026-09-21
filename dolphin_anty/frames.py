"""Работа внутри iframe встроенных приложений Shopify (Flow и т.п.).

    python frames.py --pick 0                       — какие фреймы есть
    python frames.py --pick 0 --click "Текст" --shot имя
    python frames.py --pick 0 --text                — весь видимый текст фрейма
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

BTN_JS = """() => [...document.querySelectorAll('button,a[role=button],a,[role=menuitem],li')]
    .filter(b => b.offsetParent !== null)
    .map(b => (b.innerText||'').trim().replace(/\\s+/g,' '))
    .filter(t => t && t.length < 60).slice(0, 40)"""


def app_frame(pg):
    """Самый крупный фрейм приложения (не рекламный, не служебный)."""
    best, best_len = None, -1
    for f in pg.frames:
        if f == pg.main_frame:
            continue
        try:
            n = len(f.evaluate("() => document.body ? document.body.innerText : ''"))
        except Exception:
            continue
        if n > best_len:
            best, best_len = f, n
    return best


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--pick", type=int, default=0)
    ap.add_argument("--click")
    ap.add_argument("--fill", nargs=2, metavar=("SELECTOR", "VALUE"))
    ap.add_argument("--text", action="store_true")
    ap.add_argument("--shot")
    ap.add_argument("--wait", type=float, default=6)
    args = ap.parse_args()

    cdp = json.loads(CDP.read_text(encoding="utf-8"))
    from playwright.sync_api import sync_playwright
    SHOTS.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(cdp["url"])
        ctx = browser.contexts[0]
        pg = ctx.pages[args.pick]
        pg.bring_to_front()
        time.sleep(1.5)

        print("Фреймы:")
        for f in pg.frames:
            print(f"  - {f.url[:110]}")

        fr = app_frame(pg)
        if fr is None:
            print("[x] фрейм приложения не найден")
            return 1
        print(f"\nРаботаю во фрейме: {fr.url[:110]}")

        if args.click:
            loc = fr.locator(f'button:has-text("{args.click}"), a:has-text("{args.click}"), '
                             f'[role=menuitem]:has-text("{args.click}"), li:has-text("{args.click}")')
            done = False
            for i in range(loc.count()):
                try:
                    if loc.nth(i).is_visible():
                        loc.nth(i).click(timeout=8_000)
                        print(f"[ok] клик [{i}]: {args.click}")
                        done = True
                        break
                except Exception:
                    continue
            if not done:
                print(f"[x] не нашёл во фрейме: {args.click}")

        if args.fill:
            sel, val = args.fill
            try:
                fr.fill(sel, val, timeout=8_000)
                print(f"[ok] заполнил {sel} = {val}")
            except Exception as e:
                print(f"[x] {e}")

        time.sleep(args.wait)
        fr = app_frame(pg) or fr

        if args.text:
            print("\n--- ТЕКСТ ФРЕЙМА ---")
            print(fr.evaluate("() => document.body.innerText")[:3000])
        else:
            print("\nКНОПКИ:", " | ".join(dict.fromkeys(fr.evaluate(BTN_JS))))

        if args.shot:
            pg.screenshot(path=str(SHOTS / f"{args.shot}.png"), timeout=180_000)
            print("SHOT :", SHOTS / f"{args.shot}.png")
    return 0


if __name__ == "__main__":
    sys.exit(main())
