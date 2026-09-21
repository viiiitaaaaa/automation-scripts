import sys
from shop_api import gql
Q = """
query($id: ID!, $names: [String!]) {
  theme(id: $id) {
    files(first: 10, filenames: $names) {
      nodes { filename size body { ... on OnlineStoreThemeFileBodyText { content } } }
    }
  }
}
"""
d = gql(Q, {"id": "gid://shopify/OnlineStoreTheme/188705603964", "names": sys.argv[1:]})
for n in d["theme"]["files"]["nodes"]:
    c = (n["body"] or {}).get("content", "")
    print("==", n["filename"], "размер", n["size"])
    print(c[:400])
