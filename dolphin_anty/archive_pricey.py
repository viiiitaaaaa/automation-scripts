# -*- coding: utf-8 -*-
"""Архивирует товары со стартовой ценой выше 80$. Возобновляемый."""
import json, time, os
from shop_api import gql

USD = 3.606
LIM = 80 * USD
rows = json.load(open("catalog.json", encoding="utf-8"))
kill = sorted([r for r in rows if r["min"] > LIM], key=lambda x: -x["min"])
json.dump(kill, open("archived_list.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

DONE = "archive_done.json"
done = set(json.load(open(DONE, encoding="utf-8"))) if os.path.exists(DONE) else set()
todo = [r for r in kill if r["id"] not in done]
print(f"всего под архив {len(kill)}, уже сделано {len(done)}, осталось {len(todo)}", flush=True)

M = """
mutation($id: ID!) {
  productUpdate(product: {id: $id, status: ARCHIVED}) {
    product { id status }
    userErrors { field message }
  }
}
"""
bad = []
for i, r in enumerate(todo, 1):
    try:
        d = gql(M, {"id": r["id"]})
    except Exception as e:
        bad.append((r["title"], str(e))); continue
    res = (d.get("data") or {}).get("productUpdate") or {}
    errs = res.get("userErrors") or d.get("errors")
    if errs:
        bad.append((r["title"], errs))
    else:
        done.add(r["id"])
    if i % 20 == 0:
        json.dump(sorted(done), open(DONE, "w"), indent=0)
        print(f"   ...{i}/{len(todo)}", flush=True)
json.dump(sorted(done), open(DONE, "w"), indent=0)
print(f"\nГОТОВО. архивировано всего: {len(done)} из {len(kill)}, ошибок: {len(bad)}", flush=True)
for t, e in bad[:10]:
    print("  ОШИБКА:", t[:50], e, flush=True)
