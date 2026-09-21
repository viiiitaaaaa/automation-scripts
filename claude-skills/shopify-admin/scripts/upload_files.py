"""Загрузить локальные картинки в Files магазина под латинскими именами.

Имя файла важно: в шаблоне темы картинка адресуется как
shopify://shop_images/<имя>, а кириллица в ссылке ломается.
"""
import sys
import time
from pathlib import Path

import requests

from shop_api import gql

STAGE = """
mutation($input: [StagedUploadInput!]!) {
  stagedUploadsCreate(input: $input) {
    stagedTargets { url resourceUrl parameters { name value } }
    userErrors { message }
  }
}
"""
CREATE = """
mutation($files: [FileCreateInput!]!) {
  fileCreate(files: $files) {
    files { id fileStatus alt ... on MediaImage { image { url } } }
    userErrors { field message }
  }
}
"""


def upload(local_path: Path, target_name: str, alt: str):
    st = gql(STAGE, {"input": [{
        "filename": target_name, "mimeType": "image/png",
        "httpMethod": "POST", "resource": "FILE",
    }]})["stagedUploadsCreate"]
    if st["userErrors"]:
        raise SystemExit(st["userErrors"])
    t = st["stagedTargets"][0]
    # хранилище Google иногда рвёт TLS на первой попытке — повторяем
    blob = local_path.read_bytes()
    last = None
    for attempt in range(5):
        try:
            files = {p["name"]: (None, p["value"]) for p in t["parameters"]}
            files["file"] = (target_name, blob, "image/png")
            r = requests.post(t["url"], files=files, timeout=300)
            if r.status_code in (200, 201, 204):
                break
            last = f"{r.status_code} {r.text[:150]}"
        except requests.exceptions.RequestException as e:
            last = type(e).__name__
        time.sleep(3 * (attempt + 1))
    else:
        raise SystemExit(f"загрузка не прошла: {last}")

    res = gql(CREATE, {"files": [{
        "originalSource": t["resourceUrl"], "alt": alt,
        "contentType": "IMAGE", "filename": target_name,
    }]})["fileCreate"]
    if res["userErrors"]:
        raise SystemExit(res["userErrors"])
    return res["files"][0]["id"]


if __name__ == "__main__":
    src_dir = Path(sys.argv[1])
    prefix = sys.argv[2] if len(sys.argv) > 2 else "hero"
    paths = sorted(src_dir.glob("*.png"))
    for i, p in enumerate(paths, 1):
        name = f"{prefix}-{i}.png"
        fid = upload(p, name, f"ARTMELLIO interior {i}")
        print(f"{p.name[:34]:36} -> {name}  {fid}")
        time.sleep(1)
