# wb_browser_plain_easy.py
# v14 — single-domain, честная SPP только из PRELOADED_STATE, улучшенный парс габаритов, выборка карточек=5
import csv, time, re, json, math
from urllib.parse import quote
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, JavascriptException

print("### BUILD wb_browser_plain_easy v14 ###", flush=True)

OUTFILE = r"C:\Users\User\my\wb_result.csv"

# ---- СПИСОК ЗАПРОСОВ (твой полный) ----
QUERIES = [
    "лампа настольная","светильник настольный","термокружка","лежанка для кошек","ланч бокс",
    "органайзер для хранения","сушилка для обуви","лежанка для собак","домик для кошки","машинка от катышек",
    "вешалка для одежды","мыльница для ванной","ночник детский","гирлянда штора","отпариватель для одежды",
    "фонарик аккумуляторный","сушилка для овощей и фруктов электрическая","мантоварка","зонтик женский","овощерезка многофункциональная",
    "ночник в розетку","гирлянда роса","блендер погружной мощный","швабра с отжимом и ведром для пола","воздуходувка аккумуляторная",
    "домик для кошки с когтеточкой","ламинатор","салфетки на стол под тарелки","тыква декор","мезороллер для лица",
    "пипидастр для пыли","сушилка для белья электрическая","панно на стену для интерьера","лава лампа","зонт детский для мальчика",
    "ключница настенная в прихожую","держатель для губки в раковину","зонт прозрачный","шинковка для капусты","органайзер для специй",
    "вешалки для брюк","зонт детский для девочки","органайзер для хранения вещей","зонтик детский для мальчика","ночник на батарейках",
    "мезороллер для волос","когтеточка для кошки с домиком","японская мочалка","трекер для отслеживания","сушилка для обуви электрическая",
    "кроватка для кукол","лампа настольная для маникюра","гладильная доска настенная","коврик для ванной быстросохнущий","бизиборд для девочки",
    "точилка для карандашей электрическая","коврик для ванной и туалета комплект","липучка на телефон двухсторонняя","зонтик детский","ланч бокс с подогревом",
    "мусорка настольная","набор для вязания","кардхолдер","овощечистка ручная","коврик на стиральную машину",
    "овощерезка ручная","светящийся ошейник для собак","липпер для телефона двухсторонний","часы настольные электронные","подставка под ноутбук",
    "лоток для кошек с высоким бортиком","чехол для карты","прозрачный зонт","коврик под миску для кошек","сенсорный дозатор для мыла",
    "фитолампа для растений полного спектра","органайзер для хранения пластиковый","органайзер для столовых приборов","блендер погружной для кухни","копилка для денег детская",
    "парковка для машинок","будильник громкий","кухня детская игровая деревянная","увлажнитель воздуха для дома бесшумный","зонт прозрачный женский",
    "лоток для кошек закрытый","органайзер для обуви","антискотч для удаления скотча","торшер настольный","подсвечники для свечей интерьерные",
    "электронные часы настольные","лампа настольная для школьника от сети","органайзер для носков","термокружка с трубочкой","3д бумага для рисования",
    "ершик для унитаза с подставкой напольный","гирлянда на батарейках маленькая","кубики для йоги","детская кухня игровая для девочки","зеркало с подсветкой для макияжа",
    "органайзер для документов а4","африканская мочалка","будильник детский","антистресс для рук взрослый","гирлянда уличная бахрома",
    "спальный мешок для новорожденных","органайзеры для кухни","овощерезка многофункциональная электрическая","ирригатор для зубов портативный","проектор для фильмов на стену",
    "мостик для спины","подставка для ножей на кухню","ночник в розетку с выключателем","воздуходувка аккумуляторная мощная","вешалка для отпаривания одежды",
    "диспенсер для мыла сенсорный","погружной блендер мощный и качественный","губка для цветов флористическая","ножеточка для ножей","озонатор воздуха для квартиры",
    "блоки для йоги","гирлянда на окно","спальный мешок зимний","подставка для специй","пипидастр для пыли антистатическая",
    "освежитель воздуха для туалета автоматический","магнитный держатель для телефона в машину","муфта на коляску","летающая птичка игрушка для кошек","органайзер для специй и приправ",
    "бутылка для масла растительного","дегидратор для фруктов","плед для собак","беспроводной светильник",
]

# ---- Настройки ----
HEADLESS = False
TIMEOUT  = 18
SCROLL_STEPS = 6            # докрутка выдачи
MAX_ITEMS_PER_QUERY = 30    # для цен берём до 30 с 1-й страницы
SAMPLE_PAGES = 5            # Сократили до 5: карточек для габаритов и SPP

SEARCH_HTML = "https://www.wildberries.ru/catalog/0/search.aspx?search={q}"
PRODUCT_URL = "https://www.wildberries.ru/catalog/{nm}/detail.aspx"

# ---------- базовые утилиты ----------
def open_browser():
    opts = Options()
    if HEADLESS: opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,2400")
    opts.add_argument("--lang=ru-RU")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--no-sandbox")
    d = webdriver.Chrome(options=opts)
    d.implicitly_wait(5)
    try:
        d.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        })
    except Exception: pass
    return d

def mean(xs):
    xs = [x for x in xs if isinstance(x,(int,float))]
    return round(sum(xs)/len(xs), 2) if xs else None

def percentile(xs, p):
    ys = sorted([x for x in xs if isinstance(x,(int,float))])
    if not ys: return None
    if len(ys)==1: return round(ys[0],2)
    k = (len(ys)-1)*(p/100.0)
    f = math.floor(k); c = math.ceil(k)
    if f==c: return round(ys[int(k)],2)
    return round(ys[f]*(c-k)+ys[c]*(k-f),2)

def to_number(s):
    if s is None: return None
    s = str(s).replace("\u2009"," ").replace("\xa0"," ").strip()
    s = re.sub(r"[^\d,.\s]", "", s).replace(" ", "").replace(",", ".")
    try: return float(s)
    except: return None

# ---------- 1) nmId + price из HTML поиска ----------
def extract_cards_prices_from_html(html):
    soup = BeautifulSoup(html, "lxml")
    items, seen = [], set()
    for card in soup.select("article.product-card, a.product-card__main"):
        nm = None
        href = card.get("href") or ""
        if href:
            parts = [p for p in href.split("/") if p.isdigit()]
            if parts: nm = int(parts[-1])
        if not nm:
            nm_attr = card.get("data-nm-id") or card.get("data-id")
            if nm_attr and str(nm_attr).isdigit():
                nm = int(nm_attr)
        if not nm or nm in seen: continue
        price = None
        for sel in [".price__lower-price", ".price__lower", ".price__price",
                    ".product-card__price", ".price-commission__current-price",
                    "[data-link='text{:product::price}']"]:
            el = card.select_one(sel)
            if el:
                num = to_number(el.get_text(" ", strip=True))
                if num and 10 <= num <= 150000:
                    price = num; break
        if price is None:
            text = card.get_text(" ", strip=True)
            m = re.findall(r"(\d[\d\s.,]*)\s*₽", text)
            if m:
                num = to_number(m[-1])
                if num and 10 <= num <= 150000: price = num
        if price is not None:
            items.append({"nmId": nm, "price": price})
            seen.add(nm)
    return items

def get_first_page_items(driver, query):
    url = SEARCH_HTML.format(q=quote(query))
    driver.get(url)
    try:
        WebDriverWait(driver, TIMEOUT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.product-card__main, article.product-card"))
        )
    except Exception: pass
    last = 0
    for _ in range(SCROLL_STEPS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.6)
        h = driver.execute_script("return document.body.scrollHeight || 0;")
        if h == last: break
        last = h
    items = extract_cards_prices_from_html(driver.page_source)
    return items[:MAX_ITEMS_PER_QUERY]

# ---------- 2) с карточки: PRELOADED_STATE + разметка ----------
def get_preloaded_state(driver):
    try:
        return driver.execute_script("return window.__PRELOADED_STATE__ || window.PRELOADED_STATE || null;")
    except Exception:
        return None

def find_values_anywhere(obj, keys):
    found = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = k.lower()
            if kl in keys and isinstance(v,(int,float)):
                found[kl] = v
            sub = find_values_anywhere(v, keys)
            if sub: found.update(sub)
    elif isinstance(obj, list):
        for v in obj:
            sub = find_values_anywhere(v, keys)
            if sub: found.update(sub)
    return found

def text_blocks_from_soup(soup):
    blocks = []
    # таблицы характеристик
    for row in soup.select(".product-params__row"):
        blocks.append(row.get_text(" ", strip=True))
    # любые секции с характеристиками
    for sel in ["#characteristics",".collapsible__content",".product-params",
                ".details-section",".product-details",".params",
                ".product-params__table",'[data-qa="characteristics"]',
                '.accordion__content','dl','.product-specs']:
        for b in soup.select(sel):
            blocks.append(b.get_text(" ", strip=True))
    return blocks

def parse_dims_from_text(txt):
    # 1) паттерн LxWxH
    txt = (txt or "").replace("\u00d7","x").replace("×","x")
    sep = r'[xX×\*хХ]'
    m = re.search(rf'(\d[\d\s.,]*)\s*{sep}\s*(\d[\d\s.,]*)\s*{sep}\s*(\d[\d\s.,]*)\s*(см\.?|mm|мм)?', txt, flags=re.I)
    def conv(v, unit):
        val = to_number(v)
        if val and unit in ("mm","мм"): return round(val/10,2)
        return val
    if m:
        unit = (m.group(4) or "").lower().rstrip(".")
        l,w,h = conv(m.group(1),unit), conv(m.group(2),unit), conv(m.group(3),unit)
        if l and w and h: return l,w,h
    # 2) именованные поля (приоритет упаковки)
    def f(lbl):
        mm = re.search(lbl + r'.{0,60}?(\d[\d\s.,]*)\s*(см\.?|mm|мм)?', txt, flags=re.I)
        if not mm: return None
        val = to_number(mm.group(1)); unit = (mm.group(2) or "").lower().rstrip(".")
        if val and unit in ("mm","мм"): val = round(val/10,2)
        return val
    # упаковка (приоритет)
    L = f(r"Длина упаковк")
    W = f(r"Ширин[аы] упаковк")
    H = f(r"Высот[аы] упаковк|Глубин[аы] упаковк")
    if L and W and H: return L,W,H
    # общее
    L = f(r"Длина( предмета)?")
    W = f(r"Ширин[аы]( предмета)?")
    H = f(r"Высот[аы]( предмета)?|Глубин[аы]( предмета)?")
    if L and W and H: return L,W,H
    return None,None,None

def extract_dims_and_spp_from_product_page(driver, nm):
    driver.get(PRODUCT_URL.format(nm=nm))
    try:
        WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.TAG_NAME,"body")))
    except TimeoutException:
        return (None,None,None,None)

    # --- SPP: только из PRELOADED_STATE ---
    spp_pct = None
    state = get_preloaded_state(driver)
    if state:
        vals = find_values_anywhere(state, {"priceu","salepriceu","clientpriceu","clientsale"})
        priceU = vals.get("priceu")
        salePriceU = vals.get("salepriceu") or priceU  # если нет salePriceU, считаем базой priceU
        clientPriceU = vals.get("clientpriceu")
        clientSale = vals.get("clientsale")
        if clientSale is not None:
            try:
                s = float(clientSale)
                if 0 <= s <= 95: spp_pct = round(s, 1)
            except: pass
        elif clientPriceU and salePriceU:
            try:
                base = float(salePriceU)
                cl   = float(clientPriceU)
                if base>0 and 0<cl<=base:
                    spp_pct = round((1.0 - cl/base)*100, 1)
            except: pass
    # никаких «старых/новых» цен — чтобы не ловить липовые -70%

    # --- габариты: раскрыть секции и распарсить ---
    for sel in ['[data-qa="collapsible-button"]','.collapsible__toggle',
                '.j-wba-card-item .collapsible__toggle','button[aria-expanded="false"]']:
        try:
            for el in driver.find_elements(By.CSS_SELECTOR, sel):
                try: driver.execute_script("arguments[0].click();", el); time.sleep(0.15)
                except JavascriptException: pass
        except Exception: pass
    for _ in range(4):
        driver.execute_script("window.scrollBy(0, 1200);"); time.sleep(0.3)

    soup = BeautifulSoup(driver.page_source, "lxml")
    blocks = text_blocks_from_soup(soup)
    text = " ".join(blocks) if blocks else soup.get_text(" ", strip=True)
    L,W,H = parse_dims_from_text(text)

    return (L,W,H,spp_pct)

# ---------- основной поток ----------
def main():
    print(">>> старт, открываю браузер…", flush=True)
    driver = open_browser()
    rows = []
    try:
        print(">>> запросов:", len(QUERIES), flush=True)
        for qi, q in enumerate(QUERIES, 1):
            print(f"[{qi}/{len(QUERIES)}] {q}", flush=True)

            # 1) цены + nmId с 1-й страницы
            items = get_first_page_items(driver, q)
            if not items:
                print("  ! нет карточек (проверь VPN/AdBlock).", flush=True)
                rows.append({"query": q,"items_on_page": 0,"avg_price": None,"p10": None,"p90": None,"spp_estimate_pct": None,"avg_len_cm": None,"avg_wid_cm": None,"avg_hei_cm": None,"dims_coverage_pct": 0.0})
                continue
            prices = [it["price"] for it in items]
            p10, p90, avg = percentile(prices,10), percentile(prices,90), mean(prices)
            nm_ids = [it["nmId"] for it in items]
            print(f"  карточек: {len(nm_ids)} | p10={p10} p90={p90} avg={avg}", flush=True)

            # 2) 5 карточек: габариты + SPP (только из стейта)
            dims_map = {}
            spp_vals = []
            sample_ids = nm_ids[:SAMPLE_PAGES]
            for idx, nm in enumerate(sample_ids, 1):
                print(f"    [{idx}/{len(sample_ids)}] nmId={nm} → характеристики и SPP…", flush=True)
                L,W,H,spp = extract_dims_and_spp_from_product_page(driver, nm)
                if all(v is not None for v in (L,W,H)):
                    dims_map[nm] = (L,W,H)
                if isinstance(spp,(int,float)):
                    spp_vals.append(spp)
                time.sleep(0.15)

            Ls = [v[0] for v in dims_map.values()]
            Ws = [v[1] for v in dims_map.values()]
            Hs = [v[2] for v in dims_map.values()]
            cov = round(100 * (len(dims_map) / max(1,len(sample_ids))), 1)
            spp_est = None
            if spp_vals:
                spp_vals.sort()
                n = len(spp_vals)
                spp_est = spp_vals[n//2] if n%2 else round((spp_vals[n//2-1]+spp_vals[n//2])/2, 1)

            row = {
                "query": q,
                "items_on_page": len(nm_ids),
                "avg_price": avg,
                "p10": p10,
                "p90": p90,
                "spp_estimate_pct": spp_est,     # медиана по 5 карточкам (только по PRELOADED_STATE)
                "avg_len_cm": mean(Ls),
                "avg_wid_cm": mean(Ws),
                "avg_hei_cm": mean(Hs),
                "dims_coverage_pct": cov,
            }
            print("  ->", row, flush=True)
            rows.append(row)
    finally:
        driver.quit()

    with open(OUTFILE, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=[
            "query","items_on_page","avg_price","p10","p90",
            "spp_estimate_pct","avg_len_cm","avg_wid_cm","avg_hei_cm","dims_coverage_pct"
        ])
        w.writeheader(); w.writerows(rows)
    print(">>> ГОТОВО ->", OUTFILE, flush=True)

if __name__ == "__main__":
    main()
