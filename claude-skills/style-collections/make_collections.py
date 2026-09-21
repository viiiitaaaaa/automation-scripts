# -*- coding: utf-8 -*-
"""
Раскладка вырезанных товаров магазина по коллекциям-стилям.

    python make_collections.py "<папка магазина>" "<файл разметки>"

Файл разметки — строки "<номер вырезки> <код стиля>", коды см. STYLES.
Каждый товар попадает ровно в одну коллекцию. Визуальные повторы
(один товар с разных страниц) отсеиваются в папку дублей.
"""
import os, sys, glob, shutil
import numpy as np
from PIL import Image

STYLES = {
    1:  "01 Warm Minimalism — тёплый минимализм",
    2:  "02 Organic Luxe — природная роскошь",
    3:  "03 Color Drenching — глубокий цвет",
    4:  "04 Heritage Maximalism — коллекционная классика",
    5:  "05 Modern Mediterranean — средиземноморский",
    6:  "06 Neo-Japandi — японди",
    7:  "07 Quiet Luxury 2.0 — тихая роскошь",
    8:  "08 Sculptural Contemporary — скульптурный",
    9:  "09 Dark Academia — тёмная библиотека",
    10: "10 Eclectic Collectors — эклектика коллекционера",
    0:  "00 Вне коллекций",
}
DUPES = "00 Повторы"
HAMMING_MAX = 10          # порог похожести для отсева повторов
HASH_SIDE = 16            # aHash 16x16 = 256 бит


def ahash(path):
    im = Image.open(path).convert("L").resize((HASH_SIDE, HASH_SIDE))
    a = np.asarray(im, dtype=np.float32)
    return (a > a.mean()).flatten()


def main(shop, labels_path):
    shop = os.path.abspath(shop)
    name = os.path.basename(shop.rstrip("\\/"))

    labels = {}
    for line in open(labels_path, encoding="utf-8-sig"):
        parts = line.split()
        if len(parts) == 2 and parts[0].isdigit():
            labels[int(parts[0])] = int(parts[1])

    files = {}
    for f in glob.glob(os.path.join(shop, "*.png")):
        tail = os.path.basename(f)[:-4].rsplit("-", 1)[-1]
        if tail.isdigit():
            files[int(tail)] = f
    print("вырезок: %d, размечено: %d" % (len(files), len(labels)))

    nums = sorted(files)
    hashes = np.array([ahash(files[n]) for n in nums])

    # повторы: сравниваем каждую картинку с уже принятыми
    keep, dupe_of = [], {}
    for i, n in enumerate(nums):
        dup = None
        for j in keep:
            if np.count_nonzero(hashes[i] != hashes[j]) <= HAMMING_MAX:
                dup = nums[j]
                break
        if dup is None:
            keep.append(i)
        else:
            dupe_of[n] = dup
    print("уникальных: %d, повторов: %d" % (len(keep), len(dupe_of)))

    for folder in list(STYLES.values()) + [DUPES]:
        os.makedirs(os.path.join(shop, folder), exist_ok=True)

    counts = {k: 0 for k in STYLES}
    for n in nums:
        src = files[n]
        if n in dupe_of:
            dst = os.path.join(shop, DUPES,
                               "%s — повтор %03d (как %03d).png" % (name, n, dupe_of[n]))
            shutil.copy2(src, dst)
            continue
        code = labels.get(n, 0)
        counts[code] += 1
        folder = STYLES[code]
        style = folder.split("—")[0].strip()
        dst = os.path.join(shop, folder, "%s — %s — %03d.png" % (name, style, counts[code]))
        shutil.copy2(src, dst)

    print("\nКоллекции:")
    total = 0
    for code in sorted(STYLES):
        if code == 0:
            continue
        print("  %-50s %4d" % (STYLES[code], counts[code]))
        total += counts[code]
    print("  %-50s %4d" % (STYLES[0], counts[0]))
    print("  %-50s %4d" % (DUPES, len(dupe_of)))
    print("\nв коллекциях всего: %d" % total)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
