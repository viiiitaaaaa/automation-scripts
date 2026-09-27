"""Копия katalog_1688_itog.xlsx, где фото товаров (столбец A) заменены на фото без фона.
Правка делается прямо в zip-архиве xlsx: всё остальное (графики, формулы, стили) не трогается."""
import io, re, sys, zipfile, os
from PIL import Image
from rembg import remove, new_session

SRC = 'katalog_1688_itog.xlsx'
DST = 'katalog_1688_itog_bez_fona.xlsx'
OUT_DIR = 'foto_bez_fona'
os.makedirs(OUT_DIR, exist_ok=True)

z = zipfile.ZipFile(SRC)
drawing = z.read('xl/drawings/drawing1.xml').decode('utf8')
rels = z.read('xl/drawings/_rels/drawing1.xml.rels').decode('utf8')
rid2t = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="\.\./media/([^"]+)"', rels))
photos = {}  # media name -> row
for col, row, rid in re.findall(r'<xdr:from><xdr:col>(\d+)</xdr:col>.*?<xdr:row>(\d+)</xdr:row>.*?r:embed="(rId\d+)"', drawing, re.S):
    if col == '0':
        photos[rid2t[rid]] = int(row) + 1

session = new_session('isnet-general-use')
new_media = {}  # old name -> (new name, png bytes)
for name, row in sorted(photos.items(), key=lambda x: x[1]):
    img = Image.open(io.BytesIO(z.read('xl/media/' + name))).convert('RGB')
    cut = remove(img, session=session, post_process_mask=True)
    bbox = cut.getchannel('A').getbbox()
    if bbox:
        cut = cut.crop(bbox)
    # квадрат с прозрачными полями, чтобы картинка не растянулась в ячейке
    s = max(cut.size); pad = int(s * 0.04); s += 2 * pad
    sq = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    sq.paste(cut, ((s - cut.width) // 2, (s - cut.height) // 2), cut)
    buf = io.BytesIO(); sq.save(buf, 'PNG', optimize=True)
    stem = name.rsplit('.', 1)[0]
    new_media[name] = (stem + '_nobg.png', buf.getvalue())
    sq.save(f'{OUT_DIR}/stroka_{row}.png')
    print('строка', row, name, '->', stem + '_nobg.png')

for old, (new, _) in new_media.items():
    rels = rels.replace('../media/' + old + '"', '../media/' + new + '"')

with zipfile.ZipFile(DST, 'w', zipfile.ZIP_DEFLATED) as out:
    for item in z.infolist():
        n = item.filename
        if n.startswith('xl/media/') and n[9:] in new_media:
            continue
        data = z.read(n)
        if n == 'xl/drawings/_rels/drawing1.xml.rels':
            data = rels.encode('utf8')
        elif n == '[Content_Types].xml':
            ct = data.decode('utf8')
            if 'Extension="png"' not in ct:
                ct = ct.replace('<Default ', '<Default Extension="png" ContentType="image/png"/><Default ', 1)
            data = ct.encode('utf8')
        out.writestr(item, data)
    for new, data in new_media.values():
        out.writestr('xl/media/' + new, data)
print('готово:', DST)
