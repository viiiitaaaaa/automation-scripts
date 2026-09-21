# -*- coding: utf-8 -*-
import json
from shop_api import gql
BODY = """<p>Questions about an order, a stone or a delivery date? Write to us and we reply within one working day, Monday to Friday.</p>
<p>You can also <a href="/pages/track-order">track your order</a> with the tracking number from your dispatch email.</p>"""
pid = gql('{ pages(first:1, query:"handle:contact"){ nodes { id } } }')["pages"]["nodes"][0]["id"]
r = gql("""mutation($id:ID!,$p:PageUpdateInput!){ pageUpdate(id:$id, page:$p){ page{ title handle } userErrors{ field message } } }""",
        {"id": pid, "p": {"title": "Contact", "body": BODY, "isPublished": True}})
print(json.dumps(r, ensure_ascii=False))
