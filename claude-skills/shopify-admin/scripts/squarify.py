"""Привести главные фото товаров к квадрату.

Направление обрезки задаётся вручную по каждому кадру: у части фото предмет
стоит в нижней части, и центральная обрезка срезала бы его.
"""
import io
import json
import time
import urllib.request

import requests
from PIL import Image

from shop_api import gql

# индекс из nonsquare.json -> откуда брать квадрат
PLAN = {0: "center", 1: "bottom", 3: "center", 4: "center", 5: "center",
        6: "bottom", 7: "bottom", 8: "center", 9: "center"}

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
    media { ... on MediaImage { id } }
    mediaUserErrors { message }
  }
}
"""
REORDER = """
mutation($id: ID!, $moves: [MoveInput!]!) {
  productReorderMedia(id: $id, moves: $moves) { userErrors { message } }
}
"""
MEDIA = """
query($id: ID!) { product(id: $id) { media(first: 30) { nodes { id ... on MediaImage { image { width height } } } } } }
"""


def square(path, out, where):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    s = min(w, h)
    if w >= h:
        box = ((w - s) // 2, 0, (w - s) // 2 + s, s)
    elif where == "bottom":
        box = (0, h - s, w, h)
    else:
        box = (0, (h - s) // 2, w, (h - s) // 2 + s)
    im.crop(box).save(out, quality=92)
    return Image.open(out).size


def upload(gid, path, alt):
    st = gql(STAGE, {"input": [{"filename": path, "mimeType": "image/jpeg",
                                "httpMethod": "POST", "resource": "IMAGE"}]})["stagedUploadsCreate"]
    t = st["stagedTargets"][0]
    files = {p["name"]: (None, p["value"]) for p in t["parameters"]}
    files["file"] = (path, open(path, "rb"), "image/jpeg")
    requests.post(t["url"], files=files, timeout=180)
    res = gql(CREATE, {"id": gid, "media": [{"originalSource": t["resourceUrl"],
                                             "alt": alt, "mediaContentType": "IMAGE"}]})
    if res["productCreateMedia"]["mediaUserErrors"]:
        raise SystemExit(res["productCreateMedia"]["mediaUserErrors"])
    mid = res["productCreateMedia"]["media"][0]["id"]
    for _ in range(20):
        time.sleep(3)
        nodes = gql(MEDIA, {"id": gid})["product"]["media"]["nodes"]
        if any(n["id"] == mid and n.get("image") for n in nodes):
            break
    gql(REORDER, {"id": gid, "moves": [{"id": mid, "newPosition": "0"}]})
    return mid


items = json.load(io.open("nonsquare.json", encoding="utf-8"))

for it in items:
    gid = f"gid://shopify/Product/{it['id']}"
    idx = it["i"]

    if idx not in PLAN:
        # часы: главным ставим готовое квадратное фото из галереи, коллаж уходит вниз
        nodes = gql(MEDIA, {"id": gid})["product"]["media"]["nodes"]
        sq = [n for n in nodes if n.get("image") and n["image"]["width"] == n["image"]["height"]]
        if sq:
            gql(REORDER, {"id": gid, "moves": [{"id": sq[0]["id"], "newPosition": "0"}]})
            print(f"{idx} {it['title'][:34]}: главным поставлено фото из галереи")
        continue

    src = f"ns_{idx}.jpg"
    urllib.request.urlretrieve(it["src"], src)
    out = f"sq_{idx}.jpg"
    size = square(src, out, PLAN[idx])
    upload(gid, out, it["title"])
    print(f"{idx} {it['title'][:34]}: {it['w']}x{it['h']} -> {size[0]}x{size[1]} ({PLAN[idx]})")
