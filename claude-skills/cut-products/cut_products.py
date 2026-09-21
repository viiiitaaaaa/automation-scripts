# -*- coding: utf-8 -*-
"""
Нарезка фото товаров из полностраничных скринов магазина AliExpress.

Запуск:
    python cut_products.py "C:\\Users\\User\\Desktop\\скрины магазинов\\SANTAYA Official Store"

Если папку не указать — берётся папка, из которой запущен скрипт.
Вырезанные картинки кладутся в ту же папку и называются по имени папки (= имя магазина):
    SANTAYA Official Store -001.png, -002.png, ...

Как работает: карточки товаров лежат в ровной сетке. Скрипт сам находит колонки
(по горизонтальному профилю не-белых пикселей) и ряды фото (по вертикальному),
берёт только квадратные блоки фото — шапка, футер, текст и цены отбрасываются.
"""
import sys
import os
import glob
import numpy as np
from PIL import Image

# --- настройки -------------------------------------------------------------
WHITE_LEVEL = 240      # пиксель считается "белым", если все каналы >= этого
ROW_FILL = 0.35        # какая доля строки должна быть не-белой, чтобы это был ряд фото
MIN_SIDE = 250         # минимальная сторона фото, px
SQUARE_TOL = 0.12      # допуск на "квадратность" блока фото
CELL_MIN_INK = 0.12    # если в ячейке меньше — считаем её пустой и пропускаем
SKIP_DUPLICATES = True # не сохранять повторы (страницы часто перекрываются)
SUFFIX = "-"           # разделитель перед номером в имени файла
# ---------------------------------------------------------------------------


def find_columns(nonwhite):
    """Границы колонок сетки: берём строку-медиану профиля по всей странице."""
    colprof = nonwhite.mean(axis=0)
    # порог адаптивный: колонки заполнены заметно плотнее, чем зазоры между ними
    # (в зазоры попадают только сплошные шапка и футер)
    thr = max(0.25, 0.45 * colprof.max())
    filled = colprof > thr
    segs, start = [], None
    for x, f in enumerate(filled):
        if f and start is None:
            start = x
        elif not f and start is not None:
            segs.append((start, x - 1))
            start = None
    if start is not None:
        segs.append((start, len(filled) - 1))
    return [s for s in segs if s[1] - s[0] + 1 >= MIN_SIDE]


def find_rows(nonwhite, cols):
    """Ряды фото: полосы, где колонки заполнены картинкой."""
    prof = np.zeros(nonwhite.shape[0])
    for x0, x1 in cols:
        prof += nonwhite[:, x0:x1 + 1].mean(axis=1)
    prof /= max(len(cols), 1)
    mask = prof > ROW_FILL
    segs, start = [], None
    for y, m in enumerate(mask):
        if m and start is None:
            start = y
        elif not m and start is not None:
            segs.append((start, y - 1))
            start = None
    if start is not None:
        segs.append((start, len(mask) - 1))
    return segs


def process_folder(folder):
    folder = os.path.abspath(folder)
    shop = os.path.basename(folder.rstrip("\\/"))
    out_prefix = shop + SUFFIX

    sources = []
    for p in sorted(glob.glob(os.path.join(folder, "*.png")) +
                    glob.glob(os.path.join(folder, "*.jpg")) +
                    glob.glob(os.path.join(folder, "*.jpeg"))):
        name = os.path.basename(p)
        if name.startswith(out_prefix):      # это уже наша вырезка
            continue
        sources.append(p)

    # страницы по порядку: "... страница 2" раньше "... страница 10"
    def page_key(p):
        digits = "".join(ch if ch.isdigit() else " " for ch in os.path.basename(p)).split()
        return (int(digits[-1]) if digits else 0, p)
    sources.sort(key=page_key)

    if not sources:
        print("В папке нет исходных скринов:", folder)
        return

    print("Магазин:", shop)
    print("Скринов на входе:", len(sources))

    seen = set()
    n = 0
    for path in sources:
        im = Image.open(path).convert("RGB")
        a = np.asarray(im)
        nonwhite = a.min(axis=2) < WHITE_LEVEL

        cols = find_columns(nonwhite)
        if not cols:
            print("  ! сетка не найдена:", os.path.basename(path))
            continue
        width = int(np.median([x1 - x0 + 1 for x0, x1 in cols]))

        saved_here = 0
        for y0, y1 in find_rows(nonwhite, cols):
            h = y1 - y0 + 1
            # берём только квадратные полосы = ряды фото (не шапка/футер/текст)
            if abs(h - width) / width > SQUARE_TOL:
                continue
            for x0, x1 in cols:
                cell = nonwhite[y0:y1 + 1, x0:x1 + 1]
                if cell.mean() < CELL_MIN_INK:      # пустая ячейка
                    continue
                crop = im.crop((x0, y0, x1 + 1, y1 + 1))
                if SKIP_DUPLICATES:
                    sig = crop.resize((16, 16)).convert("L").tobytes()
                    if sig in seen:
                        continue
                    seen.add(sig)
                n += 1
                saved_here += 1
                crop.save(os.path.join(folder, "%s%03d.png" % (out_prefix, n)))
        print("  %s -> %d шт." % (os.path.basename(path), saved_here))

    print("Готово. Всего вырезано:", n)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    target = os.path.abspath(target)
    # если в папке нет скринов, но есть подпапки магазинов — обходим их все
    has_shots = bool(glob.glob(os.path.join(target, "*.png")) +
                     glob.glob(os.path.join(target, "*.jpg")) +
                     glob.glob(os.path.join(target, "*.jpeg")))
    subdirs = sorted(d for d in glob.glob(os.path.join(target, "*")) if os.path.isdir(d))
    if not has_shots and subdirs:
        for d in subdirs:
            process_folder(d)
            print("-" * 60)
    else:
        process_folder(target)
