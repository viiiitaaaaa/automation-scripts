# -*- coding: utf-8 -*-
import json
from shop_api import gql
Q = """
{ products(first: 3, query: "created_at:>2026-08-27", sortKey: CREATED_AT, reverse: true) {
    nodes { id title vendor tags handle
            metafields(first:20){ nodes { namespace key value } }
            descriptionHtml } } }
"""
d = gql(Q)
for p in d["data"]["products"]["nodes"]:
    print("TITLE:", p["title"][:70])
    print("  vendor:", p["vendor"], "| tags:", p["tags"])
    print("  mf:", [(m["namespace"],m["key"]) for m in p["metafields"]["nodes"]])
    print("  desc:", p["descriptionHtml"][:200].replace("\n"," "))
    print()
