# -*- coding: utf-8 -*-
import json
from shop_api import gql

Q = '{ menus(first:20){ nodes { id handle title items { id title type url resourceId items { id title type url resourceId } } } } }'
menus = {m["handle"]: m for m in gql(Q)["menus"]["nodes"]}

def to_input(it):
    d = {"id": it["id"], "title": it["title"], "type": it["type"]}
    if it.get("resourceId"): d["resourceId"] = it["resourceId"]
    else: d["url"] = it["url"]
    if it.get("items"): d["items"] = [to_input(x) for x in it["items"]]
    return d

NEW = {"title": "Track order", "type": "HTTP", "url": "/pages/track-order"}

for h in ("main-menu", "information"):
    m = menus[h]
    items = [to_input(i) for i in m["items"]]
    if any((i.get("url") or "").endswith("/pages/track-order") for i in items):
        print(h, "уже есть"); continue
    items.append(dict(NEW))
    r = gql("""mutation($id:ID!,$t:String!,$h:String!,$i:[MenuItemUpdateInput!]!){
                 menuUpdate(id:$id, title:$t, handle:$h, items:$i){ menu{ handle items{ title url } } userErrors{ field message } } }""",
            {"id": m["id"], "t": m["title"], "h": m["handle"], "i": items})
    print(h, json.dumps(r["menuUpdate"], ensure_ascii=False))
