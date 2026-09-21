#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARTMELLIO — сборка Excel-каталога с ВШИТЫМИ картинками.

Что делает: берёт artmellio_catalog.csv (лежит рядом со скриптом),
скачивает картинку каждого товара с сайта и вставляет её прямо в ячейку Excel,
подписывая названием товара. Итог: artmellio_catalog_with_images.xlsx
Дополнительно все картинки сохраняются в папку images/ — файл называется по товару.

КАК ЗАПУСТИТЬ
  1) Установить Python 3 (python.org), если ещё нет.
  2) Положить этот скрипт и artmellio_catalog.csv в одну папку.
  3) В терминале / командной строке перейти в эту папку и выполнить:
         pip install openpyxl pillow requests
         python make_excel.py
     (на macOS/Linux может понадобиться python3 вместо python)
  4) Через 2-4 минуты рядом появится artmellio_catalog_with_images.xlsx
"""

import csv, os, re, sys, io, time

try:
    import requests
    from PIL import Image
    from openpyxl import Workbook
    from openpyxl.drawing.image import Image as XLImage
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
except ImportError as e:
    sys.exit("Не хватает библиотеки: %s\nВыполните:  pip install openpyxl pillow requests" % e.name)

HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "artmellio_catalog.csv")
IMG_DIR = os.path.join(HERE, "images")
OUT = os.path.join(HERE, "artmellio_catalog_with_images.xlsx")

THUMB = 120          # размер картинки в ячейке, px
SAVE_FULL = True     # сохранять также полноразмерные картинки в images/

if not os.path.exists(CSV_PATH):
    sys.exit("Не найден artmellio_catalog.csv рядом со скриптом.")
os.makedirs(IMG_DIR, exist_ok=True)

def safe_name(s):
    s = re.sub(r'[\\/:*?"<>|]+', "", s).strip().rstrip(".")
    return (s[:90] or "product")

with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
    rows = list(csv.DictReader(f))

print("Товаров в каталоге: %d" % len(rows))

wb = Workbook()
ws = wb.active
ws.title = "ARTMELLIO"

headers = ["№", "Картинка", "Название товара", "Цена", "Ссылка на товар"]
ws.append(headers)
hfill = PatternFill("solid", fgColor="1F2937")
for c in range(1, len(headers) + 1):
    cell = ws.cell(row=1, column=c)
    cell.fill = hfill
    cell.font = Font(color="FFFFFF", bold=True, size=11)
    cell.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 24

thin = Side(style="thin", color="D9D9D9")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0 (catalog-builder)"})

ok = fail = 0
for i, row in enumerate(rows, start=1):
    r = i + 1
    title = row["Название товара"]
    url = row["URL картинки"]

    ws.cell(row=r, column=1, value=i).alignment = Alignment(horizontal="center", vertical="center")
    c3 = ws.cell(row=r, column=3, value=title)
    c3.alignment = Alignment(vertical="center", wrap_text=True)
    ws.cell(row=r, column=4, value=row["Цена"]).alignment = Alignment(horizontal="center", vertical="center")
    c5 = ws.cell(row=r, column=5, value="открыть")
    c5.hyperlink = row["Ссылка на товар"]
    c5.font = Font(color="0563C1", underline="single")
    c5.alignment = Alignment(horizontal="center", vertical="center")
    for c in range(1, 6):
        ws.cell(row=r, column=c).border = border
    ws.row_dimensions[r].height = THUMB * 0.78

    try:
        resp = session.get(url, timeout=30)
        resp.raise_for_status()
        im = Image.open(io.BytesIO(resp.content)).convert("RGB")

        base = "%03d %s" % (i, safe_name(title))
        if SAVE_FULL:
            im.save(os.path.join(IMG_DIR, base + ".jpg"), "JPEG", quality=92)

        th = im.copy()
        th.thumbnail((THUMB, THUMB))
        buf = io.BytesIO()
        th.save(buf, "PNG")
        buf.seek(0)
        xi = XLImage(buf)
        xi.anchor = "B%d" % r
        ws.add_image(xi)
        ok += 1
    except Exception as e:
        ws.cell(row=r, column=2, value="нет картинки")
        fail += 1
        print("  ! %s — %s" % (title, e))

    if i % 25 == 0:
        print("  ...%d / %d" % (i, len(rows)))
    time.sleep(0.05)

for col, w in zip("ABCDE", [5, 19, 50, 12, 14]):
    ws.column_dimensions[col].width = w
ws.freeze_panes = "A2"
ws.auto_filter.ref = "A1:E%d" % (len(rows) + 1)
wb.save(OUT)

print("\nГотово: %s" % OUT)
print("Картинок вставлено: %d, не удалось: %d" % (ok, fail))
if SAVE_FULL:
    print("Полноразмерные картинки: %s" % IMG_DIR)
