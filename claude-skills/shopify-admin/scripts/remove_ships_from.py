# -*- coding: utf-8 -*-
"""Убирает у товаров опцию «Ships From» — она раскрывала происхождение покупателю."""
import json
from shop_api import gql

M = """
mutation($productId: ID!, $options: [ID!]!) {
  productOptionsDelete(productId: $productId, options: $options, strategy: POSITION) {
    deletedOptionsIds
    userErrors { field message }
  }
}
"""

products = gql("{ products(first:250){ nodes { id handle options { id name values } } } }")["products"]["nodes"]
targets = [(p, o) for p in products for o in p["options"] if o["name"].lower().startswith("ship")]
print("к обработке:", len(targets))

ok, bad = 0, []
for p, o in targets:
    if len(o["values"]) > 1:
        bad.append((p["handle"], "несколько значений — пропущено"))
        continue
    r = gql(M, {"productId": p["id"], "options": [o["id"]]})["productOptionsDelete"]
    if r["userErrors"]:
        bad.append((p["handle"], r["userErrors"]))
    else:
        ok += 1

print("удалено:", ok)
for b in bad:
    print("  проблема:", b)
