"""Чистка выгрузки поиска Taobao (Downloads/taobao_items.csv) -> taobao_items_chistyy.xlsx: цена, продажи, перевод, фото."""
import csv, json, re, io, os, urllib.request
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XLImage
from openpyxl.styles import Font, Alignment, PatternFill
from PIL import Image

SRC = r'C:\Users\User\Downloads\taobao_items.csv'
IMGS = 'taobao_imgs.json'
DST = 'taobao_items_chistyy.xlsx'
RATE = 7.1  # юаней за доллар
WITH_PHOTOS = False  # фото — только после отбора по нашим критериям

RU = {
 '1081407647615': 'Кардиган в новокитайском стиле с плотной вышивкой, эластичный',
 '954126513825': 'Короткий кардиган с вышитыми бантиками',
 '779696364019': 'Кардиган со смайликами (для медиков / салонов), большие размеры',
 '968518598690': 'Короткий приталенный кардиган с вышитой собачкой, корейский стиль',
 '1063585963732': 'Короткий кардиган с вышивкой и воротником «питер пэн»',
 '958119741185': 'Детский кардиган на молнии с вышивкой',
 '963637450756': 'Кардиган в контрастную полоску с вышивкой (аутлет, распродажа)',
 '819592493794': 'Свободный кардиган с вышивкой, «ленивый» стиль',
 '761472869359': 'Мягкий кардиган с забавной мультяшной вышивкой, японский ретро',
 '1081124530302': 'Чёрный кардиган с цветочной вышивкой, французский стиль «шанель»',
 '1082351564795': 'Тёмно-синий кардиган с вышивкой, V-вырез',
 '785525455475': 'Тонкий летний кардиган из «ледяного шёлка» с вышитой собачкой',
 '627537607251': 'Кардиган JK (школьная форма) с вышитой короной, хлопок',
 '942966503296': 'Короткий кардиган «косы» с вышитой лошадкой, V-вырез',
 '962212518833': 'Чёрный кардиган с вышивкой пайетками',
 '894568839144': 'Шерстяной кардиган с вышитыми сердечками (семейный: жен/муж/дет)',
 '1083966513185': 'Комплект: мягкий кардиган с бабочками + платье на бретелях',
 '1080870212347': 'Двойка: топ на бретелях + ретро-кардиган с вышивкой',
 '973045157253': 'Тонкий свободный кардиган с вышивкой, большие размеры',
 '983557208716': 'Голубой мягкий кардиган с вышитыми листьями',
 '963586078566': 'Свободный кардиган с мультяшной вышивкой',
 '945000356188': 'Кардиган «косы» с вышитой лошадкой, «школьный» стиль',
 '708593430757': 'Короткий тонкий кардиган с объёмной цветочной вышивкой, V-вырез (лето)',
 '773475551527': 'Хлопковый кардиган с вышивкой на пуговицах, ретро',
 '679337167646': 'Двойка: ажурный кардиган с вышивкой + топ на бретелях',
 '741510684081': 'Вязаный жилет с цветочной вышивкой и оборками',
 '1083786330081': 'Мужской кардиган с цветочной вышивкой, V-вырез',
 '1085725264964': 'Утеплённый кашемировый кардиган с вышивкой (Ордос)',
 '631356429319': 'Короткий кашемировый кардиган с ручной вышивкой',
 '1077844582538': 'Кардиган 100% кашемир с вышивкой зверей и цветов',
 '984360835950': 'Короткий приталенный кардиган «косы» с вышитой лошадкой',
 '779582782670': 'Кардиган 100% шерсть мериноса с вышитой собачкой',
 '639750206838': 'Тонкий ажурный летний кардиган с вышивкой, рукав 3/4',
 '992444055521': 'Тройка: кардиган с мишкой + кружевной лонгслив + юбка в клетку',
 '992030408755': 'Свободный ретро-кардиган с вышивкой, носится двумя способами',
 '978286221634': 'Чёрный кардиган с вышивкой и принтом, корейский стиль',
 '644123236367': 'Чёрный тонкий хлопковый летний кардиган с вышивкой',
 '989300207502': 'Утеплённый ретро-кардиган с мультяшной вышивкой',
 '530562470109': 'Кардиган с вышитыми вишнями, большие размеры',
 '1046253450876': 'Кардиган с синими вышитыми цветами (Jeanswest)',
 '977894778211': 'Кардиган с вышитыми животными, «школьный» стиль',
 '966313987476': 'Свободный ретро-кардиган с вышивкой, под ципао (остатки партии)',
 '1086312336198': 'Короткий контрастный кардиган с отложным воротником (бренд ROUJE KORA)',
 '813830824130': 'Кардиган с вышивкой «бриллианты», унисекс, корейский бренд',
 '1074857374802': 'Кардиган с вышитым мишкой, большие размеры',
 '627893131390': 'Кардиган с вышитыми животными, «школьный» стиль',
 '894344776878': 'Винтажный кардиган с мультяшной вышивкой (секонд/остатки)',
}


def note(t):
    n = []
    if re.search(r'儿童|女童|亲子', t): n.append('детское')
    if re.search(r'针织开衫男|男女|情侣', t): n.append('мужское/унисекс')
    if re.search(r'两件|三件套|套装', t): n.append('комплект — не наше')
    if re.search(r'夏季|春夏|冰丝|防晒|空调衫', t): n.append('лето — не сезон')
    if re.search(r'大码|胖妈妈', t): n.append('большие размеры')
    if re.search(r'清仓|尾单|中古|奥特莱斯', t): n.append('распродажа/остатки')
    return ', '.join(n)


rows = list(csv.reader(open(SRC, encoding='utf-8-sig')))[1:]
imgs = json.load(open(IMGS, encoding='utf8')) if os.path.exists(IMGS) else {}
items, seen = [], set()
for r in rows:
    if len(r) > 5:  # «10,000+» разрезалось по запятой
        r = [r[0], r[1], ','.join(r[2:-2]), r[-2], r[-1]]
    title, price, sales, link, img = r
    iid = re.search(r'id=(\d+)', link).group(1)
    if iid in seen:
        continue
    seen.add(iid)
    num = int(re.match(r'([\d,]+)', sales).group(1).replace(',', ''))
    views = bool(re.search(r'看过|viewed', sales))
    items.append(dict(id=iid, title=title, ru=RU.get(iid, ''), price=float(price),
                      paid=None if views else num, views=num if views else None, plus='+' in sales,
                      link=f'https://item.taobao.com/item.htm?id={iid}', img=imgs.get(iid) or img, note=note(title)))
items.sort(key=lambda x: (x['paid'] is None, -(x['paid'] or 0), -(x['views'] or 0)))

os.makedirs('img', exist_ok=True)


def get_img(it):
    p = f"img/{it['id']}.png"
    if os.path.exists(p):
        return p
    url = it['img']
    if not url:
        return None
    if url.startswith('//'):
        url = 'https:' + url
    for u in (re.sub(r'\.(jpg|png|bmp)(_.*)?$', r'.\1_300x300.jpg', url), url):
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://s.taobao.com/'})
            im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=15).read())).convert('RGB')
            im.thumbnail((300, 300))
            im.save(p)
            return p
        except Exception:
            pass
    return None


wb = Workbook()
ws = wb.active
ws.title = 'Taobao кардиганы'
PH = ['Фото'] if WITH_PHOTOS else []
ws.append(PH + ['Что это', 'Заметка', 'Цена ¥', 'Цена $', 'Оплатили (чел.)', 'Посмотрели (чел.)',
                'Точность', 'Название (кит.)', 'Ссылка Taobao', 'ID'])
link_col = len(PH) + 9
last_col = chr(64 + len(PH) + 10)
for c in ws[1]:
    c.font = Font(bold=True, color='FFFFFF')
    c.fill = PatternFill('solid', fgColor='404040')
    c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
for col, w in zip('ABCDEFGHIJK', [20] * len(PH) + [40, 22, 9, 9, 13, 13, 16, 45, 14, 16]):
    ws.column_dimensions[col].width = w
no_img = 0
for n, it in enumerate(items, start=2):
    ws.append([''] * len(PH) + [it['ru'], it['note'], it['price'], round(it['price'] / RATE, 2), it['paid'], it['views'],
                                'округлено («+»)' if it['plus'] else 'точно', it['title'], 'открыть', it['id']])
    ws.cell(n, link_col).hyperlink = it['link']
    ws.cell(n, link_col).font = Font(color='0563C1', underline='single')
    for c in ws[n]:
        c.alignment = Alignment(wrap_text=True, vertical='center')
    if not WITH_PHOTOS:
        continue
    ws.row_dimensions[n].height = 110
    p = get_img(it)
    if p:
        xi = XLImage(p)
        xi.width = xi.height = 140
        ws.add_image(xi, f'A{n}')
    else:
        no_img += 1
ws.freeze_panes = 'A2'
ws.auto_filter.ref = f'A1:{last_col}{len(items) + 1}'
ws2 = wb.create_sheet('Пояснения')
for line in ['Источник: выгрузка поиска Taobao «刺绣针织开衫» (вязаный кардиган с вышивкой), 27.09.2026, первая страница.',
             '«Оплатили» — сколько человек купили (Taobao не даёт помесячно). «1000+» = от 1000 до следующего порога.',
             '«Посмотрели» — у товаров, где Taobao вместо покупок показывает просмотры; это НЕ продажи.',
             f'Цена $ = цена ¥ / {RATE}. Это розничная цена в Китае, не закупочная.',
             'Заметка — метки по названию: детское, мужское, комплект, лето, большие размеры, распродажа.',
             'Повторы по ID убраны. Сортировка: больше всего покупок сверху.']:
    ws2.append([line])
ws2.column_dimensions['A'].width = 120
wb.save(DST)
print('готово', len(items), 'товаров, без фото', no_img, '->', DST)
