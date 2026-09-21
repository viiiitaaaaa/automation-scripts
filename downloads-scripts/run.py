"""
Автоматизация saleflow.pro:
- логинится на сайте
- заходит в раздел "Ниши и тренды -> По запросам"
- по очереди вводит запросы из queries.xlsx
- скачивает Excel-отчёт по каждому запросу в папку downloads/

ПЕРЕД ЗАПУСКОМ:
1) Установите Python 3.9+
2) Установите зависимости:
     pip install playwright openpyxl
     playwright install chromium
3) Положите файл queries.xlsx рядом со скриптом (список запросов в первом столбце,
   первая строка - заголовок "Запрос" - она будет пропущена).
4) Впишите логин/пароль ниже в LOGIN / PASSWORD (или через переменные окружения).
5) Запустите:  python run.py

Если что-то не находит нужную кнопку/поле - запустите с HEADLESS=False (уже стоит по
умолчанию), посмотрите, что происходит в открывшемся окне браузера, и пришлите мне
скриншот нужного экрана - я поправлю селекторы.
"""

import os
import re
import time
import openpyxl
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ================== НАСТРОЙКИ ==================
SITE_URL = "https://box.saleflow.pro/"
LOGIN = os.environ.get("SALEFLOW_LOGIN", "user_315921")
PASSWORD = os.environ.get("SALEFLOW_PASSWORD", "q9fk8u4r")

QUERIES_FILE = "queries.xlsx"
DOWNLOAD_DIR = Path("downloads")
DOWNLOAD_DIR.mkdir(exist_ok=True)

HEADLESS = False          # False = видно окно браузера (полезно для отладки)
SLOW_MO_MS = 150          # небольшая задержка между действиями, чтобы сайт успевал реагировать
WAIT_AFTER_SEARCH_SEC = 3 # сколько ждать построения отчёта перед поиском кнопки скачивания
# ================================================


def read_queries(path: str) -> list[str]:
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    queries = []
    for row in ws.iter_rows(min_row=1, values_only=True):
        val = row[0]
        if val is None:
            continue
        val = str(val).strip()
        if not val or val.lower() == "запрос":
            continue
        queries.append(val)
    return queries


def safe_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    return name[:120]


def login(page):
    page.goto(SITE_URL, wait_until="networkidle", timeout=60000)

    # Даём SPA время дорендерить форму входа
    try:
        page.wait_for_selector('input', timeout=15000)
    except PWTimeout:
        pass
    page.wait_for_timeout(1000)

    password_field = page.locator('input[type="password"]:visible').first
    login_field = page.locator('input:visible:not([type="password"])').first

    if login_field.count() == 0 or password_field.count() == 0:
        page.screenshot(path="debug_login_page.png", full_page=True)
        with open("debug_login_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        raise RuntimeError(
            "Не нашёл поле логина/пароля на стартовой странице. "
            "Я сохранил debug_login_page.png и debug_login_page.html рядом со скриптом - "
            "пришлите мне debug_login_page.png (картинку) в чат, и я поправлю селектор."
        )

    login_field.fill(LOGIN)
    password_field.fill(PASSWORD)

    # Кнопка входа - ищем по видимому тексту
    submit_btn = None
    for text in ["Войти", "Вход", "Login", "Sign in"]:
        btn = page.get_by_role("button", name=re.compile(text, re.I))
        if btn.count() > 0:
            submit_btn = btn.first
            break
    if submit_btn is None:
        # fallback: submit по Enter
        password_field.press("Enter")
    else:
        submit_btn.click()

    page.wait_for_load_state("networkidle")
    time.sleep(1)


def open_search_section(page):
    """
    Переход в раздел 'Ниши и тренды' -> 'По запросам'.
    Подстройте текст ссылок, если в меню сайта они называются иначе.
    """
    # Пункт верхнего/бокового меню
    niches_link = page.get_by_text(re.compile("Ниши и тренды", re.I))
    if niches_link.count() > 0:
        try:
            niches_link.first.hover(timeout=3000)
            page.wait_for_timeout(500)
        except Exception:
            pass
        niches_link.first.click(force=True, timeout=10000)
        page.wait_for_load_state("networkidle")
        time.sleep(1)

    by_query_link = page.get_by_text(re.compile("По запрос", re.I))
    if by_query_link.count() > 0:
        try:
            by_query_link.first.hover(timeout=3000)
            page.wait_for_timeout(500)
        except Exception:
            pass
        by_query_link.first.click(force=True, timeout=10000)
        page.wait_for_load_state("networkidle")
        time.sleep(1)
    else:
        page.screenshot(path="debug_menu_page.png", full_page=True)
        with open("debug_menu_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        raise RuntimeError(
            "Не нашёл раздел 'По запросам'. Сохранил debug_menu_page.png - пришлите его в чат."
        )


def find_search_input(page):
    for locator in [
        page.get_by_placeholder(re.compile("запрос|поиск|введите", re.I)),
        page.locator('input[type="search"]').first,
        page.locator('input[type="text"]').first,
    ]:
        try:
            if locator.count() > 0:
                return locator.first
        except Exception:
            continue
    page.screenshot(path="debug_search_page.png", full_page=True)
    with open("debug_search_page.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    raise RuntimeError(
        "Не нашёл поле поиска запросов на странице отчёта. "
        "Сохранил debug_search_page.png - пришлите его в чат."
    )


def close_modal_if_open(page):
    """Закрывает модальное окно с результатом предыдущего запроса, если оно открыто."""
    close_btn = page.locator('[aria-label="close"], [aria-label="Close"]')
    if close_btn.count() == 0:
        # запасной вариант: иконка крестика без aria-label, ищем по роли/символу
        close_btn = page.get_by_role("button", name=re.compile("закрыть|close", re.I))
    if close_btn.count() > 0:
        try:
            close_btn.first.click(force=True, timeout=5000)
            page.wait_for_timeout(500)
        except Exception:
            pass


def wait_for_report_ready(page, query: str, timeout_ms: int = 20000):
    """
    Ждёт заголовок модального окна с текстом запроса, а затем - пока пропадёт
    индикатор загрузки (если он есть), чтобы данные под графиком точно обновились.
    """
    page.get_by_text(re.compile(re.escape(query), re.I)).first.wait_for(
        state="visible", timeout=timeout_ms
    )
    # Если на сайте есть спиннер/лоадер - подождём, пока он исчезнет
    spinner = page.locator('[class*="loading" i], [class*="spinner" i], [class*="skeleton" i]')
    try:
        if spinner.count() > 0:
            spinner.first.wait_for(state="hidden", timeout=timeout_ms)
    except PWTimeout:
        pass
    for text in ["Найти", "Поиск", "Искать", "Search"]:
        btn = page.get_by_role("button", name=re.compile(text, re.I))
        if btn.count() > 0:
            btn.first.click(force=True, timeout=10000)
            return
    # Кнопки нет - нажимаем Enter прямо в поле поиска
    if search_input is not None:
        search_input.press("Enter")


def download_report(page, query: str):
    """
    Ищет кнопку 'Скачать'/'Экспорт' и сохраняет файл в DOWNLOAD_DIR
    с именем на основе запроса.
    """
    download_btn = None
    for text in ["Скачать", "Экспорт", "Export", "Download", "Excel", "XLSX"]:
        btn = page.get_by_role("button", name=re.compile(text, re.I))
        if btn.count() > 0:
            download_btn = btn.first
            break
        link = page.get_by_role("link", name=re.compile(text, re.I))
        if link.count() > 0:
            download_btn = link.first
            break

    if download_btn is None:
        safe_q = safe_filename(query)
        page.screenshot(path=f"debug_download_{safe_q}.png", full_page=True)
        with open(f"debug_download_{safe_q}.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        print(f"  [!] Не нашёл кнопку скачивания для запроса: {query} "
              f"(сохранил debug_download_{safe_q}.png)")
        return False

    with page.expect_download() as download_info:
        download_btn.click()
    download = download_info.value

    filename = safe_filename(query) + ".xlsx"
    dest = DOWNLOAD_DIR / filename
    download.save_as(dest)
    print(f"  [OK] Сохранено: {dest}")
    return True


def main():
    queries = read_queries(QUERIES_FILE)
    print(f"Найдено запросов: {len(queries)}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=SLOW_MO_MS)
        context = browser.new_context(accept_downloads=True, viewport={"width": 1600, "height": 900})
        page = context.new_page()

        print("Логинюсь...")
        login(page)

        print("Открываю раздел 'Ниши и тренды -> По запросам'...")
        open_search_section(page)

        for i, query in enumerate(queries, 1):
            print(f"[{i}/{len(queries)}] Запрос: {query}")
            try:
                close_modal_if_open(page)
                search_input = find_search_input(page)
                search_input.click(force=True, timeout=10000)
                search_input.fill("")
                search_input.fill(query)
                actual_value = search_input.input_value()
                print(f"    (в поле записалось: '{actual_value}')")
                click_search_button(page, search_input)
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except PWTimeout:
                    pass

                # Ждём, пока отчёт на странице реально обновится под новый запрос
                # (иначе можно скачать данные ещё от предыдущего запроса)
                try:
                    wait_for_report_ready(page, query)
                except PWTimeout:
                    print(f"  [!] Не увидел подтверждения обновления отчёта для '{query}', "
                          f"пробую скачать как есть")

                time.sleep(WAIT_AFTER_SEARCH_SEC)

                if i <= 3:
                    safe_q = safe_filename(query)
                    page.screenshot(path=f"debug_iter_{i}_{safe_q}.png", full_page=True)
                    print(f"    (сохранил debug_iter_{i}_{safe_q}.png для проверки)")

                download_report(page, query)
            except PWTimeout:
                safe_q = safe_filename(query)
                try:
                    page.screenshot(path=f"debug_error_{i}_{safe_q}.png", full_page=True)
                    with open(f"debug_error_{i}_{safe_q}.html", "w", encoding="utf-8") as f:
                        f.write(page.content())
                except Exception:
                    pass
                print(f"  [!] Таймаут на запросе: {query} (сохранил debug_error_{i}_{safe_q}.png)")
            except Exception as e:
                safe_q = safe_filename(query)
                try:
                    page.screenshot(path=f"debug_error_{i}_{safe_q}.png", full_page=True)
                    with open(f"debug_error_{i}_{safe_q}.html", "w", encoding="utf-8") as f:
                        f.write(page.content())
                except Exception:
                    pass
                print(f"  [!] Ошибка на запросе '{query}': {e} (сохранил debug_error_{i}_{safe_q}.png)")
            time.sleep(2)  # пауза, чтобы уведомление о скачивании исчезло и сайт не перегружался

        browser.close()
        print("Готово. Файлы лежат в папке downloads/")


if __name__ == "__main__":
    main()
