# -*- coding: utf-8 -*-
"""Выгрузка каталога: цена, число отзывов, средний рейтинг (Judge.me)."""
import json
from shop_api import gql

Q = """
query($cursor: String) {
  products(first: 100, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id handle title status
      priceRangeV2 { minVariantPrice { amount currencyCode } maxVariantPrice { amount currencyCode } }
      jm: metafield(namespace: "judgeme", key: "review_widget_data") { value }
    }
  }
}
"""

rows, cur = [], None
while True:
    d = gql(Q, {"cursor": cur})
    blk = d["data"]["products"]
    for p in blk["nodes"]:
        n, avg = 0, 0.0
        if p.get("jm") and p["jm"].get("value"):
            try:
                j = json.loads(p["jm"]["value"])
                n = int(j.get("number_of_reviews") or 0)
                avg = float(j.get("average_rating") or 0)
            except Exception:
                pass
        pr = p["priceRangeV2"]
        rows.append({
            "id": p["id"], "handle": p["handle"], "title": p["title"],
            "status": p["status"],
            "min": float(pr["minVariantPrice"]["amount"]),
            "max": float(pr["maxVariantPrice"]["amount"]),
            "cur": pr["minVariantPrice"]["currencyCode"],
            "reviews": n, "rating": avg,
        })
    if not blk["pageInfo"]["hasNextPage"]:
        break
    cur = blk["pageInfo"]["endCursor"]

json.dump(rows, open("catalog.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("всего товаров:", len(rows))
print("валюта:", rows[0]["cur"] if rows else "?")
print("с отзывами (>0):", sum(1 for r in rows if r["reviews"] > 0))
print("рейтинг >= 4.7 :", sum(1 for r in rows if r["rating"] >= 4.7))
print("макс. число отзывов:", max((r["reviews"] for r in rows), default=0))
