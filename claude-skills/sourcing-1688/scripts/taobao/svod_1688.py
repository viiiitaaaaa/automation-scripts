"""Добавляет в сводную книгу (taobao_svod.xlsx) всё найденное на 1688 -> svod_taobao_1688.xlsx.
Без захода на сайты: берёт её итог cj/katalog_1688_itog.xlsx и выгрузки 1688 из «Загрузок»."""
import glob, re
from openpyxl import load_workbook
from openpyxl.styles import Font, Alignment, PatternFill

DL = r'C:\Users\User\Downloads'
ITOG = r'C:\Users\User\cj\katalog_1688_itog.xlsx'
SRC = 'taobao_svod.xlsx'
DST = 'svod_taobao_1688.xlsx'


def pct(v):
    m = re.search(r'([\d.]+)', str(v or ''))
    if not m:
        return None
    x = float(m.group(1))
    return x / 100 if '%' in str(v) or x > 1 else x


def num(v):
    m = re.search(r'([\d.]+)\s*(万)?', str(v or '').replace(',', ''))
    return int(float(m.group(1)) * (10000 if m.group(2) else 1)) if m else None


def style(ws, widths, link_col, n_rows):
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor='404040')
        c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
    for i, w in enumerate(widths):
        ws.column_dimensions[chr(65 + i) if i < 26 else 'A' + chr(65 + i - 26)].width = w
    if link_col:
        for r in range(2, n_rows + 2):
            c = ws.cell(r, link_col)
            if c.value:
                c.hyperlink, c.value = c.value, 'открыть'
                c.font = Font(color='0563C1', underline='single')
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions


# --- 1. её итог 1688 (значения; формулы берём из кэша Excel, если он есть)
wbv = load_workbook(ITOG, data_only=True, read_only=True).worksheets[0]
rows = list(wbv.iter_rows(values_only=True))
h = list(rows[0])
want = ['Тип', 'Что это', 'Вердикт', 'Тренд (радар)', 'Чистыми с рекламой $', 'Цена 1688 ¥', 'Продано на 1688',
        'Доля повторных закупок', 'Продажи за год', 'Продажи за 30 дней', 'Динамика', 'Вывод по продажам',
        'Впервые выложен', 'Поштучно', 'Ссылка 1688', 'ID', 'Название (кит.)']
idx = []
for w in want:
    j = next((i for i, x in enumerate(h) if x and str(x).startswith(w.split(' $')[0].split(' (')[0])), None)
    idx.append(j)
itog = [[r[j] if j is not None else None for j in idx] for r in rows[1:] if any(r)]

# --- 2. выгрузки помощника 1688 (商品列表-1688采购助手)
helper = {}
for f in sorted(glob.glob(DL + r'\商品列表-1688采购助手*.xlsx')):
    it = load_workbook(f, read_only=True).active.iter_rows(values_only=True)
    hh = next(it)
    for r in it:
        if r and r[3]:
            helper[str(r[3])] = dict(zip(hh, r))

# --- 3. выгрузки поиска 1688 (TitleSearch_1688-ExportProduct)
search = {}
for f in sorted(glob.glob(DL + r'\TitleSearch_1688*.xlsx')):
    it = load_workbook(f, read_only=True).active.iter_rows(values_only=True)
    hh = next(it)
    for r in it:
        if r and r[1]:
            search[str(r[1])] = dict(zip(hh, r))

# общий список 1688: помощник точнее (годовые продажи), поиск добавляет остальное
allp = {}
for pid, d in search.items():
    allp[pid] = dict(src='поиск', title=d['Title'], price=num(d['Price']) if d['Price'] else None,
                     price_raw=d['Price'], sales=num(d['Cumulative Sales']), sales_txt=d['Cumulative Sales'],
                     rep=pct(d['Repeat Purchase Rate:']), shop=d['Shop Name'], place=d['Address'],
                     link=d['Product Link'], cat='', year=None, listed='')
for pid, d in helper.items():
    p = allp.setdefault(pid, dict(src='помощник', sales_txt='', shop='', place='', link=d['商品链接']))
    p.update(src='помощник' if p.get('src') != 'поиск' else 'поиск + помощник', title=d['标题'],
             price_raw=d['价格'], cat=d['类目'], year=num(d['年销售件数']), listed=str(d['上架时间'] or '')[:10],
             rep=pct(d['复购率']) if d['复购率'] else p.get('rep'), shop=d['店铺名称'] or p.get('shop'),
             link=d['商品链接'] or p.get('link'))
    p['sales'] = p.get('sales') or p['year']
for p in allp.values():
    try:
        p['price'] = float(str(p['price_raw']).split('-')[0])
    except (TypeError, ValueError):
        p['price'] = None

rule = [dict(p, id=k) for k, p in allp.items()
        if (p['rep'] or 0) >= 0.6 and p['price'] and 25 <= p['price'] <= 65 and (p['sales'] or 0) > 0]
rule.sort(key=lambda p: (-(p['rep'] or 0), -(p['sales'] or 0)))
everything = sorted((dict(p, id=k) for k, p in allp.items()), key=lambda p: -(p['sales'] or 0))

wb = load_workbook(SRC)
names_before = wb.sheetnames

ws = wb.create_sheet(f'1688 ваш итог ({len(itog)})')
ws.append(want)
for r in itog:
    ws.append(r)
style(ws, [10, 30, 10, 28, 10, 9, 10, 10, 10, 10, 10, 30, 11, 11, 10, 16, 45], want.index('Ссылка 1688') + 1, len(itog))


def p_sheet(title, lst):
    ws = wb.create_sheet(title)
    head = ['Доля повторных закупок', 'Цена ¥', 'Продажи (всего/за год)', 'Как указано', 'Продажи за год (помощник)',
            'Впервые выложен', 'Категория', 'Магазин', 'Где', 'Источник', 'Название (кит.)', 'Ссылка 1688', 'ID']
    ws.append(head)
    for p in lst:
        note = ' (мало продаж — % может быть случайным)' if (p['sales'] or 0) < 30 and p['rep'] else ''
        ws.append([p['rep'], p['price'], p['sales'], (p['sales_txt'] or '') + note, p['year'], p['listed'], p['cat'],
                   p['shop'], p['place'], p['src'], p['title'], p['link'], p['id']])
    for r in range(2, len(lst) + 2):
        ws.cell(r, 1).number_format = '0%'
    style(ws, [11, 9, 12, 22, 12, 11, 18, 26, 14, 14, 50, 10, 16], 12, len(lst))


p_sheet(f'1688 по правилам ({len(rule)})', rule)
p_sheet(f'1688 все выгрузки ({len(everything)})', everything)

ws = wb['Пояснения']
for line in ['',
             '— 1688 —',
             f'«1688 ваш итог» — данные из cj\\katalog_1688_itog.xlsx (лист «{load_workbook(ITOG, read_only=True).sheetnames[0]}»), '
             'без фото/графиков и формул юнит-экономики (они — в самом файле; «Чистыми с рекламой» — если Excel сохранил расчёт).',
             f'«1688 все выгрузки» — {len(helper)} товаров из окна помощника 1688 + {len(search)} из поиска 1688 (Загрузки, 26–27.09), '
             'без повторов. В основном юбки (半身裙) — это сбор соседней сессии.',
             '«1688 по правилам» — доля повторных закупок ≥ 60%, цена 25–65 ¥, продажи > 0 (ваше правило 27.09).',
             'Доля повторных закупок = 复购率 / Repeat Purchase Rate. При продажах < 30 процент может быть случайным.']:
    ws.append([line])
order = [n for n in wb.sheetnames if n.startswith('1688')] + names_before
wb._sheets = [wb[n] for n in names_before[:-1]] + [wb[n] for n in wb.sheetnames if n.startswith('1688')] + [wb['Пояснения']]
wb.save(DST)
print('итог 1688:', len(itog), '| помощник', len(helper), '| поиск', len(search), '| всего', len(everything),
      '| по правилам', len(rule), '->', DST)
