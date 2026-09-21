import sys
from shop_api import gql

Q = """
query($rt: TranslatableResourceType!) {
  translatableResources(first: 5, resourceType: $rt) {
    nodes { resourceId translatableContent { key value digest locale } }
  }
}
"""
d = gql(Q, {"rt": "ONLINE_STORE_THEME"})
nodes = d["translatableResources"]["nodes"]
print("resourceId:", nodes[0]["resourceId"], "| ключей:", len(nodes[0]["translatableContent"]))
needles = [n.lower() for n in sys.argv[1:]]
for c in nodes[0]["translatableContent"]:
    hay = (c["key"] + " " + (c["value"] or "")).lower()
    if any(n in hay for n in needles):
        print(f"{c['key']}\n    = {c['value']!r}")
