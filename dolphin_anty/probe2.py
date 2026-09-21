# -*- coding: utf-8 -*-
import json, collections
from shop_api import gql

# 1. все namespace/key метаполей по каталогу
Q = """
query($cursor: String) {
  products(first: 100, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes { title metafields(first: 40) { nodes { namespace key value } } }
  }
}
"""
cnt = collections.Counter()
nonzero = []
cur = None
while True:
    d = gql(Q, {"cursor": cur})
    b = d["data"]["products"]
    for p in b["nodes"]:
        for m in p["metafields"]["nodes"]:
            cnt[m["namespace"] + "/" + m["key"]] += 1
            v = str(m["value"])
            if "rating" in m["key"] or "review" in m["key"]:
                if "number_of_reviews" in v:
                    try:
                        j = json.loads(v)
                        if int(j.get("number_of_reviews") or 0) > 0:
                            nonzero.append((p["title"], j.get("number_of_reviews"), j.get("average_rating")))
                    except Exception:
                        pass
    if not b["pageInfo"]["hasNextPage"]:
        break
    cur = b["pageInfo"]["endCursor"]
print("МЕТАПОЛЯ (ключ -> у скольких товаров):")
for k, v in cnt.most_common():
    print(f"   {k:45s} {v}")
print("товаров с отзывами != 0:", len(nonzero))

# 2. установленные приложения
for q in ['{ appInstallations(first:50){ nodes { app { title } } } }']:
    r = gql(q)
    print("\nAPPS:", json.dumps(r)[:600])
