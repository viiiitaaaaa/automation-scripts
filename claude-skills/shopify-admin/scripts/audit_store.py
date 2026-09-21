# -*- coding: utf-8 -*-
"""Снимок состояния магазина для аудита: страницы, меню, коллекции, политики, тема."""
import json, sys
from shop_api import gql

out = {}

def safe(name, q, v=None):
    try:
        out[name] = gql(q, v) if v else gql(q)
    except Exception as e:
        out[name] = {"ERROR": str(e)[:300]}

safe("shop", "{ shop { name myshopifyDomain primaryDomain { url } currencyCode } }")

safe("pages", """{ pages(first:50) { nodes { title handle isPublished bodySummary } } }""")

safe("menus", """{ menus(first:20) { nodes { handle title items { title url type items { title url } } } } }""")

safe("collections", """{ collections(first:50) { nodes { title handle productsCount { count } image { url } } } }""")

#removed

safe("products_count", """{ productsCount { count } }""")

safe("theme", """{ themes(first:5, roles:[MAIN]) { nodes { id name role } } }""")

print(json.dumps(out, ensure_ascii=False, indent=1)[:20000])
