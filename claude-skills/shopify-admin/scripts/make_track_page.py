# -*- coding: utf-8 -*-
import json
from shop_api import gql

BODY = """<p>Every order ships with tracking. You will receive a tracking number by email within 2 working days of placing your order; it usually starts updating 2-4 days after dispatch.</p>"""

# страница уже может существовать
ex = gql('{ pages(first:5, query:"handle:track-order") { nodes { id handle } } }')["pages"]["nodes"]
if ex:
    pid = ex[0]["id"]
    r = gql("""mutation($id:ID!,$p:PageUpdateInput!){ pageUpdate(id:$id, page:$p){ page{ id handle } userErrors{ field message } } }""",
            {"id": pid, "p": {"title": "Track your order", "body": BODY, "templateSuffix": "track-order", "isPublished": True}})
    print("update:", json.dumps(r, ensure_ascii=False))
else:
    r = gql("""mutation($p:PageCreateInput!){ pageCreate(page:$p){ page{ id handle } userErrors{ field message } } }""",
            {"p": {"title": "Track your order", "handle": "track-order", "body": BODY,
                   "templateSuffix": "track-order", "isPublished": True}})
    print("create:", json.dumps(r, ensure_ascii=False))
