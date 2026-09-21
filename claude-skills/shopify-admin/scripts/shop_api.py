"""Доступ к Admin API магазина ARTMELLIO через client credentials.

Токен живёт 24 часа, поэтому берём его при каждом запуске и кладём в кэш-файл.
"""
import io
import json
import re
import time
from pathlib import Path

import requests

STORE = "kmfmxn-r4"
API = "2026-07"
KEYS = Path(r"C:\Users\User\Desktop\shopy api.txt")
CACHE = Path(r"C:\Users\User\dolphin_anty\shopify_token.json")


def creds():
    raw = KEYS.read_text(encoding="utf-8-sig", errors="replace")
    cid = re.search(r"\b[0-9a-f]{32}\b", raw)
    sec = re.search(r"\bshp(?:ss|at|ca)_[A-Za-z0-9_-]+", raw)
    if not (cid and sec):
        raise SystemExit("в файле нет пары client_id / client_secret")
    return cid.group(0), sec.group(0)


def token():
    if CACHE.exists():
        d = json.loads(CACHE.read_text())
        if d.get("exp", 0) > time.time() + 300:
            return d["token"]
    cid, sec = creds()
    r = requests.post(
        f"https://{STORE}.myshopify.com/admin/oauth/access_token",
        json={"client_id": cid, "client_secret": sec, "grant_type": "client_credentials"},
        timeout=60,
    )
    if r.status_code != 200:
        raise SystemExit(f"токен не выдан: HTTP {r.status_code} {r.text[:200]}")
    d = r.json()
    tok = d["access_token"]
    CACHE.write_text(json.dumps({"token": tok, "exp": time.time() + d.get("expires_in", 86400)}))
    return tok


def gql(query, variables=None, tok=None):
    tok = tok or token()
    r = requests.post(
        f"https://{STORE}.myshopify.com/admin/api/{API}/graphql.json",
        headers={"X-Shopify-Access-Token": tok, "Content-Type": "application/json"},
        json={"query": query, "variables": variables or {}},
        timeout=120,
    )
    d = r.json()
    if "errors" in d:
        raise SystemExit(f"GraphQL: {json.dumps(d['errors'], ensure_ascii=False)[:400]}")
    return d["data"]


if __name__ == "__main__":
    data = gql("{ shop { name myshopifyDomain currencyCode } }")
    print(data)
