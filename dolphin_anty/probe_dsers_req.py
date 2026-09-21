# -*- coding: utf-8 -*-
"""Как именно Dsers просит список: метод, тело запроса, форма ответа."""
import sys, time, json, re
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
TARGET = "import-list"
allreq = []
got = {}
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()

    def on_req(r):
        if "bff-api" in r.url:
            allreq.append((r.method, r.url[:110], (r.post_data or "")[:200]))
        if TARGET in r.url and "req" not in got:
            got["req"] = {"method": r.method, "url": r.url, "post": (r.post_data or "")[:600]}

    def on_resp(r):
        if TARGET in r.url and "resp" not in got:
            try:
                j = r.json()
            except Exception:
                return
            got["resp"] = j

    pg.on("request", on_req)
    pg.on("response", on_resp)
    pg.goto("https://www.dsers.com/application/import_list",
            wait_until="domcontentloaded", timeout=90_000)
    pg.bring_to_front()
    for _ in range(20):
        time.sleep(2)
        if "resp" in got:
            break
    if "resp" not in got:
        print("перезагружаю страницу, чтобы поймать запрос", flush=True)
        pg.reload(wait_until="domcontentloaded", timeout=90_000)
        for _ in range(30):
            time.sleep(2)
            if "resp" in got:
                break
    print("--- все запросы к bff-api ---")
    for m, u, pd in allreq[:25]:
        print(f"  {m} {u}")
        if pd:
            print(f"      тело: {pd}")

print("ЗАПРОС:", json.dumps(got.get("req"), ensure_ascii=False, indent=1))
j = got.get("resp")
if j:
    print("\nОТВЕТ, верхние ключи:", list(j.keys()))
    d = j.get("data") or j
    if isinstance(d, dict):
        print("data ключи:", list(d.keys()))
        for k in ("total", "totalCount", "count"):
            if k in d:
                print(f"  {k} =", d[k])
        arr = None
        for k, v in d.items():
            if isinstance(v, list) and v:
                arr = (k, v); break
        if arr:
            print(f"  список в поле '{arr[0]}', элементов {len(arr[1])}")
            print("  ключи одного товара:", list(arr[1][0].keys())[:25])
            one = arr[1][0]
            for k in list(one.keys()):
                if re.search(r"ali|prod|id|url|link|title", k, re.I):
                    print(f"     {k} = {str(one[k])[:70]}")
