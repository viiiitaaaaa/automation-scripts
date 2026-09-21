#!/usr/bin/env python3
"""
Полностраничный скриншот с пошаговой прокруткой.

Установка:
    pip install selenium pillow
    (Chrome должен быть установлен; Selenium 4.6+ сам скачает драйвер)

Использование:
    python fullpage_screenshot.py https://example.com out.png
    python fullpage_screenshot.py https://example.com out.png --mode cdp
    python fullpage_screenshot.py https://example.com out.png --keep-parts
"""

import argparse
import base64
import io
import os
import time

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# ---------------------------------------------------------------- driver

def make_driver(width: int, height: int, headless: bool = True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument(f"--window-size={width},{height}")
    opts.add_argument("--hide-scrollbars")
    opts.add_argument("--force-device-scale-factor=1")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=opts)
    driver.set_window_size(width, height)
    return driver


# ---------------------------------------------------------- подготовка

JS_PAGE_METRICS = """
return {
    scrollHeight: Math.max(
        document.body.scrollHeight, document.documentElement.scrollHeight,
        document.body.offsetHeight, document.documentElement.offsetHeight
    ),
    viewportHeight: window.innerHeight,
    viewportWidth: window.innerWidth,
    dpr: window.devicePixelRatio
};
"""

# Отключаем плавную прокрутку и анимации — иначе кадры «смазываются»
JS_DISABLE_ANIMATIONS = """
const style = document.createElement('style');
style.textContent = `
    *, *::before, *::after {
        animation-duration: 0s !important;
        animation-delay: 0s !important;
        transition-duration: 0s !important;
        transition-delay: 0s !important;
    }
    html { scroll-behavior: auto !important; }
`;
document.head.appendChild(style);
"""

# Прячем прилипшие шапки/футеры, чтобы они не дублировались на каждом куске
JS_HIDE_STICKY = """
window.__hidden = [];
document.querySelectorAll('*').forEach(el => {
    const pos = getComputedStyle(el).position;
    if (pos === 'fixed' || pos === 'sticky') {
        window.__hidden.push([el, el.style.visibility]);
        el.style.visibility = 'hidden';
    }
});
"""

JS_RESTORE_STICKY = """
(window.__hidden || []).forEach(([el, v]) => { el.style.visibility = v; });
window.__hidden = [];
"""


def scroll_to_bottom_and_back(driver, step_pause: float = 0.3):
    """Прогоняем страницу вниз, чтобы догрузился ленивый контент и картинки."""
    last_height = 0
    for _ in range(60):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(step_pause)
        height = driver.execute_script(
            "return document.documentElement.scrollHeight;")
        pos = driver.execute_script(
            "return window.pageYOffset + window.innerHeight;")
        if pos >= height and height == last_height:
            break
        last_height = height
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(step_pause * 2)


# --------------------------------------------------- режим 1: по кускам

def capture_by_scroll(driver, pause: float = 0.4, keep_parts: bool = False,
                      parts_dir: str = "parts"):
    """
    Скриним видимую область, скроллим ровно на её высоту, скриним снова.
    Последний кадр обрезаем сверху, чтобы не было повтора.
    """
    m = driver.execute_script(JS_PAGE_METRICS)
    total = m["scrollHeight"]
    viewport = m["viewportHeight"]
    dpr = m["dpr"] or 1

    if keep_parts:
        os.makedirs(parts_dir, exist_ok=True)

    driver.execute_script(JS_HIDE_STICKY)

    shots = []
    offset = 0
    index = 0

    while offset < total:
        driver.execute_script("window.scrollTo(0, arguments[0]);", offset)
        time.sleep(pause)

        # реальная позиция может отличаться от заданной (упёрлись в низ)
        real = driver.execute_script("return window.pageYOffset;")
        png = driver.get_screenshot_as_png()
        img = Image.open(io.BytesIO(png))

        if shots:
            prev_bottom = shots[-1][1] + viewport   # где кончился прошлый кадр
            overlap = prev_bottom - real            # нахлёст в CSS-пикселях
            if overlap > 0:
                crop_px = int(round(overlap * img.height / viewport))
                if crop_px >= img.height:
                    break
                img = img.crop((0, crop_px, img.width, img.height))

        shots.append((img, real))

        if keep_parts:
            img.save(os.path.join(parts_dir, f"part_{index:03d}.png"))
        index += 1

        if real + viewport >= total - 1:
            break
        offset = real + viewport

        # страница могла подрасти из-за подгрузки
        total = max(total, driver.execute_script(
            "return document.documentElement.scrollHeight;"))

    driver.execute_script(JS_RESTORE_STICKY)

    images = [s[0] for s in shots]
    width = max(i.width for i in images)
    height = sum(i.height for i in images)

    canvas = Image.new("RGB", (width, height), "white")
    y = 0
    for img in images:
        canvas.paste(img, (0, y))
        y += img.height
    return canvas, dpr


# ------------------------------------------------- режим 2: одним кадром

def capture_cdp(driver):
    """Полный скрин одним вызовом Chrome DevTools Protocol — без склейки."""
    m = driver.execute_script(JS_PAGE_METRICS)
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
        "width": m["viewportWidth"],
        "height": m["scrollHeight"],
        "deviceScaleFactor": m["dpr"],
        "mobile": False,
    })
    time.sleep(0.5)
    result = driver.execute_cdp_cmd("Page.captureScreenshot", {
        "captureBeyondViewport": True,
        "fromSurface": True,
    })
    driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
    return Image.open(io.BytesIO(base64.b64decode(result["data"])))


# ------------------------------------------------------------------ main

def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("output", nargs="?", default="fullpage.png")
    p.add_argument("--width", type=int, default=1440)
    p.add_argument("--height", type=int, default=900)
    p.add_argument("--pause", type=float, default=0.4,
                   help="пауза после каждой прокрутки, сек")
    p.add_argument("--mode", choices=["scroll", "cdp"], default="scroll")
    p.add_argument("--keep-parts", action="store_true",
                   help="сохранить отдельные куски в папку parts/")
    p.add_argument("--no-headless", action="store_true")
    args = p.parse_args()

    driver = make_driver(args.width, args.height,
                         headless=not args.no_headless)
    try:
        driver.get(args.url)
        time.sleep(2)
        driver.execute_script(JS_DISABLE_ANIMATIONS)
        scroll_to_bottom_and_back(driver)

        if args.mode == "cdp":
            image = capture_cdp(driver)
        else:
            image, _ = capture_by_scroll(
                driver, pause=args.pause, keep_parts=args.keep_parts)

        image.save(args.output)
        print(f"Готово: {args.output} — {image.width}x{image.height} px")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
