"""Загрузить локальный файл как главное изображение товара."""
import sys
import time

import requests

from shop_api import gql

PRODUCT_ID = sys.argv[1]
PATH = sys.argv[2]
ALT = sys.argv[3] if len(sys.argv) > 3 else ""

STAGE = """
mutation($input: [StagedUploadInput!]!) {
  stagedUploadsCreate(input: $input) {
    stagedTargets { url resourceUrl parameters { name value } }
    userErrors { message }
  }
}
"""

CREATE = """
mutation($id: ID!, $media: [CreateMediaInput!]!) {
  productCreateMedia(productId: $id, media: $media) {
    media { ... on MediaImage { id status } }
    mediaUserErrors { field message }
  }
}
"""

REORDER = """
mutation($id: ID!, $moves: [MoveInput!]!) {
  productReorderMedia(id: $id, moves: $moves) { job { id } userErrors { message } }
}
"""

QUERY_MEDIA = """
query($id: ID!) {
  product(id: $id) { media(first: 30) { nodes { id ... on MediaImage { image { width height } } } } }
}
"""

gid = f"gid://shopify/Product/{PRODUCT_ID}"

st = gql(STAGE, {"input": [{
    "filename": PATH.split("\\")[-1].split("/")[-1],
    "mimeType": "image/jpeg",
    "httpMethod": "POST",
    "resource": "IMAGE",
}]})["stagedUploadsCreate"]
if st["userErrors"]:
    raise SystemExit(st["userErrors"])
target = st["stagedTargets"][0]

files = {p["name"]: (None, p["value"]) for p in target["parameters"]}
files["file"] = (PATH.split("\\")[-1], open(PATH, "rb"), "image/jpeg")
r = requests.post(target["url"], files=files, timeout=120)
print("загрузка:", r.status_code)

res = gql(CREATE, {"id": gid, "media": [{
    "originalSource": target["resourceUrl"],
    "alt": ALT,
    "mediaContentType": "IMAGE",
}]})["productCreateMedia"]
if res["mediaUserErrors"]:
    raise SystemExit(res["mediaUserErrors"])
new_id = res["media"][0]["id"]
print("media создан:", new_id)

# ждём, пока Shopify обработает файл, иначе перестановка отвалится
for _ in range(20):
    time.sleep(3)
    nodes = gql(QUERY_MEDIA, {"id": gid})["product"]["media"]["nodes"]
    me = [n for n in nodes if n["id"] == new_id]
    if me and me[0].get("image"):
        print("обработано:", me[0]["image"])
        break

mv = gql(REORDER, {"id": gid, "moves": [{"id": new_id, "newPosition": "0"}]})["productReorderMedia"]
print("перестановка:", mv["userErrors"] or "ок")
