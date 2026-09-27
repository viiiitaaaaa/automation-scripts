"""Все страницы поиска Taobao (taobao_all.json, собран в Chrome) -> фильтр по нашим критериям -> taobao_otbor.xlsx.
Фильтр: без детского, мужского/унисекс, комплектов и летнего. Фото не добавляются (только после отбора)."""
import json, re, sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

SRC = sys.argv[1] if len(sys.argv) > 1 else 'taobao_all.json'
DST = sys.argv[2] if len(sys.argv) > 2 else 'taobao_otbor.xlsx'
RATE = 7.1  # юаней за доллар

RULES = [  # (метка, китайские слова в названии)
    ('детское', r'儿童|童装|女童|男童|宝宝|婴儿|亲子|中大童|小童|幼儿|学生童'),
    ('мужское/унисекс', r'男装|男士|男款|男生|男女|情侣|针织开衫男|男春|男秋|男冬'),
    ('комплект', r'两件|二件|三件|套装|一套|件套|\+.*裙|套裙'),
    ('лето', r'夏季|夏款|夏装|夏天|春夏|冰丝|防晒|空调衫|夏薄'),
]
EXTRA = [('большие размеры', r'大码|胖妈妈|胖mm'), ('распродажа/остатки', r'清仓|尾单|中古|奥特莱斯|捡漏')]


def parse_sales(s):
    """«2000+人付款» / «1000+ people paid» / «10,000+ people have viewed it» / «1万+人付款»."""
    if not s:
        return None, None, ''
    m = re.search(r'([\d.,]+)\s*(万)?', s)
    if not m:
        return None, None, ''
    n = float(m.group(1).replace(',', '')) * (10000 if m.group(2) else 1)
    n = int(n)
    plus = '+' in s
    views = bool(re.search(r'看过|viewed|浏览', s))
    return (None, n, plus) if views else (n, None, plus)


data = json.load(open(SRC, encoding='utf8'))
items = list(data.values()) if isinstance(data, dict) else data
keep, drop = [], {}
for it in items:
    t = it['title']
    why = [lab for lab, rx in RULES if re.search(rx, t)]
    if why:
        for w in why:
            drop[w] = drop.get(w, 0) + 1
        continue
    paid, views, plus = parse_sales(it.get('sales', ''))
    it.update(paid=paid, views=views, plus=plus,
              note=', '.join(lab for lab, rx in EXTRA if re.search(rx, t)))
    keep.append(it)
keep.sort(key=lambda x: (x['paid'] is None, -(x['paid'] or 0), -(x['views'] or 0), x['price'] or 0))

wb = Workbook()
ws = wb.active
ws.title = 'Taobao отбор'
ws.append(['Название (кит.)', 'Заметка', 'Цена ¥', 'Цена $', 'Оплатили (чел.)', 'Посмотрели (чел.)',
           'Точность', 'Магазин', 'Стр. поиска', 'Ссылка Taobao', 'ID'])
for c in ws[1]:
    c.font = Font(bold=True, color='FFFFFF')
    c.fill = PatternFill('solid', fgColor='404040')
    c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
for col, w in zip('ABCDEFGHIJK', [55, 20, 9, 9, 13, 13, 15, 24, 8, 12, 16]):
    ws.column_dimensions[col].width = w
for n, it in enumerate(keep, start=2):
    price = it.get('price') or None
    ws.append([it['title'], it['note'], price, round(price / RATE, 2) if price else None, it['paid'], it['views'],
               ('округлено («+»)' if it['plus'] else 'точно') if (it['paid'] or it['views']) else 'нет данных',
               it.get('shop', ''), it.get('page'), 'открыть', it['id']])
    ws.cell(n, 10).hyperlink = f"https://item.taobao.com/item.htm?id={it['id']}"
    ws.cell(n, 10).font = Font(color='0563C1', underline='single')
ws.freeze_panes = 'A2'
ws.auto_filter.ref = f'A1:K{len(keep) + 1}'

ws2 = wb.create_sheet('Пояснения')
lines = [f'Источник: поиск Taobao «刺绣针织开衫» (вязаный кардиган с вышивкой), все страницы, 27.09.2026. Всего товаров: {len(items)}.',
         f'Оставлено: {len(keep)}. Убрано по нашим критериям: ' + ', '.join(f'{k} — {v}' for k, v in drop.items()) +
         ' (товар может попасть сразу в несколько причин).',
         '«Оплатили» — сколько человек купили (Taobao не даёт помесячно). «1000+» = от 1000 до следующего порога.',
         '«Посмотрели» — у товаров, где Taobao показывает просмотры вместо покупок; это НЕ продажи.',
         f'Цена $ = цена ¥ / {RATE}. Розничная цена в Китае (после скидки), не закупочная.',
         'Заметка — справочно, не фильтр: большие размеры, распродажа/остатки.',
         'Фото не добавлены: добавить после отбора.']
for line in lines:
    ws2.append([line])
ws2.column_dimensions['A'].width = 130
wb.save(DST)
print('всего', len(items), 'оставлено', len(keep), 'убрано', drop, '->', DST)
