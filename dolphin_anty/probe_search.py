# -*- coding: utf-8 -*-
"""Ловим ровно запрос списка товаров Dsers: метод, тело, форма ответа."""
import sys, time, json, re
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
T = "v2/search"
got = {}

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()

    def on_req(r):
        if T in r.url:
            got.setdefault("req", {"method": r.method, "url": r.url,
                                   "post": r.post_data or "",
                                   "hdrs": {k: v for k, v in r.headers.items()
                                            if k.lower() in ("content-type", "authorization")}})

    def on_resp(r):
        if T in r.url and "resp" not in got:
            try:
                got["resp"] = r.json()
            except Exception:
                pass

    pg.on("request", on_req)
    pg.on("response", on_resp)
    pg.goto("https://www.dsers.com/application/import_list",
            wait_until="domcontentloaded", timeout=90_000)
    pg.bring_to_front()
    for _ in range(40):
        time.sleep(2)
        if "resp" in got:
            break

print("ЗАПРОС:", json.dumps(got.get("req"), ensure_ascii=False)[:800])
j = got.get("resp")
if not j:
    print("ответ не пойман")
    raise SystemExit(0)

def walk(o, path="", depth=0):
    """Ищем в ответе список товаров и поля с номером товара AliExpress."""
    if depth > 4:
        return
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                print(f"  список: {path}.{k}  элементов {len(v)}")
                print(f"     ключи: {list(v[0].keys())[:22]}")
                for kk, vv in v[0].items():
                    if re.search(r"ali|prod|supplier|url|link|title|id", kk, re.I):
                        print(f"       {kk} = {str(vv)[:60]}")
                return
            if isinstance(v, (dict,)):
                walk(v, f"{path}.{k}", depth + 1)
            elif re.search(r"total|count", k, re.I):
                print(f"  {path}.{k} = {v}")

print("\nверхние ключи ответа:", list(j.keys()))
walk(j)
