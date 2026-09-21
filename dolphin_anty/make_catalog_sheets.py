# -*- coding: utf-8 -*-
"""Листы каталога: фото товаров с номерами и подписями.

Берёт то, что реально стоит на витрине (активные и опубликованные), скачивает
главные фото и раскладывает по 20 штук на лист. Под каждым фото - номер и
название, чтобы можно было просто назвать номера нужных товаров.

    py -3.13 make_catalog_sheets.py
"""
import io
import sys
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, r"C:\Users\User\dolphin_anty")
from shop_api import gql                                     # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(r"C:\Users\User\Desktop\КАТАЛОГ по номерам")
СПИСОК = OUT / "список товаров.txt"
КОЛ, РЯД = 5, 4                  # 5 в ряд, 4 ряда = 20 товаров на листе
ЯЧЕЙКА = 360                     # размер фото
ПОДПИСЬ = 74                     # место под номер и название
ПОЛЕ = 30


def шрифт(размер, жирный=False):
    имена = ["segoeuib.ttf", "arialbd.ttf"] if жирный else ["segoeui.ttf", "arial.ttf"]
    for имя in имена:
        try:
            return ImageFont.truetype(имя, размер)
        except Exception:
            pass
    return ImageFont.load_default()


def перенос(d, текст, ft, ширина, строк=2):
    слова, строки, стр = текст.split(), [], ""
    for w in слова:
        проба = (стр + " " + w).strip()
        if d.textlength(проба, font=ft) <= ширина:
            стр = проба
        else:
            строки.append(стр)
            стр = w
            if len(строки) == строк:
                break
    if стр and len(строки) < строк:
        строки.append(стр)
    if len(строки) == строк and слова:
        while строки and d.textlength(строки[-1] + "…", font=ft) > ширина:
            строки[-1] = строки[-1][:-1]
        if len(" ".join(строки)) < len(текст):
            строки[-1] += "…"
    return строки


def товары():
    """Только то, что покупатель видит на витрине."""
    q = """query($c:String){products(first:100,after:$c,query:"status:active"){
      pageInfo{hasNextPage endCursor}
      nodes{ title handle publishedOnCurrentPublication
             featuredMedia{ preview{ image{ url(transform:{maxWidth:600}) } } } }}}"""
    out, cur = [], None
    while True:
        d = gql(q, {"c": cur})
        b = d["data"]["products"]
        for p in b["nodes"]:
            if not p.get("publishedOnCurrentPublication"):
                continue
            url = (((p.get("featuredMedia") or {}).get("preview") or {})
                   .get("image") or {}).get("url")
            out.append((p["title"], p["handle"], url))
        if not b["pageInfo"]["hasNextPage"]:
            break
        cur = b["pageInfo"]["endCursor"]
    out.sort(key=lambda x: x[0].lower())
    return out


def качать(url):
    if not url:
        return None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            im = Image.open(io.BytesIO(r.read())).convert("RGB")
        im.thumbnail((ЯЧЕЙКА, ЯЧЕЙКА))
        холст = Image.new("RGB", (ЯЧЕЙКА, ЯЧЕЙКА), (245, 243, 239))
        холст.paste(im, ((ЯЧЕЙКА - im.width) // 2, (ЯЧЕЙКА - im.height) // 2))
        return холст
    except Exception:
        return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    список = товары()
    print("товаров на витрине: %d" % len(список), flush=True)

    ft_num = шрифт(26, жирный=True)
    ft_txt = шрифт(19)
    ft_head = шрифт(30, жирный=True)

    на_листе = КОЛ * РЯД
    листов = (len(список) + на_листе - 1) // на_листе
    строки_файла = []

    for л in range(листов):
        часть = список[л * на_листе:(л + 1) * на_листе]
        W = ПОЛЕ * 2 + КОЛ * ЯЧЕЙКА + (КОЛ - 1) * 18
        H = ПОЛЕ * 2 + 60 + РЯД * (ЯЧЕЙКА + ПОДПИСЬ) + (РЯД - 1) * 18
        лист = Image.new("RGB", (W, H), (252, 251, 249))
        d = ImageDraw.Draw(лист)
        d.text((ПОЛЕ, ПОЛЕ - 4),
               "ARTMELLIO — каталог, лист %d из %d   (товары %d–%d)"
               % (л + 1, листов, л * на_листе + 1, л * на_листе + len(часть)),
               font=ft_head, fill=(30, 30, 30))

        for i, (title, handle, url) in enumerate(часть):
            номер = л * на_листе + i + 1
            кx = ПОЛЕ + (i % КОЛ) * (ЯЧЕЙКА + 18)
            кy = ПОЛЕ + 60 + (i // КОЛ) * (ЯЧЕЙКА + ПОДПИСЬ + 18)
            фото = качать(url)
            if фото:
                лист.paste(фото, (кx, кy))
            else:
                d.rectangle([кx, кy, кx + ЯЧЕЙКА, кy + ЯЧЕЙКА], fill=(238, 236, 232))
                d.text((кx + 12, кy + ЯЧЕЙКА // 2), "нет фото", font=ft_txt,
                       fill=(150, 150, 150))
            # номер крупно, чтобы можно было просто назвать его
            d.rectangle([кx, кy + ЯЧЕЙКА, кx + 54, кy + ЯЧЕЙКА + 34], fill=(28, 28, 28))
            d.text((кx + 10, кy + ЯЧЕЙКА + 4), str(номер), font=ft_num, fill=(255, 255, 255))
            for j, стр in enumerate(перенос(d, title, ft_txt, ЯЧЕЙКА - 62)):
                d.text((кx + 62, кy + ЯЧЕЙКА + 2 + j * 22), стр, font=ft_txt,
                       fill=(40, 40, 40))
            строки_файла.append("%d\t%s\t%s" % (номер, title, handle))

        путь = OUT / ("лист %02d.png" % (л + 1))
        лист.save(путь)
        print("   %s — товаров %d" % (путь.name, len(часть)), flush=True)

    СПИСОК.write_text("\n".join(строки_файла), encoding="utf-8")
    print("\nГОТОВО: листов %d, товаров %d" % (листов, len(список)), flush=True)
    print("Папка: %s" % OUT, flush=True)


if __name__ == "__main__":
    main()
