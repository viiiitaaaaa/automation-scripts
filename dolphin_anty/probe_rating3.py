# -*- coding: utf-8 -*-
"""Смотрим блок schema.org (JSON-LD) на карточке - там рейтинг, отзывы и цена сразу."""
import json, sys, re, requests
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")
port = json.load(open("cdp.json"))["port"]
ws = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=5).json()["webSocketDebuggerUrl"]
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(ws)
    pg = b.contexts[0].pages[0]
    blocks = pg.evaluate("""() => [...document.querySelectorAll('script[type="application/ld+json"]')]
                                    .map(s => s.textContent)""")
    print("блоков JSON-LD:", len(blocks))
    for i, t in enumerate(blocks):
        try:
            j = json.loads(t)
        except Exception:
            print(i, "не разобрался"); continue
        j = j[0] if isinstance(j, list) and j else j
        print(f"--- блок {i}: type={j.get(chr(64)+chr(116)+chr(121)+chr(112)+chr(101))} ключи={list(j.keys())[:12]}")
        if j.get("@type") == "Product":
            print("   name:", str(j.get("name"))[:60])
            print("   aggregateRating:", json.dumps(j.get("aggregateRating"), ensure_ascii=False))
            print("   offers:", json.dumps(j.get("offers"), ensure_ascii=False)[:300])
