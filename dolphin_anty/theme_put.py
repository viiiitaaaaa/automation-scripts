"""Залить локальные файлы в тему Shopify.

    python theme_put.py <theme_id> theme_work sections/main-product.liquid ...
Имя локального файла = путь с "/" заменёнными на "__".
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
from shop_api import gql

theme_id, src_dir = sys.argv[1], Path(sys.argv[2])
files = sys.argv[3:]
GID = f"gid://shopify/OnlineStoreTheme/{theme_id}"

M = """mutation($id: ID!, $files: [OnlineStoreThemeFilesUpsertFileInput!]!) {
  themeFilesUpsert(themeId: $id, files: $files) {
    upsertedThemeFiles { filename }
    userErrors { filename message }
    userErrors { field message } } }"""

payload = []
for name in files:
    local = src_dir / name.replace("/", "__")
    payload.append({"filename": name, "body": {"type": "TEXT", "value": local.read_text(encoding="utf-8")}})

d = gql(M, {"id": GID, "files": payload})
r = (d.get("data") or {}).get("themeFilesUpsert")
if not r:
    print(d)
    raise SystemExit(1)
print("ошибки:", r["userErrors"])
for f in r["upsertedThemeFiles"]:
    print("залит:", f["filename"])
