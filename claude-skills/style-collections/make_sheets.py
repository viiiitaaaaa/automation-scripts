# -*- coding: utf-8 -*-
"""
Контактные листы с номерами — для ручной классификации вырезок по стилям.

    python make_sheets.py "<папка магазина>" "<папка для листов>" [размер пачки]

Делает overview.png (обзор ассортимента, 100 картинок через равные промежутки)
и batch_XXXX_YYYY.png — пачки по 60 штук, 10 в ряд, с номером вырезки на каждой.
Номер на тайле = номер файла, его и пишешь в разметку.
"""
import os, sys, glob
from PIL import Image, ImageDraw


def cuts(shop):
    fs = [f for f in glob.glob(os.path.join(shop, "*.png"))
          if os.path.basename(f)[:-4].rsplit("-", 1)[-1].isdigit()]
    return sorted(fs, key=lambda f: int(os.path.basename(f)[:-4].rsplit("-", 1)[-1]))


def sheet(files, out, cols, tile):
    rows = (len(files) + cols - 1) // cols
    im = Image.new("RGB", (cols * tile, rows * tile), "white")
    d = ImageDraw.Draw(im)
    for i, f in enumerate(files):
        x, y = (i % cols) * tile, (i // cols) * tile
        im.paste(Image.open(f).convert("RGB").resize((tile, tile)), (x, y))
        lab = os.path.basename(f)[:-4].rsplit("-", 1)[-1]
        d.rectangle([x, y, x + 8 * len(lab) + 6, y + 18], fill="black")
        d.text((x + 3, y + 4), lab, fill="yellow")
    im.save(out)


def main(shop, outdir, batch=60):
    os.makedirs(outdir, exist_ok=True)
    fs = cuts(shop)
    print("вырезок:", len(fs))
    step = max(1, len(fs) // 100)
    sheet(fs[::step][:100], os.path.join(outdir, "overview.png"), 10, 165)
    for a in range(0, len(fs), batch):
        b = min(a + batch, len(fs))
        sheet(fs[a:b], os.path.join(outdir, "batch_%04d_%04d.png" % (a, b)), 10, 175)
    print("листов:", (len(fs) + batch - 1) // batch)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 60)
