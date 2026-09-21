"""Admin API клиент магазина ARTMELLIO.

Токен берётся по client credentials, кэшируется на 24ч в shopify_token.json.
Использование:
    python shop_api.py            -> печатает токен (для --password в Shopify CLI)
    from shop_api import gql; gql("{ shop { name } }")
"""
import json
import os
import time
import urllib.request

SHOP = "kmfmxn-r4.myshopify.com"
API_VERSION = "2026-07"
CREDS = r"C:\Users\User\Desktop\Новая папка (4)\shopy api.txt"
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shopify_token.json")


def _post(url, payload, headers, attempts=5):
    """POST с повтором: сеть до Shopify периодически отваливается по таймауту."""
    last = None
    for n in range(attempts):
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(), method="POST",
            headers={"Content-Type": "application/json", **headers},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:      # лимит или сбой на стороне Shopify
                last = e
            else:
                raise
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last = e
        time.sleep(2 ** n)                          # 1, 2, 4, 8, 16 секунд
    raise last


def get_token(force=False):
    if not force and os.path.exists(CACHE):
        cached = json.load(open(CACHE))
        if cached.get("expires_at", 0) > time.time() + 300:
            return cached["access_token"]

    with open(CREDS, encoding="utf-8") as f:
        client_id, client_secret = [l.strip() for l in f if l.strip()][:2]

    data = _post(
        f"https://{SHOP}/admin/oauth/access_token",
        {"client_id": client_id, "client_secret": client_secret,
         "grant_type": "client_credentials"},
        {},
    )
    data["expires_at"] = time.time() + data.get("expires_in", 86400)
    json.dump(data, open(CACHE, "w"))
    return data["access_token"]


def gql(query, variables=None):
    return _post(
        f"https://{SHOP}/admin/api/{API_VERSION}/graphql.json",
        {"query": query, "variables": variables or {}},
        {"X-Shopify-Access-Token": get_token()},
    )


if __name__ == "__main__":
    print(get_token(force="--force" in os.sys.argv))
