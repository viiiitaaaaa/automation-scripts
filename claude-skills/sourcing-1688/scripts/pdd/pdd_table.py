"""Таблица (всё по-русски, с фото) по выдаче Pinduoduo (pdd_items_skirts.json) -> pdd_yubki_ru.xlsx.
Важно: PDD пишет продажи по-разному — у товара («已拼/已售/已抢/热销») или у всего магазина/бренда («本店已拼», «全店总售», «品牌热销»)."""
import json, re
import os
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from PIL import Image
from ru_pdd import RU, TAGS
from openpyxl.styles import Font, Alignment, PatternFill

SRC, DST, RATE = 'pdd_items_skirts.json', 'pdd_yubki3_ru.xlsx', 7.1


def sales(s):
    m = re.search(r'([\d.]+)\s*(万)?\s*\+?\s*件', s or '')
    n = int(float(m.group(1)) * (10000 if m.group(2) else 1)) if m else None
    if not s:
        kind = 'нет данных'
    elif re.search(r'本店|全店|店铺', s):
        kind = 'весь магазин'
    elif '品牌' in s:
        kind = 'весь бренд'
    elif '仅剩' in s:
        kind, n = 'осталось на складе', None
    else:
        kind = 'этот товар'
    return n, kind


items = json.load(open(SRC, encoding='utf8'))
wb = Workbook()
ws = wb.active
ws.title = 'Юбки в клетку PDD'
head = ['Фото', '№ на странице', 'Тип', 'Что это', 'Цена ¥', 'Цена $', 'Продано, шт', 'Чьи продажи', 'Как указано на PDD',
        'Пометки PDD']
ws.append(head)
for c in ws[1]:
    c.font = Font(bold=True, color='FFFFFF')
    c.fill = PatternFill('solid', fgColor='404040')
    c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
for col, w in zip('ABCDEFGHIJ', [20, 9, 10, 55, 9, 9, 12, 16, 26, 45]):
    ws.column_dimensions[col].width = w


def sales_ru(s):
    m = re.search(r'([\d.]+)\s*(万)?\s*(\+)?\s*件', s or '')
    if m:
        n = float(m.group(1)) * (10000 if m.group(2) else 1)
        q = (f'{n / 1000:g} тыс.' if n >= 10000 else f'{n:g}') + ('+' if m.group(3) else '')
    else:
        q = ''
    for k, v in [('本店已拼', 'магазин продал '), ('全店总售', 'магазин продал '), ('品牌热销', 'бренд продал '),
                 ('仅剩', 'осталось '), ('已抢', 'купили '), ('已拼', 'купили '), ('限', 'лимит ')]:
        if (s or '').startswith(k):
            return v + q + ' шт'
    return s


def tags_ru(t):
    out = []
    for x in (t or '').split('|'):
        x = x.strip()
        if not x or x == '美国不可配送':
            continue
        m = re.match(r'好评超(\d+)%同款', x)
        out.append(TAGS.get(x) or (f'похожие: {m.group(1)}% хороших отзывов' if m else sales_ru(x) if '件' in x else x))
    return ', '.join(out)


for r, it in enumerate(items, start=2):
    n, kind = sales(it['sales'])
    ws.append(['', it['n'], 'комплект' if '套装' in it['title'] or '两件套' in it['title'] or '三件套' in it['title'] else 'платье' if '连衣裙' in it['title'] or '衬衣裙' in it['title'] or '吊带裙' in it['title'] or '背带裙' in it['title'] else 'комплект' if '套装' in it['title'] or '两件套' in it['title'] else 'юбка', RU.get(it['n'], it['title']), it['price'], round(it['price'] / RATE, 2) if it['price'] else None,
               n, kind, sales_ru(it['sales']), tags_ru(it.get('tags'))])
    p = f"img/{it['n']}.jpg"
    if os.path.exists(p):
        t = f"img/_t{it['n']}.jpg"
        if not os.path.exists(t):
            im = Image.open(p)
            im.thumbnail((260, 260))
            im.save(t, quality=88)
        xi = XLImage(t)
        xi.width = xi.height = 130
        ws.add_image(xi, f'A{r}')
    ws.row_dimensions[r].height = 102
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical='center')
ws.freeze_panes = 'A2'
ws.auto_filter.ref = ws.dimensions
ws2 = wb.create_sheet('Пояснения')
for line in ['Источник: выдача Pinduoduo «格子半身裙中长款秋冬» (юбка в клетку средней длины, осень-зима), цена 40–90 ¥; 27.09.2026. '
             'Загрузилось 100 товаров; 1 чужая рекомендация убрана. № — место на странице.',
             '«Чьи продажи»: PDD пишет либо продажи этого товара (已拼/已售/已抢/热销), либо всего магазина (本店已拼, 全店总售) '
             'или бренда (品牌热销). Сравнивать товары честно можно только по «этот товар».',
             f'Цена — розничная на PDD; $ = ¥ / {RATE}. Фото — в снимке Desktop\\pdd_vydacha_polnaya.png (номера совпадают).']:
    ws2.append([line])
ws2.column_dimensions['A'].width = 130
wb.save(DST)
print(len(items), '->', DST)
