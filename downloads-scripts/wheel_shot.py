#!/usr/bin/env python3
"""
Скриншот длинной страницы с прокруткой через эмуляцию колеса мыши.
Работает там, где scrollTop не помогает.

Chrome должен быть запущен с --remote-debugging-port=9222
и открыт на нужной странице.

    python wheel_shot.py out.png
    python wheel_shot.py out.png --x 900 --y 500     # где крутить колесо
    python wheel_shot.py out.png --crop 300 200 1600 900   # область кадра
    python wheel_shot.py out.png --max 100 --pause 1.0
"""

import argparse
import io
import time

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def attach(port=9222):
    o = Options()
    o.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    return webdriver.Chrome(options=o)


def wheel(driver, x, y, delta):
    """Крутим колесо мыши в точке (x, y) на delta пикселей вниз."""
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseWheel",
        "x": x, "y": y,
        "deltaX": 0, "deltaY": delta,
        "pointerType": "mouse",
    })


def frames_differ(a: Image.Image, b: Image.Image, threshold=0.002):
    """Грубое сравнение: изменился ли кадр после прокрутки."""
    if a.size != b.size:
        return True
    sa = a.resize((100, 100)).convert("L").tobytes()
    sb = b.resize((100, 100)).convert("L").tobytes()
    diff = sum(1 for p, q in zip(sa, sb) if abs(p - q) > 12)
    return diff / len(sa) > threshold


def main():
    p = argparse.ArgumentParser()
    p.add_argument("output", nargs="?", default="fullpage.png")
    p.add_argument("--port", type=int, default=9222)
    p.add_argument("--x", type=int, help="X точки прокрутки (по умолч. центр)")
    p.add_argument("--y", type=int, help="Y точки прокрутки (по умолч. центр)")
    p.add_argument("--step", type=int, default=0,
                   help="шаг прокрутки, px (0 = высота области кадра)")
    p.add_argument("--crop", nargs=4, type=int, metavar=("X1", "Y1", "X2", "Y2"),
                   help="обрезать кадр до этой области")
    p.add_argument("--pause", type=float, default=0.8)
    p.add_argument("--max", type=int, default=200, help="лимит кадров")
    args = p.parse_args()

    d = attach(args.port)
    print(f"Страница: {d.title}")

    vw = d.execute_script("return window.innerWidth;")
    vh = d.execute_script("return window.innerHeight;")
    dpr = d.execute_script("return window.devicePixelRatio;") or 1

    cx = args.x if args.x is not None else vw // 2
    cy = args.y if args.y is not None else vh // 2

    box = args.crop if args.crop else (0, 0, vw, vh)
    box_h = box[3] - box[1]
    step = args.step or box_h
    print(f"Точка прокрутки: ({cx}, {cy}), шаг {step} px")

    shots = []
    prev = None

    for i in range(args.max):
        time.sleep(args.pause)
        img = Image.open(io.BytesIO(d.get_screenshot_as_png()))
        img = img.crop(tuple(int(v * dpr) for v in box))

        if prev is not None and not frames_differ(prev, img):
            print(f"  кадр {i + 1}: изменений нет — конец страницы")
            break

        shots.append(img)
        prev = img
        print(f"  кадр {i + 1} снят")
        wheel(d, cx, cy, step)

    if not shots:
        raise SystemExit("Не снято ни одного кадра")

    canvas = Image.new("RGB", (shots[0].width,
                               sum(s.height for s in shots)), "white")
    y = 0
    for s in shots:
        canvas.paste(s, (0, y))
        y += s.height
    canvas.save(args.output)
    print(f"Готово: {args.output} — {canvas.width}x{canvas.height} px, "
          f"{len(shots)} кадров")


if __name__ == "__main__":
    main()
