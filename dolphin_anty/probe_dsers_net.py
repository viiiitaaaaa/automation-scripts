# -*- coding: utf-8 -*-
"""Какие запросы шлёт Dsers, чтобы получить список товаров. Вывод короткий."""
import sys, time, re
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
seen = []
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()

    def on_resp(r):
        u = r.url
        if re.search(r"\.(png|jpg|jpeg|gif|css|js|woff2?|svg)(\?|$)", u, re.I):
            return
        try:
            ln = len(r.body())
        except Exception:
            ln = -1
        seen.append((ln, r.status, u[:130]))

    pg.on("response", on_resp)
    pg.goto("https://www.dsers.com/application/import_list",
            wait_until="domcontentloaded", timeout=90_000)
    pg.bring_to_front()
    time.sleep(20)
    # прокрутим вниз - список догружается по мере прокрутки
    for _ in range(3):
        pg.mouse.wheel(0, 4000); time.sleep(4)
    time.sleep(6)

print("самые крупные ответы (там и лежит список):")
for ln, st, u in sorted(seen, reverse=True)[:12]:
    print(f"  {ln:>8}  {st}  {u}")
