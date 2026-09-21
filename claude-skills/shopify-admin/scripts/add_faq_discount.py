# -*- coding: utf-8 -*-
import json
from shop_api import gql

BLOCK = """
<h3>Set discount</h3>

<p><strong>How does the set discount work?</strong><br>
Pieces are made to be combined, so the more of a set you build, the less it costs. The
discount is applied automatically in the cart and at checkout — no code needed:</p>

<ul>
<li>Order over £64 — 5% off</li>
<li>Order over £90 — 7% off</li>
<li>Order over £116 — 8% off</li>
<li>Order over £150 — 10% off</li>
</ul>

<p>Only one tier applies at a time, and it is always the highest one your order qualifies
for. The cart shows how much more you need to add to reach the next tier, along with a
suggestion of a piece that goes with what you have chosen.</p>
"""

p = gql('{ pages(first:1, query:"handle:faq"){ nodes { id body } } }')["pages"]["nodes"][0]
if "Set discount" in p["body"]:
    print("уже есть")
else:
    body = p["body"] + BLOCK
    r = gql("""mutation($id:ID!,$p:PageUpdateInput!){ pageUpdate(id:$id, page:$p){ page{ handle } userErrors{ field message } } }""",
            {"id": p["id"], "p": {"body": body}})
    print(json.dumps(r, ensure_ascii=False))
