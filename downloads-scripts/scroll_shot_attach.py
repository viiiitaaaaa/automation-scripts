#!/usr/bin/env python3
"""
Скриншот длинной таблицы на странице, требующей авторизации.
Подключается к уже запущенному Chrome, где вы вошли в аккаунт вручную.

ШАГ 1. Закройте ВСЕ окна Chrome, затем запустите в cmd:

    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" ^
        --remote-debugging-port=9222 ^
        --user-data-dir="C:\\chrome-debug"

ШАГ 2. В открывшемся Chrome войдите в кабинет и откройте нужную страницу.

ШАГ 3. Запустите скрипт (браузер не закрывайте):

    python scroll_shot_attach.py out.png
    python scroll_shot_attach.py out.png --keep-parts
    python scroll_shot_attach.py out.png --selector ".Table-scroll"
"""

import argparse
import io
import os
import time

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Ищем самый большой элемент на странице, который реально скроллится.
JS_FIND_SCROLLER = """
let best = null, bestArea = 0;
document.querySelectorAll('*').forEach(el => {
    const st = getComputedStyle(el);
    const scrollable = /(auto|scroll|overlay)/.test(st.overflowY);
    if (!scrollable) return;
    if (el.scrollHeight <= el.clientHeight + 50) return;
    const r = el.getBoundingClientRect();
    const area = r.width * r.height;
    if (area > bestArea) { bestArea = area; best = el; }
});
if (best) {
    best.setAttribute('data-shot-target', '1');
    const r = best.getBoundingClientRect();
    return {found: true, x: r.x, y: r.y, w: r.width, h: r.height,
            scrollHeight: best.scrollHeight, clientHeight: best.clientHeight};
}
return {found: false,
        scrollHeight: document.documentElement.scrollHeight,
        clientHeight: window.innerHeight,
        x: 0, y: 0, w: window.innerWidth, h: window.innerHeight};
"""

JS_MARK_SELECTOR = """
const el = document.querySelector(arguments[0]);
if (!el) return {found: false};
el.setAttribute('data-shot-target', '1');
const r = el.getBoundingClientRect();
return {found: true, x: r.x, y: r.y, w: r.width, h: r.height,
        scrollHeight: el.scrollHeight, clientHeight: el.clientHeight};
"""

JS_SCROLL_TO = """
const el = document.querySelector('[data-shot-target]');
if (el) { el.scrollTop = arguments[0]; return el.scrollTop; }
window.scrollTo(0, arguments[0]);
return window.pageYOffset;
"""

JS_GET_HEIGHT = """
const el = document.querySelector('[data-shot-target]');
return el ? el.scrollHeight : document.documentElement.scrollHeight;
"""

JS_DISABLE_ANIM = """
const s = document.createElement('style');
s.textContent = `*,*::before,*::after{animation-duration:0s!important;
transition-duration:0s!important;} html{scroll-behavior:auto!important;}`;
document.head.appendChild(s);
"""


def attach(port: int = 9222):
    opts = Options()
    opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    return webdriver.Chrome(options=opts)


def capture(driver, selector=None, pause=0.6, keep_parts=False,
            parts_dir="parts"):
    driver.execute_script(JS_DISABLE_ANIM)

    if selector:
        info = driver.execute_script(JS_MARK_SELECTOR, selector)
        if not info["found"]:
            raise SystemExit(f"Элемент '{selector}' не найден на странице")
    else:
        info = driver.execute_script(JS_FIND_SCROLLER)

    if info["found"]:
        print(f"Скроллим внутренний контейнер: "
              f"{int(info['w'])}x{int(info['h'])} px, "
              f"содержимое {int(info['scrollHeight'])} px")
    else:
        print("Внутренний скролл не найден, скроллим окно")

    dpr = driver.execute_script("return window.devicePixelRatio;") or 1
    step = int(info["clientHeight"])
    total = int(info["scrollHeight"])

    # Область обрезки кадра: только сам контейнер, без шапки и боковушки
    box = (int(info["x"]), int(info["y"]),
           int(info["x"] + info["w"]), int(info["y"] + info["h"]))

    if keep_parts:
        os.makedirs(parts_dir, exist_ok=True)

    shots = []
    offset = 0
    idx = 0

    while True:
        real = driver.execute_script(JS_SCROLL_TO, offset)
        time.sleep(pause)   # даём виртуальному списку дорисовать строки

        img = Image.open(io.BytesIO(driver.get_screenshot_as_png()))
        img = img.crop(tuple(int(v * dpr) for v in box))

        if shots:
            overlap = shots[-1][1] + step - real
            if overlap > 0:
                cut = int(round(overlap * img.height / step))
                if cut >= img.height:
                    break
                img = img.crop((0, cut, img.width, img.height))

        shots.append((img, real))
        if keep_parts:
            img.save(os.path.join(parts_dir, f"part_{idx:03d}.png"))
        idx += 1
        print(f"  кадр {idx}: позиция {int(real)} из {total}")

        total = max(total, driver.execute_script(JS_GET_HEIGHT))
        if real + step >= total - 1:
            break
        if real == shots[-2][1] if len(shots) > 1 else False:
            break   # скролл встал — выходим, чтобы не зациклиться
        offset = real + step

    images = [s[0] for s in shots]
    canvas = Image.new("RGB", (max(i.width for i in images),
                               sum(i.height for i in images)), "white")
    y = 0
    for img in images:
        canvas.paste(img, (0, y))
        y += img.height
    return canvas


def main():
    p = argparse.ArgumentParser()
    p.add_argument("output", nargs="?", default="fullpage.png")
    p.add_argument("--port", type=int, default=9222)
    p.add_argument("--selector", help="CSS-селектор скроллящегося контейнера")
    p.add_argument("--pause", type=float, default=0.6)
    p.add_argument("--keep-parts", action="store_true")
    args = p.parse_args()

    driver = attach(args.port)
    print(f"Подключились к: {driver.title}")
    image = capture(driver, selector=args.selector, pause=args.pause,
                    keep_parts=args.keep_parts)
    image.save(args.output)
    print(f"Готово: {args.output} — {image.width}x{image.height} px")
    # driver.quit() НЕ вызываем — иначе закроется ваш браузер


if __name__ == "__main__":
    main()
