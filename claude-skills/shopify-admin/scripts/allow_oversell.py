"""Разрешить продажу при нулевом остатке всем вариантам магазина."""
import time

from shop_api import gql

Q_PRODUCTS = """
query($cursor: String) {
  products(first: 25, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id
      title
      variants(first: 100) { nodes { id inventoryPolicy } }
    }
  }
}
"""

M_UPDATE = """
mutation($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    userErrors { field message }
  }
}
"""

products, cursor = [], None
while True:
    d = gql(Q_PRODUCTS, {"cursor": cursor})["products"]
    products += d["nodes"]
    if not d["pageInfo"]["hasNextPage"]:
        break
    cursor = d["pageInfo"]["endCursor"]

total = sum(len(p["variants"]["nodes"]) for p in products)
deny = sum(1 for p in products for v in p["variants"]["nodes"] if v["inventoryPolicy"] == "DENY")
print(f"товаров: {len(products)}, вариантов: {total}, с запретом продажи: {deny}")

changed = 0
for i, p in enumerate(products, 1):
    vs = [{"id": v["id"], "inventoryPolicy": "CONTINUE"}
          for v in p["variants"]["nodes"] if v["inventoryPolicy"] != "CONTINUE"]
    if not vs:
        continue
    res = gql(M_UPDATE, {"productId": p["id"], "variants": vs})
    errs = res["productVariantsBulkUpdate"]["userErrors"]
    if errs:
        print("ошибка:", p["title"][:40], errs[:2])
    else:
        changed += len(vs)
    if i % 20 == 0:
        print(f"  обработано товаров: {i}/{len(products)}, вариантов изменено: {changed}")
    time.sleep(0.3)

print("итого переведено на продажу при нуле:", changed)
