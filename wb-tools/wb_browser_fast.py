# wb_browser_fast.py — цены из PRELOADED_STATE; габариты: wbx-content (глубокий парс) -> card.wb.ru (глубокий парс) -> немного со страниц
import csv, time, re, json, concurrent.futures, requests
from urllib.parse import quote
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

OUTFILE = r"C:\Users\User\my\wb_result.csv"

# --- ТВОИ ЗАПРОСЫ (для теста оставил 5; потом вставь все 135) ---
QUERIES = [
    "лампа настольная",
    "светильник настольный",
    "термокружка",
    "лежанка для кошек",
    "ланч бокс",
]

# Настройки
DIM_LIMIT_PER_QUERY     = 30   # сколько nmId с 1-й страницы пытаться взять на габариты
FALLBACK_PRODUCT_PAGES  = 10   # сколько карточек дополнительно открыть (если JSON не дал размеры)
MAX_WORKERS             = 20   # параллельность запросов к wbx-content
HEADLESS                = False  # для честного PRELOADED_STATE — лучше False

SEARCH_URL = "https://www.wildberries.ru/catalog?search={q}"
WBX_URL    = "https://wbx-content-v2.wbstatic.net/ru/{nm}.json"
CARD_EPS   = [
    "https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest={dest}&spp={spp}&nm={ids}",
    "https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest={dest}&spp={spp}&nm={ids}",
]
DESTS = [-1257786, -1029256, -2562383]
SPPS  = [30, 1, 0]

# ---------------- утилиты ----------------
def open_browser():
    opts = Options()
    if HEADLESS:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1280,2400")
    opts.add_argument("--lang=ru-RU")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(6)
    try:
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        })
    except Exception:
        pass
    return driver

def scroll_first_page(driver):
    last = 0
    for _ in range(10):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.6)
        h = driver.execute_script("return document.body.scrollHeight || 0;")
        if h == last:
            break
        last = h

def mean(xs):
    xs = [x for x in xs if isinstance(x,(int,float))]
    return round(sum(xs)/len(xs), 2) if xs else None

def to_number(s):
    if s is None: return None
    s = str(s).replace("\u2009"," ").replace("\xa0"," ").strip()
    s = re.sub(r"[^\d,.\s]", "", s).replace(" ", "").replace(",", ".")
    try: return float(s)
    except: return None

# ---------------- цены из PRELOADED_STATE ----------------
def get_preloaded_state(driver, tries=24, pause=0.5):
    for _ in range(tries):
        try:
            raw = driver.execute_script("""
                if (window.__PRELOADED_STATE__) {
                    try { return JSON.stringify(window.__PRELOADED_STATE__); } catch(e){ return null; }
                }
                return null;
            """)
            if raw: return json.loads(raw)
        except Exception:
            pass
        time.sleep(pause)
    return None

def find_products_in_state(obj):
    found = []
    if isinstance(obj, dict):
        if "products" in obj and isinstance(obj["products"], list):
            arr = [p for p in obj["products"] if isinstance(p, dict)]
            if arr: found.append(arr)
        for v in obj.values():
            found.extend(find_products_in_state(v))
    elif isinstance(obj, list):
        for v in obj:
            found.extend(find_products_in_state(v))
    return found

def prices_from_state(state):
    lists = find_products_in_state(state) if state else []
    products = max(lists, key=lambda x: len(x)) if lists else []
    out = []
    for p in products:
        nm = p.get("id") or p.get("nmId")
        if not nm: continue
        price = None
        for k in ("salePriceU","priceU"):
            v = p.get(k)
            if isinstance(v,(int,float)) and v>0:
                price = round(v/100.0, 2); break
        if price is None:
            pr = p.get("price") or {}
            for k in ("saleU","totalU","basicU","productU","basic","product"):
                v = pr.get(k)
                if isinstance(v,(int,float)) and v>0:
                    price = round((v/100.0) if v>10000 else float(v), 2); break
        if price and 10 <= price <= 150000:
            out.append({"nmId": int(nm), "price": float(price)})
    return out[:60]

# запасной путь (если state вдруг не появился)
def extract_cards_prices_from_html(html):
    soup = BeautifulSoup(html, "lxml")
    items = []
    for card in soup.select("article.product-card, a.product-card__main"):
        nm = None
        href = card.get("href") or ""
        if href:
            for part in href.split("/"):
                if part.isdigit(): nm = int(part)
        if not nm:
            nm_attr = card.get("data-nm-id") or card.get("data-id")
            if nm_attr and str(nm_attr).isdigit(): nm = int(nm_attr)
        if not nm: continue
        price = None
        for sel in [".price__lower-price", ".price__lower", ".price__price", ".product-card__price", ".price-commission__current-price"]:
            el = card.select_one(sel)
            if el:
                num = to_number(el.get_text(" ", strip=True))
                if num and 10 <= num <= 150000:
                    price = num; break
        if price is None:
            text = card.get_text(" ", strip=True)
            m = re.search(r"(\d[\d\s.,]*)\s*₽", text)
            if m:
                num = to_number(m.group(1))
                if num and 10 <= num <= 150000:
                    price = num
        if price is not None:
            items.append({"nmId": nm, "price": price})
    return items

# ---------------- глубокий парс размеров ----------------
SEP_RE = r'[xX×\*хХ]'

def parse_dims_from_LWH(L, W, H):
    vals = []
    for v in (L, W, H):
        if isinstance(v,(int,float)) and v>0: vals.append(float(v))
        else: vals.append(None)
    if all(vals):
        # если похоже на мм — переведём
        if vals[0] > 200 or vals[1] > 200 or vals[2] > 200:
            vals = [round(v/10,2) for v in vals]
        return tuple(vals)
    return (None, None, None)

def parse_dims_from_text(txt):
    txt = (txt or "").replace("\u00d7","x").replace("×","x")
    m = re.search(rf'(\d[\d\s.,]*)\s*{SEP_RE}\s*(\d[\d\s.,]*)\s*{SEP_RE}\s*(\d[\d\s.,]*)\s*(см\.?|mm|мм)?', txt, flags=re.I)
    if m:
        l,w,h = to_number(m.group(1)), to_number(m.group(2)), to_number(m.group(3))
        unit = (m.group(4) or "").lower().rstrip(".")
        if l and w and h:
            if unit in ("mm","мм"): return round(l/10,2), round(w/10,2), round(h/10,2)
            return l,w,h
    def f(lbl):
        mm = re.search(lbl + r'.{0,60}?(\d[\d\s.,]*)\s*(см\.?|mm|мм)?', txt, flags=re.I)
        if not mm: return None
        val = to_number(mm.group(1)); unit = (mm.group(2) or "").lower().rstrip(".")
        if val and unit in ("mm","мм"): val = round(val/10,2)
        return val
    L=f(r"Длина"); W=f(r"Ширина"); H=f(r"Высота")
    if L and W and H: return L,W,H
    return None,None,None

def collect_name_value_pairs(obj, acc):
    if isinstance(obj, dict):
        if "name" in obj and "value" in obj:
            name = str(obj.get("name","")).strip()
            value = str(obj.get("value","")).strip()
            if name and value: acc.append((name, value))
        for v in obj.values():
            collect_name_value_pairs(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            collect_name_value_pairs(v, acc)

def find_any_dims_dict(obj):
    """Рекурсивно ищем словари формата {length,width,height} в любом месте JSON."""
    if isinstance(obj, dict):
        keys = set(k.lower() for k in obj.keys())
        if {"length","width","height"} <= keys:
            return parse_dims_from_LWH(obj.get("length"), obj.get("width"), obj.get("height"))
        for v in obj.values():
            res = find_any_dims_dict(v)
            if any(res): return res
    elif isinstance(obj, list):
        for v in obj:
            res = find_any_dims_dict(v)
            if any(res): return res
    return (None,None,None)

def parse_dims_from_pairs_or_any(json_obj, extra_text=""):
    # 1) прямой поиск L/W/H словаря
    L,W,H = find_any_dims_dict(json_obj)
    if all((L,W,H)): return L,W,H
    # 2) пары name/value (Длина/Ширина/Высота) + текст «L×W×H»
    pairs = []
    collect_name_value_pairs(json_obj, pairs)
    if pairs:
        # прямые поля
        L1=W1=H1=None
        for name,val in pairs:
            low = name.lower()
            if "длина" in low and L1 is None:  L1 = to_number(val)
            if "ширин" in low and W1 is None:  W1 = to_number(val)
            if "высот" in low and H1 is None:  H1 = to_number(val)
            if "глубин" in low:
                if H1 is None: H1 = to_number(val)
        LWH = parse_dims_from_LWH(L1,W1,H1)
        if all(LWH): return LWH
        L2,W2,H2 = parse_dims_from_text(" ".join([f"{n}: {v}" for n,v in pairs]) + " " + (extra_text or ""))
        if all((L2,W2,H2)): return L2,W2,H2
    # 3) ничего не нашли
    return (None,None,None)

# --- быстрый путь 1: wbx-content ---
def fetch_one_wbx(nm, ua):
    try:
        r = requests.get(
            WBX_URL.format(nm=nm), timeout=12,
            headers={
                "User-Agent": ua or "Mozilla/5.0",
                "Accept":"application/json, text/plain, */*",
                "Accept-Language":"ru-RU,ru;q=0.9",
                "Origin":"https://www.wildberries.ru",
                "Referer": f"https://www.wildberries.ru/catalog/{nm}/detail.aspx",
            }
        )
        if r.status_code != 200:
            return nm, (None,None,None)
        data = r.json()
        desc = data.get("description") or ""
        return nm, parse_dims_from_pairs_or_any(data, desc)
    except Exception:
        return nm, (None,None,None)

def fetch_dims_wbx_fast(nm_ids, ua):
    result = {}
    if not nm_ids: return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = [ex.submit(fetch_one_wbx, nm, ua) for nm in nm_ids]
        for fut in concurrent.futures.as_completed(futures):
            nm, dims = fut.result()
            if all(v is not None for v in dims):
                result[nm] = dims
    return result

# --- быстрый путь 2: card.wb.ru (ищем L/W/H в любом месте product) ---
def fetch_dims_from_cards_api(nm_ids, ua):
    out = {}
    if not nm_ids: return out
    s = requests.Session()
    s.headers.update({
        "User-Agent": ua or "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Referer": "https://www.wildberries.ru/",
        "Connection": "keep-alive",
    })
    for i in range(0, len(nm_ids), 100):
        batch = nm_ids[i:i+100]
        found_any = False
        for ep in CARD_EPS:
            for dest in DESTS:
                for spp in SPPS:
                    url = ep.format(dest=dest, spp=spp, ids=";".join(map(str, batch)))
                    try:
                        r = s.get(url, timeout=12)
                        if r.status_code != 200:
                            continue
                        data = r.json()
                        products = ((data.get("data") or {}).get("products")) or []
                        for pr in products:
                            nm = pr.get("id") or pr.get("nmId")
                            if not nm: continue
                            L,W,H = find_any_dims_dict(pr)
                            if all((L,W,H)):
                                out[int(nm)] = (L,W,H)
                                found_any = True
                        if found_any:
                            break
                    except Exception:
                        continue
                if found_any: break
            if found_any: break
        time.sleep(0.15)
    return out

# --- резерв: немного со страниц товара (быстро) ---
def fetch_dims_from_product_page(driver, nm):
    url = f"https://www.wildberries.ru/catalog/{nm}/detail.aspx"
    driver.get(url)
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    except: pass
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 1000);"); time.sleep(0.35)
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    blocks = []
    for sel in ["#characteristics",".collapsible__content",".product-params",".details-section",".product-details",".params",".product-params__table"]:
        for b in soup.select(sel):
            blocks.append(b.get_text(" ", strip=True))
    text = " ".join(blocks) if blocks else soup.get_text(" ", strip=True)
    return parse_dims_from_text(text)

# ---------------- основной поток ----------------
def main():
    print(">>> старт, открываю браузер…", flush=True)
    driver = open_browser()
    rows = []
    try:
        print(">>> запросов:", len(QUERIES), flush=True)
        for i, q in enumerate(QUERIES, 1):
            print(f"[{i}/{len(QUERIES)}] {q}", flush=True)
            driver.get(SEARCH_URL.format(q=quote(q)))
            try:
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "script")))
            except Exception:
                pass
            scroll_first_page(driver)

            # 1) ЦЕНЫ
            state = get_preloaded_state(driver)
            if state:
                cards = prices_from_state(state)
            else:
                print("  ! state не появился, беру цены из верстки (может быть неточнее)", flush=True)
                cards = extract_cards_prices_from_html(driver.page_source)

            nm_ids = [c["nmId"] for c in cards]
            prices = [c["price"] for c in cards]
            print(f"  товаров на 1-й странице: {len(nm_ids)}", flush=True)

            # 2) ГАБАРИТЫ
            take = min(DIM_LIMIT_PER_QUERY, len(nm_ids))
            target_ids = nm_ids[:take]
            ua = driver.execute_script("return navigator.userAgent;")

            # шаг A: wbx-content
            dims_map = fetch_dims_wbx_fast(target_ids, ua)
            wbx_ok = len(dims_map)

            # шаг B: card.wb.ru
            missing = [nm for nm in target_ids if nm not in dims_map]
            if missing:
                dims_cards = fetch_dims_from_cards_api(missing, ua)
                dims_map.update(dims_cards)
            cards_ok = len(dims_map) - wbx_ok

            # шаг C: немного со страниц товара
            missing = [nm for nm in target_ids if nm not in dims_map]
            pages_ok = 0
            for nm in missing[:FALLBACK_PRODUCT_PAGES]:
                try:
                    L,W,H = fetch_dims_from_product_page(driver, nm)
                    if all(v is not None for v in (L,W,H)):
                        dims_map[nm] = (L,W,H)
                        pages_ok += 1
                except Exception:
                    pass

            print(f"  dims: wbx_ok={wbx_ok}, cards_ok={cards_ok}, pages_ok={pages_ok}", flush=True)

            Ls = [v[0] for v in dims_map.values()]
            Ws = [v[1] for v in dims_map.values()]
            Hs = [v[2] for v in dims_map.values()]

            row = {
                "query": q,
                "items_on_page": len(nm_ids),
                "avg_price": mean(prices),
                "avg_len": mean(Ls),
                "avg_wid": mean(Ws),
                "avg_hei": mean(Hs),
                "dims_coverage_%": round(100 * (len(dims_map) / max(1, take)), 1) if take else 0.0,
            }
            print("  ->", row, flush=True)
            rows.append(row)
            time.sleep(0.2)
    finally:
        driver.quit()

    with open(OUTFILE, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["query","items_on_page","avg_price","avg_len","avg_wid","avg_hei","dims_coverage_%"])
        w.writeheader(); w.writerows(rows)
    print(">>> готово ->", OUTFILE, flush=True)

if __name__ == "__main__":
    main()
