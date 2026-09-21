# -*- coding: utf-8 -*-
"""Лестница автоматических скидок на набор. Пороги в PLN (валюта магазина), 1 USD ~ 3.606 PLN."""
import json
from shop_api import gql

RATE = 3.606
# (название, порог в USD, процент)
TIERS = [
    ("Set 5% - from $85",  85,  5),
    ("Set 7% - from $120", 120, 7),
    ("Set 8% - from $155", 155, 8),
    ("Set 10% - from $200", 200, 10),
]

M = """
mutation($d: DiscountAutomaticBasicInput!) {
  discountAutomaticBasicCreate(automaticBasicDiscount: $d) {
    automaticDiscountNode { id automaticDiscount { ... on DiscountAutomaticBasic { title status } } }
    userErrors { field message }
  }
}
"""

existing = gql("""{ discountNodes(first:50){ nodes { id discount { ... on DiscountAutomaticBasic { title } } } } }""")
have = {n["discount"].get("title") for n in existing["discountNodes"]["nodes"] if n.get("discount")}

for title, usd, pct in TIERS:
    if title in have:
        print("уже есть:", title); continue
    d = {
        "title": title,
        "startsAt": "2026-08-24T00:00:00Z",
        "combinesWith": {"orderDiscounts": False, "productDiscounts": False, "shippingDiscounts": True},
        "minimumRequirement": {"subtotal": {"greaterThanOrEqualToSubtotal": str(round(usd * RATE, 2))}},
        "customerGets": {
            "value": {"percentage": pct / 100.0},
            "items": {"all": True},
        },
    }
    r = gql(M, {"d": d})["discountAutomaticBasicCreate"]
    print(title, "->", json.dumps(r, ensure_ascii=False))
