import io, sys
from shop_api import gql

M = """
mutation($id: ID!, $files: [OnlineStoreThemeFilesUpsertFileInput!]!) {
  themeFilesUpsert(themeId: $id, files: $files) {
    upsertedThemeFiles { filename }
    userErrors { filename message }
  }
}
"""
files = []
for path in sys.argv[1:]:
    local = r"C:\Users\User\shopify-decor-theme" + "\\" + path.replace("/", "\\")
    content = io.open(local, encoding="utf-8-sig").read()
    files.append({"filename": path, "body": {"type": "TEXT", "value": content}})

res = gql(M, {"id": "gid://shopify/OnlineStoreTheme/188705603964", "files": files})["themeFilesUpsert"]
print("залито:", [f["filename"] for f in res["upsertedThemeFiles"]])
print("ошибки:", res["userErrors"])
