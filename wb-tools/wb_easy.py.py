# wb_easy.py — «для чайника», расширенные регионы/склады
# Запуск: py -3 -u C:\Users\User\my\wb_easy.py
import csv, time, requests, traceback

OUTFILE = r"C:\Users\User\my\wb_result.csv"
PAUSE = 0.6
APP = 1

# 1) Несколько наборов DEST (склады/регионы WB).
#   ВАЖНО: WB иногда принимает список через запятую как один параметр dest.
DEST_LISTS = [
    "-1029256,-1257786,-2562383,-1128787",  # частый «рабочий» комбо-набор
    "-1257786,-1029256",
    "-1029256",
    "-1257786",
]

# 2) Разные spp — влияет на полноту выдачи
SPPS  = [0, 1, 30]

# 3) Расширенные списки regions (как на сайте, иногда помогают)
REGION_SETS = [
    "68,64,83,4,38,33,70,69,86,75,30,40,1,80,71",
    "68,64,83,4,38,33,70,69,86,75,30,40,1,80,71,66,31,82",
    "64,68,31,66,82,83,4,38,33,70,69,86,75,30,40,1,80,71",
]

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

# <<< сюда можно менять/добавлять запросы >>>
QUERIES = [
    "лампа настольная",
    "светильник настольный",
    "термокружка",
    "лежанка для кошек",
    "ланч бокс",
]
# <<< если заработает (станет > 10–20 товаров на запрос) — вставь свой список из 135 строк >>>

def parse_price(p):
    for k in ("salePriceU","priceU"):
        v = p.get(k)
        if isinstance(v,(int,float)) and v>0:
            return round(v/100.0, 2)
    pr = p.get("price") or {}
    for k in ("saleU","totalU","basicU","productU","basic","product"):
        v = pr.get(k)
        if isinstance(v,(int,float)) and v>0:
            return round((v/100.0) if v>10000 else float(v), 2)
    return None

def mean(xs):
    xs = [x for x in xs if isinstance(x,(int,float))]
    return round(sum(xs)/len(xs),2) if xs else None

def try_search_once(url, q, dest_combo, spp, regions):
    params = {
        "appType": APP, "curr": "rub", "dest": dest_combo, "lang": "ru",
        "resultset": "catalog", "sort": "popular", "spp": spp,
        "query": q, "page": 1, "reg": 0, "uiv": 4, "regions": regions,
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=25)
    if r.status_code != 200:
        return []
    d = r.json()
    prods = (d.get("data") or {}).get("products") or d.get("products") or []
    out = []
    for p in prods:
        nm = p.get("id") or p.get("nmId")
        price = parse_price(p)
        if nm and price:
            out.append({"nmId": int(nm), "price": float(price)})
    return out

def search_first_page(q):
    best = []
    # перебираем: эндпоинт × dest-комбо × spp × regions-наборы
    for url in SEARCH_ENDPOINTS:
        for dest_combo in DEST_LISTS:
            for spp in SPPS:
                for regions in REGION_SETS:
                    items = try_search_once(url, q, dest_combo, spp, regions)
                    if len(items) > len(best):
                        best = items
                        # как только набрали >= 50 — это уже «полная» страница
                        if len(best) >= 50:
                            return best
    return best

def fetch_dims(nm_ids):
    if not nm_ids:
        return {}
    ids = ";".join(map(str, nm_ids))
    # для карточек достаточно одного dest/spp, возьмём первый набор
    params = {"appType": APP, "curr": "rub", "dest": DEST_LISTS[0], "spp": SPPS[0], "nm": ids}
    r = requests.get(URL_CARDS, params=params, headers=HEADERS, timeout=25)
    if r.status_code != 200:
        return {}
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

def main():
    print(">>> старт, запросов:", len(QUERIES), flush=True)
    rows=[]
    for i, q in enumerate(QUERIES, 1):
        try:
            print(f"[{i}/{len(QUERIES)}] {q}", flush=True)
            prods = search_first_page(q)
            prices = [p["price"] for p in prods]
            avg_price = mean(prices)

            ids = [p["nmId"] for p in prods]
            time.sleep(PAUSE)
            dims = fetch_dims(ids)
            Ls = [v[0] for v in dims.values()]
            Ws = [v[1] for v in dims.values()]
            Hs = [v[2] for v in dims.values()]

            row = {
                "query": q,
                "items_on_page": len(prods),
                "avg_price": avg_price,
                "avg_len": mean(Ls),
                "avg_wid": mean(Ws),
                "avg_hei": mean(Hs),
                "dims_coverage_%": round(100*(len(dims)/max(1,len(prods))),1),
            }
            print("  ->", row, flush=True)
            rows.append(row)
            time.sleep(PAUSE)
        except Exception as e:
            print("  ! ошибка:", e, flush=True)
            traceback.print_exc()
            rows.append({"query": q, "items_on_page": 0, "avg_price": None,
                         "avg_len": None, "avg_wid": None, "avg_hei": None, "dims_coverage_%": 0.0})
            time.sleep(PAUSE)

    with open(OUTFILE, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["query","items_on_page","avg_price","avg_len","avg_wid","avg_hei","dims_coverage_%"])
        w.writeheader(); w.writerows(rows)

    print(">>> готово ->", OUTFILE, flush=True)

if __name__ == "__main__":
    main()
