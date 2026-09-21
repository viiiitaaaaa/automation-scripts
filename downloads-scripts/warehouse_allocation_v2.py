"""
Алгоритм распределения партии товара по складам (Ozon FBO / Wildberries).
Версия 2 — порог "меньше 20 — не рассматриваем" считается по СУММЕ
склада за всю партию (по всем артикулам), а не по каждому артикулу
отдельно.

Логика:
  1. Для каждого артикула есть общее количество единиц к поставке (qty)
     и веса по складам (рекомендованное количество из Export).
  2. ПЕРВЫЙ ПРОХОД: партия каждого артикула делится между ВСЕМИ
     складами пропорционально весам, округление до шага STEP (обычно 5)
     методом наибольшего остатка — сумма по складам точно равна qty.
     Здесь НЕТ порога на отдельный артикул — склад может получить
     и 5 шт по одному артикулу, это нормально.
  3. Считаем сумму каждого склада по ВСЕМ артикулам партии.
  4. Если у какого-то склада суммарно набралось МЕНЬШЕ min_amount —
     такой склад убираем из рассмотрения целиком, а его товар
     переразбрасываем среди оставшихся складов (шаг 2 повторяется
     заново уже без этого склада).
  5. Повторяем, пока при пересчёте больше не появляется складов
     с суммой ниже порога.

Использование:
    python3 warehouse_allocation_v2.py

Либо импортировать allocate_shipment() в свой скрипт.
"""

import openpyxl
from typing import Dict, List, Sequence, Tuple


# ---------------------------------------------------------------------------
# 1. Ядро алгоритма — чистые функции, без Excel.
# ---------------------------------------------------------------------------

def largest_remainder_round(qty: int, weights: Dict[int, float], step: int = 5) -> Dict[int, int]:
    """
    Делит qty между ключами weights пропорционально весам, округляя
    каждое значение до кратного `step`, так что сумма результата
    ТОЧНО равна qty (метод наибольшего остатка).
    """
    idxs = list(weights.keys())
    total = sum(weights[i] for i in idxs)
    n = len(idxs)

    if total == 0:
        raw = {i: qty / n for i in idxs}
    else:
        raw = {i: qty * weights[i] / total for i in idxs}

    floor = {i: int(raw[i] // step) * step for i in idxs}
    remainder_units = qty - sum(floor.values())
    blocks = int(remainder_units // step)

    order = sorted(idxs, key=lambda i: -(raw[i] - floor[i]))

    alloc = dict(floor)
    for i in range(blocks):
        alloc[order[i]] += step
    return alloc


def allocate_shipment(
    articles: List[Tuple[str, int, Sequence[float]]],
    warehouse_count: int,
    min_amount: int = 20,
    step: int = 5,
) -> Tuple[List[List[int]], set]:
    """
    Распределяет ВСЮ партию (список артикулов) по складам.

    articles         — список (артикул, qty, weights), weights — список
                        весов по складам (длина = warehouse_count) для
                        конкретно этого артикула.
    warehouse_count  — общее число складов-кандидатов.
    min_amount       — минимальная суммарная (по всей партии) поставка
                        на склад, ниже которой склад исключается.
    step             — шаг округления (обычно 5 шт).

    Возвращает:
      alloc_per_article — список списков: для каждого артикула — список
                           длиной warehouse_count с распределением.
      active_warehouses — множество индексов складов, которые остались
                           в итоге (прошли порог min_amount).
    """
    active = set(range(warehouse_count))

    while True:
        col_totals = [0] * warehouse_count
        alloc_per_article: List[List[int]] = []

        for art, qty, weights in articles:
            alloc_dict = largest_remainder_round(
                qty, {i: weights[i] for i in active}, step
            )
            alloc = [alloc_dict.get(i, 0) for i in range(warehouse_count)]
            alloc_per_article.append(alloc)
            for i in active:
                col_totals[i] += alloc[i]

        below_threshold = [i for i in active if col_totals[i] < min_amount]
        if not below_threshold:
            return alloc_per_article, active

        active -= set(below_threshold)
        if not active:
            # край.случай: вообще не осталось складов — отдаём всё
            # складу с наибольшим суммарным весом по всем артикулам
            total_weight = [0.0] * warehouse_count
            for _, _, weights in articles:
                for i in range(warehouse_count):
                    total_weight[i] += weights[i]
            best = max(range(warehouse_count), key=lambda i: total_weight[i])
            active = {best}
            # пересчитать с единственным складом — цикл продолжится сам


# ---------------------------------------------------------------------------
# 2. Обвязка для работы с Excel-файлами.
# ---------------------------------------------------------------------------

def load_export_weights(export_path: str, sheet_name: str,
                         warehouse_export_cols: Dict[str, int]) -> Dict[str, List[float]]:
    """
    Читает лист Export, строит { "артикул поставщика": [веса по складам] }.
    warehouse_export_cols — {имя_склада: номер_колонки_в_Export (1-based)}.
    Порядок ключей словаря задаёт порядок в итоговом списке весов.
    """
    wb = openpyxl.load_workbook(export_path, data_only=True)
    ws = wb[sheet_name]

    wh_names = list(warehouse_export_cols.keys())
    data: Dict[str, List[float]] = {}

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
        art = row[1]  # колонка B — "Артикул поставщика"
        if not art:
            continue
        art = str(art).strip()
        data[art] = [row[warehouse_export_cols[w] - 1] or 0 for w in wh_names]

    return data


def process_workbook(
    target_path: str, target_sheet: str,
    export_path: str, export_sheet: str,
    output_path: str,
    article_col: int, qty_col: int,
    warehouse_target_cols: Dict[str, int],
    warehouse_export_cols: Dict[str, int],
    min_amount: int = 20, step: int = 5,
    first_data_row: int = 2, last_data_row: int = None,
) -> None:
    """
    Полный цикл: читает целевой лист (артикул + количество к поставке),
    берёт веса из Export, считает распределение по всей партии сразу
    (с отсевом складов по суммарному порогу) и записывает результат
    в колонки складов целевого листа.
    """
    wh_names = list(warehouse_target_cols.keys())
    assert wh_names == list(warehouse_export_cols.keys()), \
        "Порядок и состав складов в target/export должны совпадать"

    weights_by_article = load_export_weights(export_path, export_sheet, warehouse_export_cols)

    wb_target = openpyxl.load_workbook(target_path, data_only=False)
    ws_target = wb_target[target_sheet]
    wb_target_data = openpyxl.load_workbook(target_path, data_only=True)
    ws_target_data = wb_target_data[target_sheet]

    if last_data_row is None:
        last_data_row = ws_target_data.max_row

    # "Замораживаем" формулы в статичные значения — иначе openpyxl
    # потеряет закэшированные результаты формул (например VLOOKUP на
    # внешнюю книгу) при сохранении.
    for row in ws_target.iter_rows():
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith("="):
                cell.value = ws_target_data.cell(row=cell.row, column=cell.column).value

    # собираем список артикулов для распределения
    rows_meta = []      # (номер_строки, артикул, qty)
    articles = []        # (артикул, qty, weights) — для алгоритма
    skipped_no_article = 0
    missing_in_export = []

    for r in range(first_data_row, last_data_row + 1):
        art = ws_target_data.cell(row=r, column=article_col).value
        qty = ws_target_data.cell(row=r, column=qty_col).value

        if not art:
            skipped_no_article += 1
            continue
        if not isinstance(qty, (int, float)) or qty <= 0:
            continue

        key = str(art).strip()
        weights = weights_by_article.get(key)
        if weights is None:
            missing_in_export.append((r, art, qty))
            weights = [0] * len(wh_names)

        rows_meta.append((r, art, int(qty)))
        articles.append((key, int(qty), weights))

    alloc_per_article, active_warehouses = allocate_shipment(
        articles, warehouse_count=len(wh_names), min_amount=min_amount, step=step
    )

    target_cols = [warehouse_target_cols[w] for w in wh_names]
    for (r, art, qty), alloc in zip(rows_meta, alloc_per_article):
        for idx, col in enumerate(target_cols):
            ws_target.cell(row=r, column=col).value = alloc[idx] or None

    wb_target.save(output_path)

    print(f"Обработано артикулов: {len(rows_meta)}")
    print(f"Пропущено строк без артикула (итоги и т.п.): {skipped_no_article}")
    if missing_in_export:
        print(f"Не найдено соответствия в Export ({len(missing_in_export)}):")
        for row_num, art, qty in missing_in_export:
            print(f"  строка {row_num}: {art!r} ({qty} шт)")

    excluded = [w for w in wh_names if wh_names.index(w) not in active_warehouses]
    print(f"Склады, исключённые по порогу (< {min_amount} шт суммарно): {excluded or 'нет'}")
    print(f"Сохранено: {output_path}")


# ---------------------------------------------------------------------------
# 3. Пример использования.
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    WAREHOUSES = [
        "Москва", "СПБ", "Саратов", "Казань", "Самара", "Новосибирск",
        "Красноярск", "Воронеж", "Ростов", "Ярославль", "Тверь",
        "Уфа", "Краснодар", "Калининград", "Невинномысск",
    ]

    # колонки в целевом файле (лист "Метал"), K..Y = 11..25
    warehouse_target_cols = {name: 11 + i for i, name in enumerate(WAREHOUSES)}

    # соответствующие колонки в Export
    warehouse_export_cols = {
        "Москва": 8, "СПБ": 9, "Саратов": 10, "Казань": 14, "Самара": 17,
        "Новосибирск": 18, "Красноярск": 20, "Воронеж": 21, "Ростов": 25,
        "Ярославль": 27, "Тверь": 28, "Уфа": 15, "Краснодар": 24,
        "Калининград": 22, "Невинномысск": 26,
    }

    process_workbook(
        target_path="Проверочный_лист_Зеневич_04_08_Озон_ОБНОВЛЕН.xlsx",
        target_sheet="Метал",
        export_path="supply.xlsx",
        export_sheet="Export",
        output_path="Проверочный_лист_распределено_v2.xlsx",
        article_col=5,   # "Артикул продавца"
        qty_col=8,        # "Заявленное количество"
        warehouse_target_cols=warehouse_target_cols,
        warehouse_export_cols=warehouse_export_cols,
        min_amount=20,    # порог считается по СУММЕ склада за всю партию
        step=5,
    )
