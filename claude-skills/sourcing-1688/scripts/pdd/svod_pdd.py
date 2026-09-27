"""Все выдачи Pinduoduo (cj/pdd, pdd2, pdd3) в одну книгу с фото: общий лист + лист на каждый поиск.
Повторы (одинаковое название и цена в разных поисках) помечены. Переводы — ru_pdd.py каждой папки."""
import importlib.util, json, os, re, sys
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Font, Alignment, PatternFill
from PIL import Image

ROOT = r'C:\Users\User\cj'
DST = os.path.join(ROOT, 'pdd_svod', sys.argv[1] if len(sys.argv) > 1 else 'pdd_vse_poiski.xlsx')
RATE = 7.1
SEARCHES = [('pdd', '1. Юбки в клетку 2026', '格子半身裙2026, фильтр 40–90 ¥, по цене'),
            ('pdd2', '2. Клетчатые юбки-платья', '2026格子裙子新款 2026年 爆款, 40–90 ¥'),
            ('pdd3', '3. Средней длины, осень-зима', '格子半身裙中长款秋冬, 40–90 ¥')]

sys.path.insert(0, os.path.join(ROOT, 'pdd'))
tbl = importlib.util.spec_from_file_location('t', os.path.join(ROOT, 'pdd3', 'pdd_table.py'))
src = open(os.path.join(ROOT, 'pdd3', 'pdd_table.py'), encoding='utf8').read()
ns = {}
exec(src[:src.index('items = json.load')].replace('from ru_pdd import RU, TAGS', ''), ns)   # sales()
exec('import re\n' + src[src.index('def sales_ru'):src.index('for r, it in enumerate')], ns)  # sales_ru(), tags_ru()


def kind_of(t):
    if re.search(r'套装|两件套|三件套', t):
        return 'комплект'
    if re.search(r'连衣裙|衬衣裙|吊带裙|背带裙', t):
        return 'платье'
    return 'юбка'


rows = []
for folder, name, query in SEARCHES:
    spec = importlib.util.spec_from_file_location('ru_' + folder, os.path.join(ROOT, folder, 'ru_pdd.py'))
    ru = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ru)
    ns['TAGS'] = ru.TAGS
    fid = os.path.join(ROOT, folder, 'pdd_ids.txt')   # goods_id по порядку карточек на странице (№ = позиция)
    gids = dict(enumerate(open(fid).read().strip().split(','), start=1)) if os.path.exists(fid) else {}
    for it in json.load(open(os.path.join(ROOT, folder, 'pdd_items_skirts.json'), encoding='utf8')):
        n, kind = ns['sales'](it['sales'])
        rows.append(dict(search=name, folder=folder, n=it['n'], type=kind_of(it['title']), ru=ru.RU.get(it['n'], it['title']),
                         price=it['price'], sold=n, whose=kind, sales_ru=ns['sales_ru'](it['sales']),
                         tags=ns['tags_ru'](it.get('tags')), key=(it['title'], it['price']),
                         img=os.path.join(ROOT, folder, 'img', f"{it['n']}.jpg"), gid=gids.get(it['n'])))

seen = {}
for r in rows:
    seen.setdefault(r['key'], []).append(r['search'].split('.')[0])
for r in rows:
    other = [s for s in dict.fromkeys(seen[r['key']]) if s != r['search'].split('.')[0]]
    r['dup'] = ('есть и в поиске ' + ', '.join(other)) if other else ''

HEAD = ['Фото', 'Поиск', '№ на странице', 'Тип', 'Что это', 'Цена ¥', 'Цена $', 'Продано, шт', 'Чьи продажи',
        'Как указано на PDD', 'Пометки PDD', 'Повтор', 'Ссылка PDD']
WID = [20, 16, 8, 10, 52, 8, 8, 11, 14, 24, 40, 18, 14]


def thumb(p):
    t = p.replace('.jpg', '_t.jpg')
    if not os.path.exists(t):
        im = Image.open(p)
        im.thumbnail((260, 260))
        im.save(t, quality=88)
    return t


def sheet(wb, title, lst):
    ws = wb.create_sheet(title)
    ws.append(HEAD)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor='404040')
        c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
    for i, w in enumerate(WID):
        ws.column_dimensions[chr(65 + i)].width = w
    for rn, r in enumerate(lst, start=2):
        ws.append(['', r['search'], r['n'], r['type'], r['ru'], r['price'], round(r['price'] / RATE, 2) if r['price'] else None,
                   r['sold'], r['whose'], r['sales_ru'], r['tags'], r['dup'], 'открыть' if r['gid'] else 'нет'])
        if r['gid']:
            c = ws.cell(rn, 13)
            c.hyperlink = f"https://mobile.yangkeduo.com/goods.html?goods_id={r['gid']}"
            c.font = Font(color='0563C1', underline='single')
        for c in ws[rn]:
            c.alignment = Alignment(wrap_text=True, vertical='center')
        if os.path.exists(r['img']):
            xi = XLImage(thumb(r['img']))
            xi.width = xi.height = 130
            ws.add_image(xi, f'A{rn}')
        ws.row_dimensions[rn].height = 102
    ws.freeze_panes = 'B2'
    ws.auto_filter.ref = ws.dimensions


wb = Workbook()
wb.remove(wb.active)
sheet(wb, f'Все 3 поиска ({len(rows)})', rows)
for folder, name, query in SEARCHES:
    lst = [r for r in rows if r['folder'] == folder]
    sheet(wb, f'{name[:24]} ({len(lst)})', lst)
ws = wb.create_sheet('Пояснения')
for line in (['Три выдачи Pinduoduo от 27.09.2026 (мобильная версия, цена 40–90 ¥), чужие рекомендации (еда, техника) убраны:'] +
             [f'  {name}: «{query}»' for _, name, query in SEARCHES] +
             ['«Чьи продажи»: PDD чаще пишет продажи всего магазина (本店已拼, 全店总售) или бренда (品牌热销), а не этой модели; '
              'честно сравнивать товары можно только по «этот товар».',
              '«Повтор» — тот же товар (название и цена) встретился в другом поиске.',
              f'Цена — розничная на PDD; $ = ¥ / {RATE}. № — место товара на странице выдачи.',
              'Ссылки есть только у поиска 3 (номера товаров взяты с открытой страницы); у поисков 1 и 2 номера не сохранились.',
              'Названия переведены по смыслу; китайские оригиналы — в cj\\pdd*\\pdd_items_skirts.json.']):
    ws.append([line])
ws.column_dimensions['A'].width = 130
wb.save(DST)
print(len(rows), 'строк, повторов', sum(1 for r in rows if r['dup']), '->', DST)
