# Разбор сбора Apify 1688 -> таблица «поставщик → растущие хиты» (cj\apify1688\hity_<дата>.xlsx).
# Рост = заказы дропшипперов за 7 дн × 30/7 ÷ заказы за 30 дн (>1 — ускоряется). Цена 35–70 ¥ уже отфильтрована сбором.
import json, glob, os, re, io, datetime, collections, concurrent.futures as cf, requests
import openpyxl
from openpyxl.drawing.image import Image as XImg
from openpyxl.styles import Font, PatternFill, Alignment
from PIL import Image

import sys
D = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else max(glob.glob(os.path.join(D, 'raw_*.json')), key=os.path.getmtime)
it = json.load(open(src, encoding='utf-8'))
STAMP = os.path.basename(src)[4:-5]
# поставщики, уже виденные в прошлых сборах (кроме текущего) и её отметки (столбец K = 1)
KNOWN, LIKED = set(), set()
for p in glob.glob(os.path.join(D, 'raw_*.json')):
    if os.path.abspath(p) != os.path.abspath(src):
        for x in json.load(open(p, encoding='utf-8')): KNOWN.add((x.get('supplier') or {}).get('companyName', ''))
for p in glob.glob(os.path.join(D, 'hity_*.xlsx')):
    try:
        wsx = openpyxl.load_workbook(p)['Поставщики']
        hdr = [c.value for c in wsx[2]]
        col = next((i for i, h in enumerate(hdr) if h and 'отметка' in str(h)), 10)
        for rr in wsx.iter_rows(min_row=3):
            if len(rr) > col and rr[col].value in (1, '1'): LIKED.add(rr[0].value)
    except Exception: pass
PLUS = ['毛呢', '麂皮', '鹿皮', '丝绒', '金丝绒', '百褶', '不规则', '设计感', '小众', '过膝', '高领', '西装', '深V', '收腰', '皮带', '叠穿',
        '立领', '格', '针织连衣裙', '毛衣裙', '中长', '复古', '花苞', '流苏', '重工', '刺绣', '盘扣', '新中式', '斗篷', '披肩', '提花', '老钱', '法式']
MINUS = ['豹纹', '印花', '碎花', '甜美', '蛋糕', '毛绒', '仿貂', '灯笼袖', '基础', '打底', '辣妹', '卫衣', '睡', '广场舞', '学生', '中老年', '妈妈']
def taste(t):
    p = [w for w in PLUS if w in t]; m = [w for w in MINUS if w in t]
    return len(p) - 2 * len(m), ' '.join(['+' + w for w in p] + ['−' + w for w in m])

def num(s):
    if s is None: return None
    s = str(s)
    if '以内' in s: return 50
    m = re.search(r'([\d.]+)\s*(万)?', s)
    if not m: return None
    v = float(m.group(1)) * (10000 if m.group(2) else 1)
    return v

BAD = re.compile(r'裤|套装|两件套|三件套|短裙|超短|迷你|小香风|豹纹|连帽|睡衣|家居')
rows, seen = [], set()
for x in it:
    if x['offerId'] in seen: continue
    seen.add(x['offerId'])
    t = x.get('title') or ''
    if BAD.search(t) and '裙裤' not in t: continue
    s = x.get('supplier') or {}
    m = ((x.get('dropship') or {}).get('metrics')) or {}
    o30, o7 = num(m.get('orders30d')), num(m.get('orders7d'))
    growth = round(o7 * 30 / 7 / o30, 2) if o30 and o7 and '以内' not in str(m.get('orders30d')) else None
    price = (x.get('price') or {}).get('min')
    rows.append(dict(
        id=x['offerId'], t=t, cat=x.get('categoryName', ''), price=price, sold=x.get('saledCount') or 0,
        o30=m.get('orders30d') or '', o7=m.get('orders7d') or '', growth=growth, pub=m.get('publishDate') or '',
        rep=x.get('offerRepurchaseRate'), srep=x.get('repurchaseRate'), stock=x.get('stock'),
        biz=s.get('bizType') or '', fact=s.get('isFactoryInspected'), comp=s.get('companyName', ''),
        shop=s.get('shopUrl', ''), city=(x.get('province') or '') + ' ' + (x.get('city') or ''), yrs=s.get('tpYear'),
        url=x.get('detailUrl'), same=x.get('sameDesignUrl', ''), img=(x.get('images') or [''])[0], kw=x.get('sourceKeyword')))

def score(r):  # растущий хит: объём × ускорение
    o30 = num(r['o30']) or 0
    return o30 * (r['growth'] or 0.5)
for r in rows:
    r['score'] = score(r); r['tv'], r['tt'] = taste(r['t'])

# группировка по поставщикам
sup = collections.defaultdict(list)
for r in rows: sup[r['comp']].append(r)
sup_rows = []
for comp, lst in sup.items():
    grow = [r for r in lst if (r['growth'] or 0) >= 1.0 and (num(r['o30']) or 0) >= 300]
    strong = [r for r in lst if r['sold'] >= 500]
    sup_rows.append(dict(comp=comp, n=len(lst), grow=len(grow), strong=len(strong), taste=round(sum(r['tv'] for r in lst) / len(lst), 1),
                         status='★ ваш' if comp in LIKED else ('уже был' if comp in KNOWN else 'НОВЫЙ'),
                         best=max(r['score'] for r in lst), biz=lst[0]['biz'],
                         fact=lst[0]['fact'], city=lst[0]['city'], yrs=lst[0]['yrs'], srep=lst[0]['srep'], shop=lst[0]['shop'],
                         cats=', '.join(sorted({r['cat'] for r in lst}))))
sup_rows.sort(key=lambda s: (-s['strong'], -s['taste'], -s['grow']))
rows.sort(key=lambda r: -r['score'])

UA = {'User-Agent': 'Mozilla/5.0'}
def thumb(u):
    try:
        b = requests.get(u + '_120x120.jpg', headers=UA, timeout=20).content
        im = Image.open(io.BytesIO(b)).convert('RGB'); im.thumbnail((90, 90)); bio = io.BytesIO(); im.save(bio, 'JPEG', quality=80); return bio
    except Exception:
        return None
pics = list(cf.ThreadPoolExecutor(8).map(thumb, [r['img'] for r in rows]))

wb = openpyxl.Workbook()
hdrfill = PatternFill('solid', fgColor='404040'); green = PatternFill('solid', fgColor='D9EAD3'); yellow = PatternFill('solid', fgColor='FFF2CC')
def header(ws, cols):
    ws.append(cols)
    for c in ws[ws.max_row]: c.font = Font(bold=True, color='FFFFFF'); c.fill = hdrfill; c.alignment = Alignment(wrap_text=True, vertical='center')

ws = wb.active; ws.title = 'Поставщики'
ws.append([f'1688 через Apify, {datetime.date.today():%d.%m.%Y}: юбки/трикотаж/платья осень-зима, 35–70 ¥, от 1 шт, «самые продаваемые». '
           'Растущий хит = заказов за 30 дн ≥300 и рост ≥1.0 (заказы за 7 дн идут быстрее среднего за месяц). '
           '生产加工 = производство, 经销批发 = оптовая перепродажа.'])
header(ws, ['Поставщик', 'Статус', 'Сильных моделей (500+ продаж)', 'Растущих хитов', 'Моделей в сборе', 'По вашему вкусу (ср.)',
             'Тип', 'Город', 'Лет на 1688', 'Выкуп магазина', 'Категории', 'Магазин', 'Ваша отметка (1)'])
for s in sup_rows:
    ws.append([s['comp'], s['status'], s['strong'], s['grow'], s['n'], s['taste'], s['biz'], s['city'], s['yrs'],
               f"{s['srep']:.0%}" if isinstance(s['srep'], (int, float)) else '', s['cats'], 'открыть', ''])
    ws.cell(ws.max_row, 12).hyperlink = s['shop']
    if s['status'] == 'НОВЫЙ' and s['strong'] >= 2 and s['taste'] > 0:
        for c in ws[ws.max_row]: c.fill = green
    elif s['status'] == '★ ваш':
        for c in ws[ws.max_row]: c.fill = yellow
for col, w in zip('ABCDEFGHIJKLM', [32, 9, 10, 8, 8, 9, 10, 14, 7, 9, 24, 8, 9]): ws.column_dimensions[col].width = w
ws.freeze_panes = 'B3'

w2 = wb.create_sheet('Хиты')
header(w2, ['№', 'Фото', 'Модель (кит.)', 'Категория', 'Цена ¥', 'Продано всего', 'Заказов дропшипп. 30 дн', 'за 7 дн', 'Рост (×)',
            'Выложена', 'Выкуп модели', 'Остаток', 'Поставщик', 'Тип', 'Город', 'Карточка', 'Та же модель у других', 'Подсказка по вкусу'])
for i, (r, p) in enumerate(zip(rows, pics), 1):
    w2.append([i, '', r['t'], r['cat'], r['price'], r['sold'], r['o30'], r['o7'], r['growth'], r['pub'],
               f"{r['rep']:.0%}" if isinstance(r['rep'], (int, float)) else '', r['stock'], r['comp'], r['biz'], r['city'], 'открыть', 'сравнить', r['tt']])
    row = w2.max_row
    w2.cell(row, 16).hyperlink = r['url']; w2.cell(row, 17).hyperlink = r['same']
    w2.row_dimensions[row].height = 70
    if p: im = XImg(p); im.anchor = f'B{row}'; w2.add_image(im)
    if (r['growth'] or 0) >= 1.0 and (num(r['o30']) or 0) >= 300:
        for c in w2[row]: c.fill = green
for col, w in zip('ABCDEFGHIJKLMNOPQ', [4, 13, 40, 10, 7, 9, 10, 8, 7, 10, 8, 9, 26, 10, 14, 9, 10]): w2.column_dimensions[col].width = w
for row in w2.iter_rows(min_row=2):
    for c in row: c.alignment = Alignment(wrap_text=True, vertical='center')
w2.freeze_panes = 'D2'
out = os.path.join(D, f'hity_{STAMP}.xlsx'); wb.save(out)
print(out)
print('моделей после фильтра:', len(rows), '| растущих:', sum(1 for r in rows if (r['growth'] or 0) >= 1 and (num(r['o30']) or 0) >= 300),
      '| новых поставщиков:', sum(1 for s in sup_rows if s['status'] == 'НОВЫЙ'))
for s in sup_rows[:20]:
    print(f"{s['status']} | сильн {s['strong']} / {s['n']} | вкус {s['taste']} | раст {s['grow']} | {s['comp']} | {s['biz']} | {s['city']} | {s['cats']}")
print('---')
for r in rows[:15]:
    print(f"{r['t'][:30]} | {r['price']}¥ | 30д {r['o30']} 7д {r['o7']} ×{r['growth']} | {r['pub']} | {r['comp'][:16]} | {r['biz']}")
