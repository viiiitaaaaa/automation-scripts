#!/usr/bin/env python3
"""
Скриншот виртуальной таблицы Ant Design (кабинет WB, таблица цен).

Chrome должен быть запущен с --remote-debugging-port=9222
и открыт на странице с таблицей.

    python wb_table_shot.py prices.png
    python wb_table_shot.py prices.png --pause 1.5      # медленный интернет
    python wb_table_shot.py prices.png --with-header    # захватить шапку таблицы
    python wb_table_shot.py prices.png --keep-parts
"""

import argparse
import io
import os
import time

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

SELECTOR = "div.ant-table-tbody-virtual-holder"
HEADER_SELECTOR = "div.ant-table-header, thead.ant-table-thead"

JS_PREP = """
const sel = arguments[0];
const el = document.querySelector(sel);
if (!el) return {found: false};

// гасим анимации, чтобы кадры не смазывались
if (!document.getElementById('__shot_style')) {
    const s = document.createElement('style');
    s.id = '__shot_style';
    s.textContent = `*,*::before,*::after{animation-duration:0s!important;
        transition-duration:0s!important;} html{scroll-behavior:auto!important;}`;
    document.head.appendChild(s);
}

// окно наверх, иначе контейнер уедет посреди съёмки
window.scrollTo(0, 0);
el.scrollTop = 0;

const r = el.getBoundingClientRect();
return {
    found: true,
    x: r.x, y: r.y, w: r.width, h: r.height,
    client: el.clientHeight,
    scroll: el.scrollHeight
};
"""

JS_HEADER_BOX = """
const el = document.querySelector(arguments[0]);
if (!el) return null;
const r = el.getBoundingClientRect();
return {x: r.x, y: r.y, w: r.width, h: r.height};
"""

JS_SCROLL = """
const el = document.querySelector(arguments[0]);
el.scrollTop = arguments[1];
return el.scrollTop;
"""

JS_HEIGHT = """
const el = document.querySelector(arguments[0]);
return {scroll: el.scrollHeight, top: el.scrollTop};
"""


def attach(port):
    o = Options()
    o.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    return webdriver.Chrome(options=o)


def shot(driver, box, dpr):
    img = Image.open(io.BytesIO(driver.get_screenshot_as_png()))
    return img.crop((int(box[0] * dpr), int(box[1] * dpr),
                     int(box[2] * dpr), int(box[3] * dpr)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output", nargs="?", default="table.png")
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--selector", default=SELECTOR)
    ap.add_argument("--pause", type=float, default=1.0,
                    help="пауза после прокрутки — виртуальный список должен "
                         "успеть дорисовать строки")
    ap.add_argument("--overlap", type=int, default=0,
                    help="снимать с нахлёстом в N px (страховка от срезанных строк)")
    ap.add_argument("--with-header", action="store_true",
                    help="приклеить шапку таблицы сверху")
    ap.add_argument("--keep-parts", action="store_true")
    ap.add_argument("--max", type=int, default=100)
    args = ap.parse_args()

    d = attach(args.port)
    print(f"Страница: {d.title}")

    info = d.execute_script(JS_PREP, args.selector)
    if not info["found"]:
        raise SystemExit(f"Элемент {args.selector} не найден. "
                         f"Таблица прогрузилась?")

    dpr = d.execute_script("return window.devicePixelRatio;") or 1
    view = int(info["client"])
    total = int(info["scroll"])
    step = max(100, view - args.overlap)

    box = (info["x"], info["y"], info["x"] + info["w"], info["y"] + info["h"])
    print(f"Контейнер: видно {view} px, всего {total} px "
          f"→ примерно {-(-total // step)} кадров")

    header = None
    if args.with_header:
        hb = d.execute_script(JS_HEADER_BOX, HEADER_SELECTOR)
        if hb:
            time.sleep(0.3)
            header = shot(d, (hb["x"], hb["y"],
                              hb["x"] + hb["w"], hb["y"] + hb["h"]), dpr)
            print(f"Шапка захвачена: {header.width}x{header.height}")
        else:
            print("Шапка не найдена, пропускаю")

    if args.keep_parts:
        os.makedirs("parts", exist_ok=True)

    parts = []
    offset = 0
    idx = 0
    stuck = 0

    while idx < args.max:
        real = d.execute_script(JS_SCROLL, args.selector, offset)
        time.sleep(args.pause)

        img = shot(d, box, dpr)

        # обрезаем нахлёст относительно фактической позиции
        if parts:
            over = parts[-1][1] + view - real
            if over > 0:
                cut = int(round(over * img.height / view))
                if cut >= img.height:
                    break
                img = img.crop((0, cut, img.width, img.height))

        parts.append((img, real))
        if args.keep_parts:
            img.save(os.path.join("parts", f"part_{idx:03d}.png"))
        idx += 1
        print(f"  кадр {idx}: позиция {int(real)} / {total}")

        state = d.execute_script(JS_HEIGHT, args.selector)
        total = max(total, int(state["scroll"]))

        if len(parts) > 1 and real == parts[-2][1]:
            stuck += 1
            if stuck >= 2:
                print("  прокрутка встала — останавливаюсь")
                break
        else:
            stuck = 0

        if real + view >= total - 1:
            print("  достигнут низ списка")
            break
        offset = real + step

    images = ([header] if header else []) + [p[0] for p in parts]
    width = max(i.width for i in images)
    canvas = Image.new("RGB", (width, sum(i.height for i in images)), "white")
    y = 0
    for i in images:
        canvas.paste(i, (0, y))
        y += i.height
    canvas.save(args.output)
    print(f"Готово: {args.output} — {canvas.width}x{canvas.height} px, "
          f"{len(parts)} кадров")


if __name__ == "__main__":
    main()
