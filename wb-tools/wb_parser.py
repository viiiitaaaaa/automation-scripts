import sys, time, csv, traceback, requests
from urllib.parse import quote

print(">>> START wb_parser (exactmatch w/ regions & dest fallback)", flush=True)

OUTFILE = r"C:\Users\User\my\wb_first_page_stats.csv"
PAUSE = 0.6
APP = 1

# Комбинации, которые чаще всего дают полную первую страницу
DEST_CANDIDATES = [
    -1029256,       # часто «богатая» выдача
    -1257786,       # дефолт
]
SPP_CANDIDATES = [0, 30]

# regions — как у фронта WB (список складов/регионов в запросах)
REGIONS = "68,64,83,4,38,33,70,69,86,75,30,40,1,80,71"

SEARCH_ENDPOINTS = [
    "https://search.wb.ru/exactmatch/ru/common/v18/search",
    "https://search.wb.ru/exactmatch/ru/common/v5/search",
    "https://search.wb.ru/exactmatch/ru/common/v4/search",
]
URL_CARDS = "https://card.wb.ru/cards/v2/detail"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://www.wildberries.ru/",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Connection": "keep-alive",
}

# Для проверки оставил 8 запросов. Когда увидишь нормальные цифры — подставишь свой полный список.
QUERIES = [
    "лампа настольная",
    "термокружка",
    "лежанка для кошек",
    "гирлянда штора",
    "блендер погружной мощный",
    "светильник настольный",
    "зонт прозрачный",
    "органайзер для хранения",
]

def parse_price(prod):
    for k in ("salePriceU","priceU"):
        v = prod.get(k)
        if isinstance(v,(int,float)) and v > 0:
            return round(v/100.0, 2)
    price = prod.get("price") or {}
    for k in ("saleU","totalU","basicU","productU","basic","product"):
        v = price.get(k)
        if isinstance(v,(int,float)) and v > 0:
            return round((v/100.0) if v>10000 else float(v), 2)
    return None

def try_exactmatch_once(base_url, q, dest, spp, with_regions):
    params = {
        "appType": APP,
        "curr": "rub",
        "dest": dest,
        "lang": "ru",
        "resultset": "catalog",
        "sort": "popular",
        "spp": spp,
        "query": q,
        "page": 1,
        "reg": 0,
        "uiv": 4,            # как у фронта
    }
    if with_regions:
        params["regions"] = REGIONS
    r = requests.get(base_url, params=params, headers=HEADERS, timeout=30)
    if r.status_code != 200:
        raise requests.HTTPError(f"{r.status_code} for {base_url}")
    d = r.json()
    products = (d.get("data") or {}).get("products") or d.get("products") or []
    out = []
    for p in products:
        nm = p.get("id") or p.get("nmId")
        price = parse_price(p)
        if nm and price:
            out.append({"nmId": int(nm), "price": float(price)})
    return out

def search_first_page(q):
    last_error = None
    best = []
    # 1) с regions
    for base in SEARCH_ENDPOINTS:
        for dest in DEST_CANDIDATES:
            for spp in SPP_CANDIDATES:
                for with_regions in (True, False):
                    try:
                        prods = try_exactmatch_once(base, q, dest, spp, with_regions)
                        msg = f"{base.split('/common/')[1]} dest={dest} spp={spp} regions={with_regions}"
                        if prods and len(prods) > len(best):
                            best = prods
                            print(f"    -> ok ({msg}) items={len(prods)}", flush=True)
                            # если набрали 50+, считаем этого достаточно
                            if len(best) >= 50:
                                return best
                        else:
                            print(f"    -> {'empty' if not prods else 'worse'} ({msg}) items={len(prods)}", flush=True)
                    except Exception as e:
                        last_error = e
                        print(f"    -> fail ({msg}): {e}", flush=True)
    if not best and last_error:
        print(f"    !! no results. last error: {last_error}", flush=True)
    return best

def fetch_dims(nm_ids):
    if not nm_ids: return {}
    ids = ";".join(map(str, nm_ids))
    params = {"appType": APP, "curr": "rub", "dest": DEST_CANDIDATES[0], "spp": SPP_CANDIDATES[0], "nm": ids}
    r = requests.get(URL_CARDS, params=params, headers=HEADERS, timeout=30)
    r.raise_for_status()
    d = r.json()
    prods = (d.get("data") or {}).get("products") or []
    out = {}
    for pr in prods:
        nm = pr.get("id") or pr.get("nmId")
        dims = pr.get("dimensions") or {}
        L,W,H = dims.get("length"), dims.get("width"), dims.get("height")
        if nm and all(isinstance(x,(int,float)) and x>0 for x in (L,W,H)):
            out[int(nm)] = (float(L), float(W), float(H))
    return out

def mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs)/len(xs), 2) if xs else None

def robust_price_stats(prices):
    if not prices: return None, None
    ps = sorted(prices)
    # отсечём явные аномалии: > 150_000 р (для наших бытовых запросов) и < 10 р
    ps = [p for p in ps if 10 <= p <= 150000]
    if not ps: return None, None
    n = len(ps)
    median = ps[n//2] if n%2==1 else round((ps[n//2-1]+ps[n//2])/2,2)
    avg = round(sum(ps)/n, 2)
    return avg, median

def main():
    print(">>> total queries:", len(QUERIES), flush=True)
    rows = []
    for i, q in enumerate(QUERIES, 1):
        try:
            print(f"[{i}/{len(QUERIES)}] query: {q}", flush=True)
            prods = search_first_page(q)
            print(f"  • items_on_page={len(prods)}", flush=True)
            prices = [p["price"] for p in prods]
            avg_price, med_price = robust_price_stats(prices)

            ids    = [p["nmId"] for p in prods]
            time.sleep(PAUSE)
            dims   = fetch_dims(ids)
            Ls = [v[0] for v in dims.values()]
            Ws = [v[1] for v in dims.values()]
            Hs = [v[2] for v in dims.values()]
            row = {
                "query": q,
                "items_on_page": len(prods),
                "avg_price": avg_price,
                "median_price": med_price,
                "avg_len": mean(Ls),
                "avg_wid": mean(Ws),
                "avg_hei": mean(Hs),
                "dims_coverage_%": round(100 * (len(dims) / max(1,len(prods))), 1),
            }
            rows.append(row)
            print("  ✓", row, flush=True)
