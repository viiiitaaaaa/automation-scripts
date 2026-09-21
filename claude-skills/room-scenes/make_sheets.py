# Сборка листов товаров для QwenImageEditApi.
# Qwen принимает максимум 3 картинки: комната + два листа. Товары клеим в сетку с подписями,
# в промте адресуем по кодам (A1, B3...). Кропы обязательны - срезать логотипы,
# иероглифы, рекламный текст и вторые расцветки в том же кадре.
#
# Правка под задачу: SRC, OUT и списки items внизу файла.

from PIL import Image, ImageDraw, ImageFont
import os

SRC = r"C:\Users\User\Desktop\japandi_white\1"
OUT = r"C:\Users\User\AppData\Local\Temp\claude\scratchpad"


def load(name, box=None):
    """box=(left, top, right, bottom) - кроп в пикселях исходника."""
    im = Image.open(os.path.join(SRC, name)).convert("RGB")
    return im.crop(box) if box else im


def sheet(items, path, cols=3, cell=460, title_h=54):
    """items: список (подпись, Image). Подпись - код и короткое английское имя товара."""
    rows = (len(items) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * cell, rows * (cell + title_h)), (255, 255, 255))
    d = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arialbd.ttf", 30)
    except OSError:
        font = ImageFont.load_default()

    for i, (label, im) in enumerate(items):
        r, c = divmod(i, cols)
        x, y = c * cell, r * (cell + title_h)
        im = im.copy()
        im.thumbnail((cell - 16, cell - 16), Image.LANCZOS)
        canvas.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
        d.rectangle([x + 2, y + 2, x + cell - 2, y + cell - 2], outline=(210, 210, 210), width=2)
        d.text((x + 10, y + cell + 8), label, fill=(0, 0, 0), font=font)

    canvas.save(path)
    return canvas.size


if __name__ == "__main__":
    # Лист A - сантехника. Кропы: у ZGRK срезан логотип, у WJNMONE взята только чёрная
    # половина (в кадре рядом хромовая), у SailFlow срезан рекламный текст.
    a = [
        ("A1 black tall bamboo tap", load("ZGRK Official Store-143.png", (18, 18, 262, 386))),
        ("A2 black shower column",   load("WJNMONE Official Store-083.png", (196, 58, 386, 386))),
        ("A3 shower curtain",        load("SailFlow Store-106.png", (0, 0, 292, 416))),
    ]
    print("A", sheet(a, os.path.join(OUT, "sheetA.png")))

    # Лист B - декор.
    b = [
        ("B1 moss frame on stand",  load("Call black white and white black-015.png")),
        ("B2 travertine wall lamp", load("Plum Lighting Store-061.png", (198, 60, 400, 384))),
        ("B3 buddha halo lamp",     load("SailFlow Store-139.png", (58, 78, 362, 404))),
        ("B4 grey bath mat",        load("white_08.png")),
        ("B5 towel rack shelf",     load("white_13.png")),
        ("B6 wood radio",           load("60.png")),
    ]
    print("B", sheet(b, os.path.join(OUT, "sheetB.png")))
