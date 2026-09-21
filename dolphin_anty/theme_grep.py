"""Поиск текста по файлам темы Shopify через Admin API.

    python theme_grep.py <theme_id> "Continue shopping"
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
from shop_api import gql

theme_id, needle = sys.argv[1], sys.argv[2]
GID = f"gid://shopify/OnlineStoreTheme/{theme_id}"

LIST = """query($id: ID!, $after: String) {
  theme(id: $id) { files(first: 250, after: $after) {
    pageInfo { hasNextPage endCursor } nodes { filename } } } }"""

BODY = """query($id: ID!, $f: [String!]) {
  theme(id: $id) { files(filenames: $f, first: 50) { nodes { filename
    body { ... on OnlineStoreThemeFileBodyText { content } } } } } }"""

names, after = [], None
while True:
    d = gql(LIST, {"id": GID, "after": after})
    f = d["data"]["theme"]["files"]
    names += [n["filename"] for n in f["nodes"]]
    if not f["pageInfo"]["hasNextPage"]:
        break
    after = f["pageInfo"]["endCursor"]

targets = [n for n in names if n.endswith(".liquid") or n.endswith(".json")]
targets = [n for n in targets if not n.startswith("locales/")]
print(f"файлов к просмотру: {len(targets)}")

hits = 0
for i in range(0, len(targets), 40):
    chunk = targets[i:i + 40]
    d = gql(BODY, {"id": GID, "f": chunk})
    for n in d["data"]["theme"]["files"]["nodes"]:
        c = (n["body"] or {}).get("content") or ""
        for ln, line in enumerate(c.splitlines(), 1):
            if needle.lower() in line.lower():
                print(f"{n['filename']}:{ln}: {line.strip()[:150]}")
                hits += 1
print("совпадений:", hits)
