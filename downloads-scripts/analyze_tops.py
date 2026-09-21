"""
Анализ скачанных отчётов "Анализ топов поиска" (saleflow.pro).

Читает файлы из downloads_tops/ (по одному на каждый запрос и каждую категорию),
берёт пары "ключевой запрос - категория" из pairs.xlsx и считает по каждому:

- Тренд: рост выручки за последние 12 мес к предыдущим 12 мес, %
- Сезонность: топ-3 пиковых месяца по выручке + коэффициент сезонности
  (насколько пиковый месяц выше среднего)
- Средний чек: среднее за последние 12 недель
- Демпинг: средний коэффициент демпинга за последние 12 недель

Результат: analysis_result.xlsx - сравнительная таблица
"ключевой запрос vs его категория" по всем метрикам.

Запуск: python analyze_tops.py
(после того как run_tops.py скачал отчёты по всем 25 позициям)
"""

import re
from pathlib import Path
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

DOWNLOAD_DIR = Path("downloads_tops")
PAIRS_FILE = "pairs.xlsx"
OUT_FILE = "analysis_result.xlsx"

MONTH_NAMES = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
               "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]


def safe_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)[:120]


def load_report(query: str):
    """Читает скачанный отчёт, возвращает список dict по неделям."""
    path = DOWNLOAD_DIR / (safe_filename(query) + ".xlsx")
    if not path.exists():
        return None
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    header_idx = None
    for i, r in enumerate(rows):
        if r and r[0] == "Дата":
            header_idx = i
            break
    if header_idx is None:
        return None
    header = list(rows[header_idx])
    data = []
    for r in rows[header_idx + 1:]:
        if not r or not isinstance(r[0], datetime):
            continue
        rec = dict(zip(header, r))
        data.append(rec)
    return data


def metric(data, name, default=None):
    vals = [r.get(name) for r in data if isinstance(r.get(name), (int, float))]
    return vals if vals else default


def analyze(data):
    """Возвращает dict метрик для одного запроса/категории."""
    if not data:
        return None
    data = sorted(data, key=lambda r: r["Дата"])
    last_date = data[-1]["Дата"]

    def in_range(r, days_from, days_to):
        d = (last_date - r["Дата"]).days
        return days_from <= d < days_to

    # Тренд: выручка последних 365 дней vs предыдущих 365
    rev_now = sum(r.get("Выручка на позицию") or 0 for r in data if in_range(r, 0, 365))
    rev_prev = sum(r.get("Выручка на позицию") or 0 for r in data if in_range(r, 365, 730))
    trend_pct = (rev_now / rev_prev - 1) * 100 if rev_prev else None

    # Сезонность: средняя выручка по месяцам за всё время
    by_month = {}
    for r in data:
        m = r["Дата"].month
        by_month.setdefault(m, []).append(r.get("Выручка на позицию") or 0)
    month_avg = {m: sum(v) / len(v) for m, v in by_month.items()}
    overall_avg = sum(month_avg.values()) / len(month_avg) if month_avg else 0
    top3 = sorted(month_avg, key=month_avg.get, reverse=True)[:3]
    top3_names = ", ".join(MONTH_NAMES[m - 1] for m in sorted(top3))
    season_coef = (max(month_avg.values()) / overall_avg) if overall_avg else None

    # Средний чек и демпинг: последние 12 недель (84 дня)
    recent = [r for r in data if in_range(r, 0, 84)]
    checks = [r.get("Средний чек") for r in recent if isinstance(r.get("Средний чек"), (int, float))]
    avg_check = sum(checks) / len(checks) if checks else None
    dump = [r.get("Коэффициент демпинга на позицию") for r in recent
            if isinstance(r.get("Коэффициент демпинга на позицию"), (int, float))]
    avg_dump = sum(dump) / len(dump) if dump else None

    return {
        "trend_pct": trend_pct,
        "season_months": top3_names,
        "season_coef": season_coef,
        "avg_check": avg_check,
        "avg_dump": avg_dump,
        "period": f"{data[0]['Дата']:%d.%m.%Y} - {last_date:%d.%m.%Y}",
    }


def read_pairs():
    wb = openpyxl.load_workbook(PAIRS_FILE)
    ws = wb.active
    pairs = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] and row[1]:
            pairs.append((str(row[0]).strip(), str(row[1]).strip()))
    return pairs


def fmt(v, kind):
    if v is None:
        return "нет данных"
    if kind == "pct":
        return round(v, 1)
    if kind == "money":
        return round(v)
    if kind == "coef":
        return round(v, 2)
    return v


def main():
    pairs = read_pairs()
    print(f"Пар для анализа: {len(pairs)}")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Сравнение"

    headers = [
        "Ключевой запрос", "Категория",
        "Тренд запроса, % г/г", "Тренд категории, % г/г",
        "Пик. месяцы запроса", "Пик. месяцы категории",
        "Коэф. сезонности запроса", "Коэф. сезонности категории",
        "Ср. чек запроса, руб (12 нед)", "Ср. чек категории, руб (12 нед)",
        "Демпинг запроса, % (12 нед)", "Демпинг категории, % (12 нед)",
    ]
    ws.append(headers)

    header_fill = PatternFill("solid", start_color="D9E1F2")
    for c in ws[1]:
        c.font = Font(name="Arial", bold=True, size=10)
        c.fill = header_fill
        c.alignment = Alignment(wrap_text=True, vertical="center")

    cache = {}

    def get_metrics(name):
        if name not in cache:
            cache[name] = analyze(load_report(name))
        return cache[name]

    for q, cat in pairs:
        mq = get_metrics(q)
        mc = get_metrics(cat)
        if mq is None:
            print(f"  [!] Нет файла отчёта для запроса: {q}")
        if mc is None:
            print(f"  [!] Нет файла отчёта для категории: {cat}")
        row = [
            q, cat,
            fmt(mq and mq["trend_pct"], "pct"), fmt(mc and mc["trend_pct"], "pct"),
            (mq and mq["season_months"]) or "нет данных",
            (mc and mc["season_months"]) or "нет данных",
            fmt(mq and mq["season_coef"], "coef"), fmt(mc and mc["season_coef"], "coef"),
            fmt(mq and mq["avg_check"], "money"), fmt(mc and mc["avg_check"], "money"),
            fmt(mq and mq["avg_dump"], "pct"), fmt(mc and mc["avg_dump"], "pct"),
        ]
        ws.append(row)

    for cell_row in ws.iter_rows(min_row=2):
        for c in cell_row:
            c.font = Font(name="Arial", size=10)

    widths = [34, 20, 12, 12, 16, 16, 12, 12, 14, 14, 12, 12]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

    ws.freeze_panes = "A2"
    wb.save(OUT_FILE)
    print(f"Готово: {OUT_FILE}")


if __name__ == "__main__":
    main()
