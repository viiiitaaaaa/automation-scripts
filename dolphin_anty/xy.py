"""Клик и ввод по координатам — для встроенных приложений Shopify.

Playwright не достаёт до кросс-доменного iframe через CDP, но клики мышью
браузер маршрутизирует внутрь него сам.

    python xy.py --shot имя                     — снять и показать размер вьюпорта
    python xy.py --click 1828 197 --shot имя
    python xy.py --type "Продукт создан" --shot имя
    python xy.py --key Enter --shot имя
    python xy.py --close-extra                  — закрыть лишние вкладки
"""
from __future__ import annotations

import argparse, json, sys, time
from pathlib import Path

CDP = Path(__file__).with_name("cdp.json")
SHOTS = Path(r"C:\Users\User\AppData\Local\Temp\claude\C--Users-User"
             r"\fe7d07b8-c28f-4c8f-b6c2-711eddff37f2\scratchpad\shots")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--pick", type=int, default=0)
    ap.add_argument("--click", nargs=2, type=float, metavar=("X", "Y"))
    ap.add_argument("--type")
    ap.add_argument("--key")
    ap.add_argument("--scroll", type=int, help="прокрутка колесом, пиксели")
    ap.add_argument("--move", nargs=2, type=float, metavar=("X", "Y"),
                    help="навести курсор перед прокруткой, не кликая")
    ap.add_argument("--close-extra", action="store_true")
    ap.add_argument("--shot")
    ap.add_argument("--wait", type=float, default=4)
    args = ap.parse_args()

    cdp = json.loads(CDP.read_text(encoding="utf-8"))
    from playwright.sync_api import sync_playwright
    SHOTS.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(cdp["url"])
        ctx = b.contexts[0]

        if args.close_extra:
            keep = ctx.pages[args.pick]
            for pg in list(ctx.pages):
                if pg is not keep:
                    try:
                        pg.close()
                    except Exception:
                        pass
            print(f"[ok] осталась одна вкладка: {keep.url[:80]}")
            return 0

        pg = ctx.pages[args.pick]
        pg.bring_to_front()
        time.sleep(1)
        vs = pg.evaluate("() => ({w: innerWidth, h: innerHeight, dpr: devicePixelRatio})")
        print(f"вьюпорт: {vs['w']}x{vs['h']} CSS, dpr {vs['dpr']} "
              f"(скрин будет {int(vs['w']*vs['dpr'])}x{int(vs['h']*vs['dpr'])})")

        if args.move:
            pg.mouse.move(args.move[0], args.move[1])
            time.sleep(0.3)
            print(f"[ok] курсор в ({args.move[0]}, {args.move[1]})")
        if args.scroll:
            pg.mouse.wheel(0, args.scroll)
        if args.click:
            x, y = args.click
            pg.mouse.move(x, y)
            time.sleep(0.3)
            pg.mouse.click(x, y)
            print(f"[ok] клик ({x}, {y})")
        if args.type:
            pg.keyboard.type(args.type, delay=45)
            print(f"[ok] ввод: {args.type}")
        if args.key:
            pg.keyboard.press(args.key)
            print(f"[ok] клавиша: {args.key}")

        time.sleep(args.wait)
        if args.shot:
            path = SHOTS / f"{args.shot}.png"
            pg.screenshot(path=str(path), timeout=180_000)
            print("SHOT :", path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
