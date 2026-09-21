# -*- coding: utf-8 -*-
"""Разведка: где лежат отзывы и рейтинг у товаров."""
import json
from shop_api import gql

q = """
{
  products(first: 5) {
    nodes {
      id
      title
      metafields(first: 30) { nodes { namespace key type value } }
    }
  }
}
"""
d = gql(q)
for p in d["data"]["products"]["nodes"]:
    print(p["title"][:60])
    for m in p["metafields"]["nodes"]:
        print("   ", m["namespace"], "/", m["key"], "=", str(m["value"])[:80])
    print()

# какие приложения установлены
q2 = """
{
  appInstallations(first: 30) {
    nodes { app { title handle } }
  }
}
"""
try:
    d2 = gql(q2)
    print("APPS:")
    for a in d2["data"]["appInstallations"]["nodes"]:
        print("  -", a["app"]["title"], a["app"].get("handle"))
except Exception as e:
    print("apps err:", e)
