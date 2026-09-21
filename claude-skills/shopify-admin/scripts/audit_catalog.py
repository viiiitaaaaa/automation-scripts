# -*- coding: utf-8 -*-
"""Проверка каталога: длинные названия, пустые описания, дубли, теги, фото, статус."""
import collections
from shop_api import gql

r = gql("""{ products(first:250){ nodes { handle title descriptionHtml tags status
  featuredMedia { preview { image { width height } } } } } }""")["products"]["nodes"]

print("всего товаров:", len(r))
checks = [
    ("названия длиннее 45 символов", [p["title"] for p in r if len(p["title"]) > 45]),
    ("описание короче 120 символов", [p["title"] for p in r if len(p["descriptionHtml"] or "") < 120]),
    ("повторяющиеся названия", [t for t, n in collections.Counter(p["title"] for p in r).items() if n > 1]),
    ("без тега cat:", [p["title"] for p in r if not any(t.startswith("cat:") for t in p["tags"])]),
    ("без тега style:", [p["title"] for p in r if not any(t.startswith("style:") for t in p["tags"])]),
    ("неквадратное главное фото", [p["title"] for p in r if p["featuredMedia"]
                                   and p["featuredMedia"]["preview"]["image"]["width"]
                                   != p["featuredMedia"]["preview"]["image"]["height"]]),
    ("не ACTIVE", [p["title"] for p in r if p["status"] != "ACTIVE"]),
]
for name, items in checks:
    print(f"{name}: {len(items)}")
    for t in items[:6]:
        print("   ", t[:60])
