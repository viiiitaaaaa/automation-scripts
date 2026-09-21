#!/usr/bin/env python3
"""
Скриншот виртуальной таблицы Ant Design — v2.

Исправлено:
  * окно подводится так, чтобы контейнер целиком влез в экран
  * кадр обрезается строго по видимой области (нет чёрных полос)
  * шаг прокрутки = реально видимая высота, а не clientHeight
  * досъёмка хвоста, когда scrollTop упёрся в максимум

    python wb_table_shot2.py prices.png
    python wb_table_shot2.py prices.png --overlap 40 --pause 1.5
    python wb_table_shot2.py prices.png --keep-parts
"""

import argparse
import io
import os
import time

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

SELECTOR = "div.ant-table-tbody-virtual-holder"

JS_PREP = """
const el = document.querySelector(arguments[0]);
if (!el) return {found: false};

if (!document.getElementById('__shot_style')) {
    const s = document.createElement('style');
    s.id = '__shot_style';
    s.textContent = `*,*::before,*::after{animation-duration:0s!important;
        transition-duration:0s!important;} html{scroll-behavior:auto!important;}`;
    document.head.appendChild(s);
}

el.scrollTop = 0;

// Подводим окно так, чтобы низ контейнера влез в экран.
// Сначала наверх, чтобы померить исходное положение.
window.scrollTo(0, 0);
let r = el.getBoundingClientRect();
const overflowBottom = r.bottom - window.innerHeight;
if (overflowBottom > 0) {
    window.scrollTo(0, Math.min(overflowBottom + 2,
        document.documentElement.scrollHeight - window.innerHeight));
}
r = el.getBoundingClientRect();

// Видимая часть контейнера после подводки
const visTop = Math.max(r.top, 0);
const visBottom = Math.min(r.bottom, window.innerHeight);

return {
    found: true,
    winScroll: window.pageYOffset,
    left: r.left, right: r.right,
    visTop: visTop, visBottom: visBottom,
    visible: visBottom - visTop,
    client: el.clientHeight,
    scroll: el.scrollHeight,
    fullyVisible: (visBottom - visTop) >= el.clientHeight - 2
};
"""

JS_SCROLL = """
const el = document.querySelector(arguments[0]);
window.scrollTo(0, arguments[2]);      // держим окно на месте
el.scrollTop = arguments[1];
return {top: el.scrollTop, max: el.scrollHeight - el.clientHeight,
        scroll: el.scrollHeight};
"""


def attach(port):
    o = Options()
    o.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    return webdriver.Chrome(options=o)


def grab(driver, box, dpr):
    """Снимок с обрезкой строго внутри границ картинки."""
    img = Image.open(io.BytesIO(driver.get_screenshot_as_png()))
    x1 = max(0, int(box[0] * dpr))
    y1 = max(0, int(box[1] * dpr))
    x2 = min(img.width, int(box[2] * dpr))
    y2 = min(img.height, int(box[3] * dpr))
    return img.crop((x1, y1, x2, y2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output", nargs="?", default="table.png")
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--selector", default=SELECTOR)
    ap.add_argument("--pause", type=float, default=1.0)
    ap.add_argument("--overlap", type=int, default=0,
                    help="нахлёст в px — страховка от срезанных строк")
    ap.add_argument("--keep-parts", action="store_true")
    ap.add_argument("--max", type=int, default=200)
    args = ap.parse_args()

    d = attach(args.port)
    print(f"Страница: {d.title}")

    info = d.execute_script(JS_PREP, args.selector)
    if not info["found"]:
        raise SystemExit(f"Элемент {args.selector} не найден")

    dpr = d.execute_script("return window.devicePixelRatio;") or 1
    win_y = info["winScroll"]
    visible = int(info["visible"])
    client = int(info["client"])
    total = int(info["scroll"])

    box = (info["left"], info["visTop"], info["right"], info["visBottom"])

    print(f"Окно подведено на {int(win_y)} px")
    print(f"Контейнер: clientHeight {client}, видно {visible} px"
          f"{' (целиком)' if info['fullyVisible'] else ' (ЧАСТИЧНО)'}")
    print(f"Содержимое: {total} px → примерно "
          f"{-(-total // max(1, visible - args.overlap))} кадров")

    if not info["fullyVisible"]:
        print("  ! Контейнер не влез в экран целиком. Кадры всё равно будут")
        print("  ! без чёрных полос, но снимков понадобится больше.")

    step = max(100, visible - args.overlap)

    if args.keep_parts:
        os.makedirs("parts", exist_ok=True)

    parts = []          # (изображение, позиция контента в px)
    content_pos = 0     # какая точка содержимого сейчас вверху кадра
    idx = 0
    max_top = None

    while idx < args.max:
        # scrollTop может быть не больше scrollHeight - clientHeight
        want_top = content_pos
        st = d.execute_script(JS_SCROLL, args.selector, want_top, win_y)
        real_top = st["top"]
        max_top = st["max"]
        total = max(total, int(st["scroll"]))

        # Если scrollTop упёрся, содержимое вверху кадра всё равно = real_top
        actual_pos = real_top
        time.sleep(args.pause)

        img = grab(d, box, dpr)

        if parts:
            prev_bottom = parts[-1][1] + visible
            over = prev_bottom - actual_pos
            if over > 0:
                cut = int(round(over * img.height / visible))
                if cut >= img.height:
                    print("  кадр полностью дублирует предыдущий — стоп")
                    break
                img = img.crop((0, cut, img.width, img.height))
            elif over < 0:
                print(f"  ! пропуск {-over} px — увеличьте --pause")

        parts.append((img, actual_pos))
        if args.keep_parts:
            img.save(os.path.join("parts", f"part_{idx:03d}.png"))
        idx += 1
        print(f"  кадр {idx}: позиция {int(actual_pos)} / {total}")

        # Дно достигнуто, когда низ кадра дошёл до конца содержимого
        if actual_pos + visible >= total - 1:
            print("  достигнут конец списка")
            break

        # Если scrollTop уже на максимуме, дальше двигаться некуда
        if real_top >= max_top - 1 and want_top >= max_top:
            remaining = total - (actual_pos + visible)
            if remaining > 1:
                print(f"  ! scrollTop на максимуме, но осталось {remaining} px")
                print(f"  ! нижняя часть контейнера вне экрана")
            break

        content_pos = actual_pos + step

    images = [p[0] for p in parts]
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
