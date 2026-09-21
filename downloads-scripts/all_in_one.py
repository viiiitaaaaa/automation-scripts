# -*- coding: utf-8 -*-
"""
ВСЁ В ОДНОМ: скачивание отчётов saleflow.pro + анализ.

Что делает:
1. Логинится на box.saleflow.pro
2. Скачивает отчёты "Анализ топов поиска" по 16 ключевым запросам и 9 категориям
   (все запросы уже зашиты внутри - никакие другие файлы не нужны)
3. Считает тренд, сезонность, средний чек, демпинг
4. Сохраняет итоговую таблицу analysis_result.xlsx

КАК ЗАПУСТИТЬ:
1. Рядом с этим файлом создайте .env (см. .env.example) с логином и паролем saleflow.pro
2. Откройте командную строку В ЭТОЙ ПАПКЕ:
   (в Проводнике откройте папку, кликните в адресную строку, напишите cmd, Enter)
3. Выполните:  python all_in_one.py

Если не установлены библиотеки, сначала один раз выполните:
   pip install playwright openpyxl python-dotenv
   playwright install chromium
"""

import os
import re
import time
import urllib.parse
from pathlib import Path
from datetime import datetime

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
from dotenv import load_dotenv

load_dotenv()

# ================== НАСТРОЙКИ ==================
LOGIN = os.environ["SALEFLOW_LOGIN"]
PASSWORD = os.environ["SALEFLOW_PASSWORD"]
CITY = "Москва"
PERIOD_TAB = "по неделям"

# Пары: (ключевой запрос, категория)
PAIRS = [
    ("рубашка мужская вельветовая", "рубашка мужская"),
    ("рубашка серая мужская", "рубашка мужская"),
    ("коричневая рубашка мужская", "рубашка мужская"),
    ("джинсы рваные женские широкие", "джинсы женские"),
    ("брюки палаццо классические широкие", "брюки женские"),
    ("брюки коричневые мужские", "брюки мужские"),
    ("брюки клеш коричневые женские", "брюки женские"),
    ("юбка баллон женская", "юбка женская"),
    ("юбка рыбка женская", "юбка женская"),
    ("пиджак женский с баской", "пиджак женский"),
    ("пиджак женский удлиненный приталенный", "пиджак женский"),
    ("кейп женский вечерний", "кейп женский"),
    ("сумка ведро женская", "сумка женская"),
    ("сумка кисет женская", "сумка женская"),
    ("сумка замшевая женская натуральная", "сумка женская"),
    ("шоппер женский кожаный", "шоппер женский"),
]

DOWNLOAD_DIR = Path("downloads_tops")
OUT_FILE = "analysis_result.xlsx"
HEADLESS = False
WAIT_PAGE_SEC = 4
# ================================================

DOWNLOAD_DIR.mkdir(exist_ok=True)
MONTH_NAMES = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
               "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]


def safe_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", name)[:120]


def all_queries():
    """16 ключевых + уникальные категории, без повторов."""
    seen, result = set(), []
    for q, c in PAIRS:
        for item in (q, c):
            if item not in seen:
                seen.add(item)
                result.append(item)
    return result


# ---------------- СКАЧИВАНИЕ ----------------

def login(page):
    page.goto("https://box.saleflow.pro/", wait_until="networkidle", timeout=60000)
    try:
        page.wait_for_selector('input', timeout=15000)
    except PWTimeout:
        pass
    page.wait_for_timeout(1000)

    password_field = page.locator('input[type="password"]:visible').first
    login_field = page.locator('input:visible:not([type="password"])').first
    if login_field.count() == 0 or password_field.count() == 0:
        page.screenshot(path="debug_login_page.png", full_page=True)
        raise RuntimeError("Не нашёл поля логина/пароля (debug_login_page.png)")

    login_field.fill(LOGIN)
    password_field.fill(PASSWORD)
    btn = page.get_by_role("button", name=re.compile("Войти|Вход|Login", re.I))
    if btn.count() > 0:
        btn.first.click()
    else:
        password_field.press("Enter")
    page.wait_for_load_state("networkidle")
    time.sleep(1)


def build_url(query: str) -> str:
    params = urllib.parse.urlencode({"city": CITY, "wb_search": query, "tab": 1})
    return f"https://box.saleflow.pro/dashboard/search-tops-analysis/formed?{params}"


def select_period_tab(page):
    tab = page.get_by_role("button", name=re.compile(PERIOD_TAB, re.I))
    if tab.count() == 0:
        tab = page.get_by_text(re.compile(PERIOD_TAB, re.I))
    if tab.count() > 0:
        try:
            tab.first.click(force=True, timeout=8000)
            page.wait_for_timeout(1500)
        except Exception:
            pass


def download_one(page, query: str) -> bool:
    dest = DOWNLOAD_DIR / (safe_filename(query) + ".xlsx")
    if dest.exists():
        print("  [пропуск] уже скачан")
        return True

    page.goto(build_url(query), wait_until="networkidle", timeout=60000)
    time.sleep(WAIT_PAGE_SEC)
    select_period_tab(page)

    btn = page.get_by_role("button", name=re.compile("Скачать список", re.I))
    if btn.count() == 0:
        btn = page.get_by_text(re.compile("Скачать список", re.I))
    if btn.count() == 0:
        safe_q = safe_filename(query)
        page.screenshot(path=f"debug_tops_{safe_q}.png", full_page=True)
        print(f"  [!] Не нашёл 'Скачать список' (debug_tops_{safe_q}.png)")
        return False

    try:
        btn.first.scroll_into_view_if_needed(timeout=5000)
    except Exception:
        pass

    with page.expect_download(timeout=30000) as dl:
        btn.first.click(force=True)
    dl.value.save_as(dest)
    print(f"  [OK] {dest}")
    return True


def download_all():
    queries = all_queries()
    print(f"Нужно скачать отчётов: {len(queries)}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=100)
        context = browser.new_context(accept_downloads=True,
                                      viewport={"width": 1600, "height": 900})
        page = context.new_page()
        print("Логинюсь...")
        login(page)
        for i, q in enumerate(queries, 1):
            print(f"[{i}/{len(queries)}] {q}")
            try:
                download_one(page, q)
            except PWTimeout:
                print(f"  [!] Таймаут: {q}")
            except Exception as e:
                print(f"  [!] Ошибка: {e}")
            time.sleep(1.5)
        browser.close()
    print("Скачивание завершено.\n")


# ---------------- АНАЛИЗ ----------------

def load_report(query: str):
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
        if r and isinstance(r[0], datetime):
            data.append(dict(zip(header, r)))
    return data or None


def analyze(data):
    if not data:
        return None
    data = sorted(data, key=lambda r: r["Дата"])
    last_date = data[-1]["Дата"]

    def in_range(r, a, b):
        d = (last_date - r["Дата"]).days
        return a <= d < b

    rev_now = sum(r.get("Выручка на позицию") or 0 for r in data if in_range(r, 0, 365))
    rev_prev = sum(r.get("Выручка на позицию") or 0 for r in data if in_range(r, 365, 730))
    trend_pct = (rev_now / rev_prev - 1) * 100 if rev_prev else None

    by_month = {}
    for r in data:
        by_month.setdefault(r["Дата"].month, []).append(r.get("Выручка на позицию") or 0)
    month_avg = {m: sum(v) / len(v) for m, v in by_month.items()}
    overall = sum(month_avg.values()) / len(month_avg) if month_avg else 0
    top3 = sorted(month_avg, key=month_avg.get, reverse=True)[:3]
    season_months = ", ".join(MONTH_NAMES[m - 1] for m in sorted(top3))
    season_coef = (max(month_avg.values()) / overall) if overall else None

    recent = [r for r in data if in_range(r, 0, 84)]
    checks = [r.get("Средний чек") for r in recent if isinstance(r.get("Средний чек"), (int, float))]
    dump = [r.get("Коэффициент демпинга на позицию") for r in recent
            if isinstance(r.get("Коэффициент демпинга на позицию"), (int, float))]

    return {
        "trend_pct": trend_pct,
        "season_months": season_months,
        "season_coef": season_coef,
        "avg_check": sum(checks) / len(checks) if checks else None,
        "avg_dump": sum(dump) / len(dump) if dump else None,
    }


def fmt(v, kind):
    if v is None:
        return "нет данных"
    if kind == "pct":
        return round(v, 1)
    if kind == "money":
        return round(v)
    return round(v, 2)


def build_result():
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
    fill = PatternFill("solid", start_color="D9E1F2")
    for c in ws[1]:
        c.font = Font(name="Arial", bold=True, size=10)
        c.fill = fill
        c.alignment = Alignment(wrap_text=True, vertical="center")

    cache = {}

    def m(name):
        if name not in cache:
            cache[name] = analyze(load_report(name))
        return cache[name]

    missing = []
    for q, cat in PAIRS:
        mq, mc = m(q), m(cat)
        if mq is None:
            missing.append(q)
        if mc is None and cat not in missing:
            missing.append(cat)
        ws.append([
            q, cat,
            fmt(mq and mq["trend_pct"], "pct"), fmt(mc and mc["trend_pct"], "pct"),
            (mq and mq["season_months"]) or "нет данных",
            (mc and mc["season_months"]) or "нет данных",
            fmt(mq and mq["season_coef"], "coef"), fmt(mc and mc["season_coef"], "coef"),
            fmt(mq and mq["avg_check"], "money"), fmt(mc and mc["avg_check"], "money"),
            fmt(mq and mq["avg_dump"], "pct"), fmt(mc and mc["avg_dump"], "pct"),
        ])

    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = Font(name="Arial", size=10)
    widths = [34, 20, 12, 12, 16, 16, 12, 12, 14, 14, 12, 12]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    ws.freeze_panes = "A2"
    wb.save(OUT_FILE)

    print(f"Итоговая таблица: {OUT_FILE}")
    if missing:
        print("Не хватило отчётов по:", "; ".join(missing))
        print("Запустите скрипт ещё раз - он докачает недостающие (скачанные пропустит).")


if __name__ == "__main__":
    download_all()
    build_result()
