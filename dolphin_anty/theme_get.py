"""Скачать файлы темы Shopify в локальную папку.

    python theme_get.py <theme_id> out_dir file1 [file2 ...]
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
from shop_api import gql

theme_id, out_dir = sys.argv[1], Path(sys.argv[2])
files = sys.argv[3:]
GID = f"gid://shopify/OnlineStoreTheme/{theme_id}"

BODY = """query($id: ID!, $f: [String!]) {
  theme(id: $id) { files(filenames: $f, first: 50) { nodes { filename
    body { ... on OnlineStoreThemeFileBodyText { content } } } } } }"""

out_dir.mkdir(parents=True, exist_ok=True)
d = gql(BODY, {"id": GID, "f": files})
for n in d["data"]["theme"]["files"]["nodes"]:
    p = out_dir / n["filename"].replace("/", "__")
    p.write_text((n["body"] or {}).get("content") or "", encoding="utf-8")
    print("скачан:", n["filename"], "->", p.name)
