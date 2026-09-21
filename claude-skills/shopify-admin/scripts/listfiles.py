from shop_api import gql
Q = """
query($id: ID!, $cursor: String) {
  theme(id: $id) { files(first: 250, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    nodes { filename size } } }
}
"""
names, cur = [], None
while True:
    d = gql(Q, {"id": "gid://shopify/OnlineStoreTheme/188705603964", "cursor": cur})["theme"]["files"]
    names += [(n["filename"], n["size"]) for n in d["nodes"]]
    if not d["pageInfo"]["hasNextPage"]:
        break
    cur = d["pageInfo"]["endCursor"]
print("файлов:", len(names))
for f, s in names:
    if f.startswith("templates/") or "header-group" in f:
        print(f" {f:44} {s}")
