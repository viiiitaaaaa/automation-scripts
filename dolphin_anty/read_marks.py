# -*- coding: utf-8 -*-
"""Прочитать товары, отмеченные фиолетовой галочкой на скринах каталога.

Пользователь отмечает нужные товары прямо на скринах и сохраняет файлы.
Скрипт находит метки по цвету, сопоставляет их координаты с карточками
товаров на той же странице и выдаёт список handle'ов.

    py -3.13 read_marks.py                 показать найденное
    py -3.13 read_marks.py --tag style:dark-academia   и проставить тег
"""
import re
import sys
import time
from pathlib import Path

from PIL import Image
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

PROFILE = 836461485
SHOTS = Path(r"C:\Users\User\Desktop\скрины artmellio")
BASE = "https://www.artmellio.com/collections/all"
ТЕГ = None
if "--tag" in sys.argv:
    ТЕГ = sys.argv[sys.argv.index("--tag") + 1]


def метки(путь):
    """Центры фиолетовых пятен на картинке."""
    im = Image.open(путь).convert("RGB")
    w, h = im.size
    px = im.load()
    точки = []
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b = px[x, y]
            if b > 100 and r > 70 and g + 30 < b and g + 20 < r:
                точки.append((x, y))
    # склеиваем соседние пиксели в пятна
    пятна = []
    for x, y in точки:
        for п in пятна:
            if abs(п["x"] - x) < 60 and abs(п["y"] - y) < 60:
                п["xs"].append(x)
                п["ys"].append(y)
                п["x"] = sum(п["xs"]) // len(п["xs"])
                п["y"] = sum(п["ys"]) // len(п["ys"])
                break
        else:
            пятна.append({"x": x, "y": y, "xs": [x], "ys": [y]})
    # мелкий шум отбрасываем: галочка - это десятки пикселей
    return [(п["x"], п["y"], len(п["xs"])) for п in пятна if len(п["xs"]) >= 8]


def main():
    файлы = sorted(SHOTS.glob("*.png"),
                   key=lambda p: int(re.sub(r"\D", "", p.name) or 0))
    страницы = {}
    for f in файлы:
        м = метки(f)
        if м:
            страницы[int(re.sub(r"\D", "", f.name))] = м
    print("страниц с отметками: %d" % len(страницы))
    if not страницы:
        return

    api = DolphinLocal(port=DolphinLocal.discover() or 3001)
    auto = start_with_retry(api, PROFILE)["automation"]
    найдено = []

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(
            "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
        ctx = b.contexts[0] if b.contexts else b.new_context()
        pg = ctx.new_page()
        pg.set_viewport_size({"width": 1600, "height": 1000})

        for n in sorted(страницы):
            pg.goto("%s?page=%d" % (BASE, n), wait_until="domcontentloaded", timeout=90_000)
            pg.bring_to_front()
            for _ in range(20):
                time.sleep(1.2)
                if pg.evaluate("() => document.querySelectorAll(\"a[href*='/products/']\").length"):
                    break
            # рамки карточек в тех же координатах, что и на скрине
            карточки = pg.evaluate("""() => {
              const out = [];
              for (const c of document.querySelectorAll('.card-wrapper, .grid__item')) {
                const a = c.querySelector("a[href*='/products/']");
                if (!a) continue;
                const r = c.getBoundingClientRect();
                out.push({h: a.getAttribute('href').split('?')[0].split('/products/')[1],
                          t: (c.innerText || '').split('\\n')[0].slice(0, 60),
                          x: r.x + window.scrollX, y: r.y + window.scrollY,
                          w: r.width, hh: r.height});
              }
              return out;
            }""")
            for x, y, вес in страницы[n]:
                подходят = [c for c in карточки
                            if c["x"] - 20 <= x <= c["x"] + c["w"] + 20
                            and c["y"] - 20 <= y <= c["y"] + c["hh"] + 20]
                if подходят:
                    c = подходят[0]
                    найдено.append((n, c["h"], c["t"]))
                else:
                    print("   стр.%d: метка (%d,%d) мимо карточек" % (n, x, y))
        pg.close()

    # убираем повторы: на одной карточке могло быть несколько пятен
    видели, итог = set(), []
    for n, h, t in найдено:
        if h in видели:
            continue
        видели.add(h)
        итог.append((n, h, t))

    print("\nОТМЕЧЕНО ТОВАРОВ: %d" % len(итог))
    for n, h, t in итог:
        print("   стр.%-3d %s" % (n, t or h))

    if not ТЕГ or not итог:
        print("\n(чтобы проставить тег: --tag style:dark-academia)")
        return

    from shop_api import gql
    q = "query($h:String!){productByIdentifier(identifier:{handle:$h}){id}}"
    m = "mutation($id:ID!,$t:[String!]!){tagsAdd(id:$id,tags:$t){userErrors{message}}}"
    ok = 0
    for n, h, t in итог:
        d = gql(q, {"h": h})
        p = (d.get("data") or {}).get("productByIdentifier")
        if not p:
            print("   [x] не нашёлся:", h[:40])
            continue
        r = gql(m, {"id": p["id"], "t": [ТЕГ]})
        if not r["data"]["tagsAdd"]["userErrors"]:
            ok += 1
    print("\n[ok] тег %s проставлен %d товарам" % (ТЕГ, ok))


if __name__ == "__main__":
    main()
