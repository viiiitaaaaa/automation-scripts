"""Снимок всей выдачи Pinduoduo одной картинкой: pdd_items.json (собран со страницы) -> сетка карточек PNG.
Фото качаются напрямую с pddpic; для img-4.pddpic.com — быстрый адрес 14.0.37.180 (второй адрес отдаёт по 25 с)."""
import io, json, os, socket, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont

SRC = sys.argv[1] if len(sys.argv) > 1 else 'pdd_items.json'
DST = sys.argv[2] if len(sys.argv) > 2 else r'C:\Users\User\Desktop\pdd_vydacha_polnaya.png'
COLS, W, PAD = 4, 360, 14
FONT = r'C:\Windows\Fonts\msyh.ttc'

_orig = socket.getaddrinfo
FAST = {'img-4.pddpic.com': '14.0.37.180'}
socket.getaddrinfo = lambda host, *a, **k: _orig(FAST.get(host, host), *a, **k)

items = json.load(open(SRC, encoding='utf8'))
os.makedirs('img', exist_ok=True)


def get(it):
    p = f"img/{it['n']}.jpg"
    if not os.path.exists(p) and it['img']:
        u = it['img'].replace('format/webp', 'format/jpg')
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://mobile.pinduoduo.com/'})
            Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=30).read())).convert('RGB').save(p, quality=90)
        except Exception as e:
            print('нет фото', it['n'], e)
            return None
    return p if os.path.exists(p) else None


with ThreadPoolExecutor(6) as ex:
    paths = list(ex.map(get, items))

f_t = ImageFont.truetype(FONT, 17)
f_p = ImageFont.truetype(FONT, 26)
f_s = ImageFont.truetype(FONT, 15)
f_n = ImageFont.truetype(FONT, 15)


def wrap(d, text, font, width, lines=2):
    out, cur = [], ''
    for ch in text:
        if d.textlength(cur + ch, font=font) > width:
            out.append(cur)
            cur = ch
            if len(out) == lines:
                break
        else:
            cur += ch
    else:
        out.append(cur)
    if len(out) == lines and ''.join(out) != text:
        out[-1] = out[-1][:-1] + '…'
    return out[:lines]


CARD_H = W + 130
rows = (len(items) + COLS - 1) // COLS
sheet = Image.new('RGB', (COLS * (W + PAD) + PAD, rows * (CARD_H + PAD) + PAD), (244, 244, 244))
d = ImageDraw.Draw(sheet)
for i, (it, p) in enumerate(zip(items, paths)):
    x, y = PAD + (i % COLS) * (W + PAD), PAD + (i // COLS) * (CARD_H + PAD)
    d.rectangle([x, y, x + W, y + CARD_H], fill='white')
    if p:
        im = Image.open(p)
        im.thumbnail((W, W))
        sheet.paste(im, (x + (W - im.width) // 2, y + (W - im.height) // 2))
    else:
        d.text((x + 20, y + W // 2), 'фото не загрузилось', font=f_s, fill=(150, 150, 150))
    d.rectangle([x, y, x + 34, y + 22], fill=(0, 0, 0))
    d.text((x + 4, y + 2), str(it['n']), font=f_n, fill='white')
    ty = y + W + 6
    for line in wrap(d, it['title'], f_t, W - 16):
        d.text((x + 8, ty), line, font=f_t, fill=(30, 30, 30))
        ty += 23
    price = f"¥{it['price']:g}" if it['price'] else ''
    d.text((x + 8, ty + 4), price, font=f_p, fill=(224, 46, 36))
    d.text((x + 16 + d.textlength(price, font=f_p), ty + 13), it['sales'], font=f_s, fill=(130, 130, 130))
    if it.get('tags'):
        d.text((x + 8, ty + 42), it['tags'][:40], font=f_s, fill=(160, 120, 60))
sheet.save(DST, optimize=True)
print(len(items), 'товаров,', sum(1 for p in paths if p), 'с фото ->', DST, sheet.size)
