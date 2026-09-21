# -*- coding: utf-8 -*-
import json
from shop_api import gql
rows = json.load(open("catalog.json", encoding="utf-8"))
USD = 3.606; lim = 75*USD
# кто из них "новый импорт" - без метаполей artmellio
Q = """
query($cursor: String) {
  products(first: 100, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes { id createdAt vendor
            mf: metafield(namespace:"artmellio", key:"style") { value } }
  }
}
"""
info = {}; cur=None
while True:
    d = gql(Q, {"cursor": cur}); b = d["data"]["products"]
    for p in b["nodes"]:
        info[p["id"]] = (p["createdAt"][:10], bool(p.get("mf")), p["vendor"])
    if not b["pageInfo"]["hasNextPage"]: break
    cur = b["pageInfo"]["endCursor"]

new = [r for r in rows if not info[r["id"]][1]]
old = [r for r in rows if info[r["id"]][1]]
print(f"обработанные ранее (есть теги/метаполя): {len(old)}")
print(f"свежий импорт (метаполей нет):          {len(new)}")
import collections
c = collections.Counter(info[r['id']][0] for r in new)
print("\nдаты создания свежего импорта:")
for k,v in sorted(c.items()): print("   ", k, v)
print("\nсвежий импорт по цене:")
print("   до 75$ :", sum(1 for r in new if r["max"]<=lim))
print("   дороже :", sum(1 for r in new if r["max"]>lim))
print("\nранее обработанные по цене:")
print("   до 75$ :", sum(1 for r in old if r["max"]<=lim))
print("   дороже :", sum(1 for r in old if r["max"]>lim))
