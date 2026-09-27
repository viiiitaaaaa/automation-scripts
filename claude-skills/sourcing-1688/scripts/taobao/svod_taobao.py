"""Сводная книга по всему собранному с Taobao (27.09.2026) — без новых заходов на Taobao.
Листы: итог 35–85 ¥ / от 200 покупок / все после фильтров / все собранные (с причиной отсева) / пояснения."""
import json, re
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

RATE = 7.1
DST = 'taobao_svod.xlsx'
RULES = [('детское', r'儿童|童装|女童|男童|宝宝|婴儿|亲子|中大童|小童|幼儿|学生童'),
         ('мужское/унисекс', r'男装|男士|男款|男生|男女|情侣|针织开衫男|男春|男秋|男冬'),
         ('комплект', r'两件|二件|三件|套装|一套|件套|\+.*裙|套裙'),
         ('лето', r'夏季|夏款|夏装|夏天|春夏|冰丝|防晒|空调衫|夏薄')]
EXTRA = [('большие размеры', r'大码|胖妈妈|胖mm'), ('распродажа/остатки', r'清仓|尾单|中古|奥特莱斯|捡漏')]
TAGS = [('для женщин постарше', r'中老年|妈妈装|妈妈上衣|妈妈打底'), ('униформа', r'工作服|定制|LOGO|logo|护士'),
        ('жилет', r'马甲|背心|坎肩|马夹')]


def sales(s):
    m = re.search(r'([\d.,]+)\s*(万)?', s or '')
    if not m:
        return None, None, 'нет данных'
    n = int(float(m.group(1).replace(',', '')) * (10000 if m.group(2) else 1))
    acc = 'округлено («+»)' if '+' in s else 'точно'
    return (None, n, acc) if re.search(r'看过|viewed|浏览', s) else (n, None, acc)


items = []
for it in json.load(open('taobao_all.json', encoding='utf8')).values():
    t = it['title']
    paid, views, acc = sales(it.get('sales'))
    drop = [lab for lab, rx in RULES + EXTRA if re.search(rx, t)]
    tags = [lab for lab, rx in TAGS if re.search(rx, t)]
    if 'униформа' in tags:
        drop.append('униформа')
    items.append(dict(it, paid=paid, views=views, acc=acc, drop=', '.join(drop), tags=', '.join(tags)))
items.sort(key=lambda x: (x['paid'] is None, -(x['paid'] or 0), -(x['views'] or 0)))

after = [x for x in items if not x['drop']]
top200 = [x for x in after if (x['paid'] or 0) >= 200]
final = [x for x in top200 if 35 <= (x['price'] or 0) <= 85]

HEAD = ['Заметка', 'Цена ¥', 'Цена $', 'Оплатили (чел.)', 'Посмотрели (чел.)', 'Точность', 'Магазин',
        'Стр. поиска', 'Название (кит.)', 'Ссылка Taobao', 'ID']
WID = [22, 9, 9, 12, 12, 15, 24, 8, 55, 12, 16]


def sheet(wb, title, rows, with_drop=False):
    ws = wb.create_sheet(title)
    head = (['Почему убран'] if with_drop else []) + HEAD
    ws.append(head)
    for c in ws[1]:
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = PatternFill('solid', fgColor='404040')
        c.alignment = Alignment(wrap_text=True, vertical='center', horizontal='center')
    for i, w in enumerate(([22] if with_drop else []) + WID):
        ws.column_dimensions[chr(65 + i)].width = w
    link = len(head) - 1
    for n, x in enumerate(rows, start=2):
        p = x.get('price') or None
        ws.append(([x['drop']] if with_drop else []) +
                  [x['tags'], p, round(p / RATE, 2) if p else None, x['paid'], x['views'], x['acc'],
                   x.get('shop', ''), x.get('page'), x['title'], 'открыть', str(x['id'])])
        ws.cell(n, link).hyperlink = f"https://item.taobao.com/item.htm?id={x['id']}"
        ws.cell(n, link).font = Font(color='0563C1', underline='single')
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = f'A1:{chr(64 + len(head))}{len(rows) + 1}'


wb = Workbook()
wb.remove(wb.active)
sheet(wb, f'Итог 35–85 ¥ ({len(final)})', final)
sheet(wb, f'От 200 покупок ({len(top200)})', top200)
sheet(wb, f'После фильтров ({len(after)})', after)
sheet(wb, f'Все собранные ({len(items)})', items, with_drop=True)
ws = wb.create_sheet('Пояснения')
for line in [
    'Источник: поиск Taobao «刺绣针织开衫» (вязаный кардиган с вышивкой), страницы 1–50, 27.09.2026. Разных товаров: %d.' % len(items),
    'Отсев (лист «После фильтров»): детское, мужское/унисекс, комплекты, летнее, большие размеры, распродажа/остатки, униформа.',
    'Лист «От 200 покупок»: оплатили ≥ 200. Лист «Итог»: плюс цена 35–85 ¥.',
    '«Оплатили» — сколько человек купили (за всё время, помесячно Taobao не даёт). «1000+» = от 1000 до следующего порога.',
    '«Посмотрели» — Taobao показывает просмотры вместо покупок у новых / малопродаваемых товаров; это НЕ продажи.',
    f'Цена — розничная в Китае после скидки; $ = ¥ / {RATE}.',
    'Заметка — справочно: для женщин постарше, жилет.',
    'Фото, рейтинг, процент выкупа, возвраты — НЕ собраны: 27.09 Taobao ограничил аккаунт за автосбор. На Taobao больше не заходим.',
]:
    ws.append([line])
ws.column_dimensions['A'].width = 130
wb.save(DST)
print('итог', len(final), '| от 200', len(top200), '| после фильтров', len(after), '| всего', len(items), '->', DST)
