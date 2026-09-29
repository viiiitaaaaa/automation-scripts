# Сбор 1688 через treg.to (поиск по словам) -> items.json. Каждый удачный запрос ~$0.015.
import json, re, sys, time, os, requests
from dotenv import dotenv_values
env = dotenv_values(r'C:\Users\User\fashion-trend-radar\fashion-trend-radar\.env')
H = {"X-Treg-Token": env["TREG_TOKEN"], "X-Treg-Org": env.get("TREG_ORG", "vi")}
D = os.path.dirname(os.path.abspath(__file__))
KW = ['格子半身裙中长款秋冬', '格纹半身裙', '格子半身裙2026', '不规则格纹半身裙', '格纹半身裙中长款']
PAGES = int(sys.argv[1]) if len(sys.argv) > 1 else 3

def call(kw, page):
    for i in range(4):
        r = requests.get("https://treg.to/call/justoneapi.x.1688-search-item-list-v1", headers=H,
                         params={"keyword": kw, "page": page}, timeout=120)
        d = r.json()
        if d.get('code') == 0: return d
        time.sleep(5)
    return None

def items_of(d):
    out = []
    def walk(o):
        if isinstance(o, dict):
            if 'offerRepurchaseRate' in o: out.append(o)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(d); return out

allit, calls = {}, 0
for kw in KW:
    for p in range(1, PAGES + 1):
        d = call(kw, p); calls += 1
        if not d: print(kw, p, 'не удалось'); continue
        n = 0
        for o in items_of(d):
            if o.get('block') == 'P4P' or o.get('type') == 'bid': continue   # реклама
            oid = str(o.get('offerId') or '')
            if not oid or oid in allit: continue
            t = re.sub('<[^>]+>', '', o.get('title', ''))
            allit[oid] = dict(offer=oid, title=t, kw=kw,
                              rep=o.get('offerRepurchaseRate') or '', shop_rep=(o.get('turnHead') or {}).get('percent', ''),
                              sold=int(o.get('bookedCount') or 0), price=float((o.get('priceInfo') or {}).get('price') or 0),
                              shop=(o.get('shop') or {}).get('text', ''), years=o.get('tpYear') or (o.get('shop') or {}).get('tpYear'),
                              factory=bool(o.get('factoryInspection')), superf=bool(o.get('superFactory')),
                              pic=o.get('offerPicUrl', ''), same=o.get('sameDesignUrl', ''), city=o.get('province', ''))
            n += 1
        print(kw, p, 'новых', n)
json.dump(list(allit.values()), open(os.path.join(D, 'items.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('всего', len(allit), 'запросов', calls)
