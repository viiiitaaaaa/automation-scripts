# -*- coding: utf-8 -*-
import sys, json, io
from shop_api import gql
names = ["templates/index.json","sections/footer-group.json","sections/header-group.json","config/settings_data.json"]
q = """query($f:[String!]){ themes(first:1, roles:[MAIN]){ nodes { files(first:10, filenames:$f){ nodes { filename body { ... on OnlineStoreThemeFileBodyText { content } } } } } } }"""
r = gql(q, {"f": names})
for n in r["themes"]["nodes"][0]["files"]["nodes"]:
    p = "dump_" + n["filename"].replace("/","_")
    io.open(p,"w",encoding="utf-8").write(n["body"]["content"])
    print(p, len(n["body"]["content"]))
