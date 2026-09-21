from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
import csv, os, time, random, sys

# ------------------ НАСТРОЙКИ (подкрутите при необходимости) ------------------
BASE_URL = "https://saleflow.pro/seo/tools/seo-trends-checker"

# Пагинация:
USE_PAGE_PARAM = False            # True: листать по ?page=N; False: нажимать «Далее»
PAGE_PARAM_FMT = "?page={}"       # если USE_PAGE_PARAM=True
START_PAGE = 1
END_PAGE = 25000                  # верхний предел

# Селекторы таблицы:
TABLE_SELECTOR = "table"          # можно заменить на таблицу с классом, если их несколько
HEADER_ROW_SELECTOR = "thead tr"
BODY_ROW_SELECTOR   = "tbody tr"
CELL_SELECTOR       = "td, th"    # оставьте так — берёт текст из ячеек
ROW_CHECKBOX_SEL    = "input[type='checkbox']"  # чекбокс в строке (если есть)

# Кнопка "следующая страница", если USE_PAGE_PARAM=False
NEXT_BUTTON_CANDIDATES = [
    "a[rel='next']",
    "button[aria-label='Next']",
    "button:has-text('След')",
    "button:has-text('›')",
    "a:has-text('След')",
]

# Тайминги/надёжность
RATE_LIMIT_SECONDS = 0.6
RANDOM_JITTER = 0.4
MAX_RETRIES = 3
RETRY_DELAY = 3

# Вывод/прогресс
OUT_CSV = "saleflow_export.csv"
CHECKPOINT = "saleflow_checkpoint.txt"
# -----------------------------------------------------------------------------


def human_sleep(base=RATE_LIMIT_SECONDS):
    t = max(0, base + random.uniform(-RANDOM_JITTER, RANDOM_JITTER))
    time.sleep(t)

def save_checkpoint(n):
    with open(CHECKPOINT, "w", encoding="utf-8") as f:
        f.write(str(n))

def load_checkpoint():
    if os.path.exists(CHECKPOINT):
        try:
            return int(open(CHECKPOINT, encoding="utf-8").read().strip())
        except:
            return START_PAGE
    return START_PAGE

def append_rows(rows, headers=None):
    new_file = not os.path.exists(OUT_CSV)
    with open(OUT_CSV, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new_file and headers:
            w.writerow(headers)
        for r in rows:
            w.writerow(r)

def read_headers(page):
    # Пробуем достать заголовки из thead; если пусто — возьмём первую строку body.
    if page.locator(f"{TABLE_SELECTOR} {HEADER_ROW_SELECTOR}").count() > 0:
        hdr_cells = page.locator(f"{TABLE_SELECTOR} {HEADER_ROW_SELECTOR} {CELL_SELECTOR}")
        if hdr_cells.count() > 0:
            return [hdr_cells.nth(i).inner_text().strip() for i in range(hdr_cells.count())]
    # fallback: первая строка body
    body_rows = page.locator(f"{TABLE_SELECTOR} {BODY_ROW_SELECTOR}")
    if body_rows.count() > 0:
        first_cells = body_rows.nth(0).locator(CELL_SELECTOR)
        return [first_cells.nth(i).inner_text().strip() for i in range(first_cells.count())]
    return []

def collect_page(page, page_index):
    # ждём появления таблицы
    page.wait_for_selector(f"{TABLE_SELECTOR} {BODY_ROW_SELECTOR}", timeout=30000)

    # заголовки — один раз при первом заходе на страницу
    headers = read_headers(page)

    # проходим строки
    rows_el = page.locator(f"{TABLE_SELECTOR} {BODY_ROW_SELECTOR}")
    nrows = rows_el.count()
    data = []

    for i in range(nrows):
        row = rows_el.nth(i)

        # ставим галочку, если есть чекбокс
        try:
            if row.locator(ROW_CHECKBOX_SEL).count() > 0:
                cb = row.locator(ROW_CHECKBOX_SEL).first
                # на некоторых таблицах нужен JS-клик
                try:
                    cb.click(timeout=1000)
                except Exception:
                    page.evaluate("(el)=>el.click()", cb.element_handle())
                human_sleep(0.05)
        except Exception:
            pass

        cells = row.locator(CELL_SELECTOR)
        values = []
        for c in range(cells.count()):
            txt = cells.nth(c).inner_text().strip()
            values.append(txt)
        # если строка короче заголовков — дополним пустыми
        if headers and len(values) < len(headers):
            values += [""] * (len(headers) - len(values))
        data.append(values)

    # перед возвратом — добавим мета-колонки, если нужны:
    # ничего не добавляем, чтобы не ломать ширину.

    # запись в CSV
    append_rows(data, headers=headers)
    print(f"  ✓ Стр. {page_index}: сохранено строк — {len(data)}")

def goto_page_by_param(page, n):
    url = BASE_URL + PAGE_PARAM_FMT.format(n)
    for k in range(1, MAX_RETRIES+1):
        try:
            page.goto(url, wait_until="networkidle", timeout=0)
            return True
        except Exception as e:
            print(f"   ! Ошибка загрузки ({k}/{MAX_RETRIES}): {e}")
            time.sleep(RETRY_DELAY)
    return False

def click_next(page):
    for sel in NEXT_BUTTON_CANDIDATES:
        loc = page.locator(sel)
        if loc.count() > 0 and loc.first.is_enabled():
            try:
                loc.first.click()
                page.wait_for_load_state("networkidle")
                return True
            except Exception:
                continue
    return False


def main():
    start = load_checkpoint()
    print(f"Стартуем со страницы: {start}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)
        context = browser.new_context()
        page = context.new_page()
        page.set_default_timeout(0)

        # открываем базовый адрес — вы логинитесь сами
        page.goto(BASE_URL)
        input("➡ ВОЙДИТЕ в аккаунт и откройте таблицу.\nКогда таблица видна — нажмите ENTER здесь... ")

        # если листаем параметром
        if USE_PAGE_PARAM:
            # сразу перейдём на стартовую страницу
            if not goto_page_by_param(page, start):
                print("Не удалось открыть стартовую страницу.")
                browser.close(); sys.exit(1)

        for n in range(start, END_PAGE + 1):
            try:
                print(f"\n=== Страница {n} ===")
                if USE_PAGE_PARAM:
                    if n > start:
                        if not goto_page_by_param(page, n):
                            print("Пропускаем из-за ошибок загрузки.")
                            save_checkpoint(n+1); continue
                else:
                    # первый прогон — уже на нужной странице
                    if n > start:
                        ok = click_next(page)
                        if not ok:
                            print("Кнопка 'Далее' не найдена или неактивна. Останавливаюсь.")
                            break

                # подождём стабилизации
                page.wait_for_selector(f"{TABLE_SELECTOR} {BODY_ROW_SELECTOR}", timeout=60000)
                human_sleep()

                # собираем
                collect_page(page, n)

                # чекпоинт — на следующую страницу
                save_checkpoint(n + 1)

                # бережно паузим
                human_sleep()
            except KeyboardInterrupt:
                print("\nОстановлено вами. Прогресс сохранён.")
                break
            except PWTimeoutError:
                print("Тайм-аут. Пытаюсь продолжить.")
                human_sleep(RETRY_DELAY)
            except Exception as e:
                print("Ошибка:", e)
                human_sleep(RETRY_DELAY)

        print("\nГотово. Файл:", OUT_CSV)
        browser.close()


if __name__ == "__main__":
    main()
