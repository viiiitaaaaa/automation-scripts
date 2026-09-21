# wb_browser_easy.py — «для чайника»: берём товары прямо со страницы через браузер
# Запуск: py -3 -u C:\Users\User\my\wb_browser_easy.py

import csv, time, math
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

OUTFILE = r"C:\Users\User\my\wb_result.csv"

# <<< сюда вставь свои запросы; для пробы — 5 штук >>>
QUERIES = [
    "лампа настольная",
    "светильник настольный",
    "термокружка",
    "лежанка для кошек",
    "ланч бокс",
]
# потом просто замени этот список на свои 135 строк

START_URL = "https://www.wildberries.ru/"

def open_browser():
    opts = uc.ChromeOptions()
    opts.add_argument("--headless=new")        # тихий режим (без окна)
    opts.add_argument("--disable-gpu")
    opts.add_argument("--lang=ru-RU")
    opts.add_argument("--window-size=1280,2000")
    driver = uc.Chrome(options=opts)
    driver.implicitly_wait(10)
    return driver

def human_sleep(sec=0.7):
    time.sleep(sec)

def go_search(driver, query):
    driver.get(START_URL)
    # поле поиска
    box = driver.find_element(By.ID, "searchInput")
    box.clear()
    box.send_keys(query)
    box.send_keys(Keys.ENTER)
    # ждём загрузку выдачи
    human_sleep(1.2)

def scroll_first_page(driver):
    # прокручиваем до конца несколько раз, чтоб всё догрузилось
    last_h = 0
    for _ in range(8):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        human_sleep(1.0)
        h = driver.execute_script("return document.body.scrollHeight || 0;")
        if h == last_h:
            break
        last_h = h

def parse_products_from_html(html):
    soup = BeautifulSoup(html, "lxml")
    items = []
    # карточки товаров: ссылки вида <a class="product-card__main" href="/catalog/XXXX/detail.aspx?...">
    for a in soup.select("a.product-card__main"):
        href = a.get("href") or ""
        # ищем nmId (число) в href: /catalog/178976584/detail.aspx
        nm = None
        for part in href.split("/"):
            if part.isdigit():
                nm = int(part)
        if not nm:
            continue
        # цена: элемент с классом price__lower-price (или похожим)
        price_text_el = a.select_one(".price__lower-price, .price__lower, .price__price")
        price = None
        if price_text_el:
            txt = price_text_el.get_text(" ", strip=True)
            # вытащим цифры (в рублях), напр. "1 234 ₽" -> "1234"
            digits = "".join(ch for ch in txt if ch.isdigit())
            if digits:
                try:
                    price = float(digits)
                except:
                    price = None
        items.append({"nmId": nm, "price": price})
    # возможная альтернативная разметка (иногда элементы другие)
    if not items:
        for card in soup.select("article.product-card"):
            # атрибут data-nm-id
            nm_attr = card.get("data-nm-id") or card.get("data-id")
            nm = int(nm_attr) if nm_attr and str(nm_attr).isdigit() else None
            if not nm:
                continue
            price_el = card.select_one(".price__lower-price, .price__lower, .price__price")
            price = None
            if price_el:
                digits = "".join(ch for ch in price_el.get_text(" ", strip=True) if ch.isdigit())
                if digits:
                    try:
                        price = float(digits)
                    except:
                        price = None
            items.append({"nmId": nm, "price": price})
    # фильтруем нулевые/подозрительные цены (больше 150 тыс. — артефакты)
    clean = []
    for it in items:
        p = it["price"]
        if p is not None and (10 <= p <= 150000):
            clean.append(it)
    return clean

def fetch_dims_batch(driver, nm_ids):
    # используем тот же браузер: с его куками запрос «карточек» даёт корректнее
    if not nm_ids:
        return {}
    nm_param = ";".join(str(x) for x in nm_ids[:120])  # до 120 за раз
    url = f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-1257786&spp=0&nm={nm_param}"
    driver.get(url)
    human_sleep(0.8)
    soup = BeautifulSoup(driver.page_source, "lxml")
    # ответ — JSON, отрендеренный как текст; вытащим его целиком
    pre = soup.find("pre")
    if not pre or not pre.text:
        return {}
    import json
    try:
        data = json.loads(pre.text)
    except:
        return {}
    prods = (data.get("data") or {}).get("products") or []
    out = {}
    for pr in prods:
        nm = pr.get("id") or pr.get("nmId")
        dims = pr.get("dimensions") or {}
        L,W,H = dims.get("length"), dims.get("width"), dims.get("height")
        if nm and all(isinstance(x,(int,float)) and x>0 for x in (L,W,H)):
            out[int(nm)] = (float(L), float(W), float(H))
    return out

def mean(xs):
    xs = [x for x in xs if isinstance(x,(int,float))]
    return round(sum(xs)/len(xs), 2) if xs else None

def main():
    print(">>> запускаю браузер…", flush=True)
    driver = open_browser()
    rows = []
    try:
        print(">>> запросов:", len(QUERIES), flush=True)
        for i, q in enumerate(QUERIES, 1):
            print(f"[{i}/{len(QUERIES)}] {q}", flush=True)
            go_search(driver, q)
            scroll_first_page(driver)
            items = parse_products_from_html(driver.page_source)
            print(f"  товаров на 1-й странице: {len(items)}", flush=True)

            prices = [it["price"] for it in items if it["price"] is not None]
            avg_price = mean(prices)

            # габариты — запросим батчем
            dims_map = {}
            batch = [it["nmId"] for it in items]
            # разобьём по 100 штук на всякий случай
            for k in range(0, len(batch), 100):
                part = batch[k:k+100]
                dm = fetch_dims_batch(driver, part)
                dims_map.update(dm)
                time.sleep(0.6)

            Ls = [v[0] for v in dims_map.values()]
            Ws = [v[1] for v in dims_map.values()]
            Hs = [v[2] for v in dims_map.values()]

            row = {
                "query": q,
                "items_on_page": len(items),
                "avg_price": avg_price,
                "avg_len": mean(Ls),
                "avg_wid": mean(Ws),
                "avg_hei": mean(Hs),
                "dims_coverage_%": round(100 * (len(dims_map) / max(1, len(items))), 1),
            }
            print("  ->", row, flush=True)
            rows.append(row)
            time.sleep(0.6)
    finally:
        driver.quit()

    # сохраняем CSV
    with open(OUTFILE, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["query","items_on_page","avg_price","avg_len","avg_wid","avg_hei","dims_coverage_%"])
        w.writeheader()
        w.writerows(rows)

    print(">>> готово ->", OUTFILE, flush=True)

if __name__ == "__main__":
    main()
