# Сбор 1688 через Apify zen-studio/1688-wholesale-scraper (без входа в 1688). Потолок трат на запуск — MAX_USD.
# python zapusk.py  -> cj\apify1688\raw_<дата>.json
import json, os, sys, time, datetime, requests
from dotenv import dotenv_values

e = dotenv_values(r'C:\Users\User\lead-engine\.env')
TOK = e.get('APIFY_TOKEN') or e.get('APIFY_API_TOKEN')
H = {'Authorization': 'Bearer ' + TOK}
D = os.path.dirname(os.path.abspath(__file__))
MAX_USD = float(sys.argv[1]) if len(sys.argv) > 1 else 2.0
KW = sys.argv[2].split(',') if len(sys.argv) > 2 else ['半身裙女秋冬', '针织衫女秋冬', '连衣裙女秋冬']
PER = int(sys.argv[3]) if len(sys.argv) > 3 else 80
INP = {
    'keywords': KW,
    'maxResults': PER, 'sortBy': 'bestSelling',
    'priceMin': 35, 'priceMax': 70, 'minOrderQuantity': 1,
    'merchantType': 'any', 'includeSupplierIntelligence': True,
    'includeSkuDetails': False, 'includeDescriptionHtml': False, 'proxyCountryMode': 'rotate',
}
r = requests.post('https://api.apify.com/v2/acts/zen-studio~1688-wholesale-scraper/runs',
                  params={'maxTotalChargeUsd': MAX_USD}, headers=H, json=INP, timeout=60).json()['data']
rid, ds = r['id'], r['defaultDatasetId']
print('запуск', rid, '| потолок $', MAX_USD, flush=True)
t0 = time.time()
while True:
    try:
        s = requests.get(f'https://api.apify.com/v2/actor-runs/{rid}', headers=H, timeout=90).json()['data']
        n = requests.get(f'https://api.apify.com/v2/datasets/{ds}', headers=H, timeout=90).json()['data'].get('itemCount', 0)
    except Exception as ex:   # обрыв сети/VPN — просто ждём и пробуем снова, запуск на Apify продолжается
        print('связь оборвалась, повтор…', ex.__class__.__name__, flush=True); time.sleep(20); continue
    print(f"{s['status']} | собрано {n} из ~{PER*len(KW)} | ${s.get('usageTotalUsd') or 0:.2f} | {int(time.time()-t0)} с", flush=True)
    if s['status'] in ('SUCCEEDED', 'FAILED', 'ABORTED', 'TIMED-OUT'):
        break
    time.sleep(30)
for i in range(6):
    try:
        items = requests.get(f'https://api.apify.com/v2/datasets/{ds}/items', headers=H, params={'clean': 'true'}, timeout=240).json(); break
    except Exception:
        print('скачивание оборвалось, повтор…', flush=True); time.sleep(10)
out = os.path.join(D, f'raw_{datetime.datetime.now():%Y%m%d_%H%M}.json')
json.dump(items, open(out, 'w', encoding='utf-8'), ensure_ascii=False)
print('готово:', len(items), 'товаров ->', out)
