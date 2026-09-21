"""Разведка: достаются ли отзывы и картинки с карточки AliExpress.

Пробуем два пути:
  1) официальный фид отзывов feedback.aliexpress.com (JSON) — открываем вкладкой;
  2) картинки товара из HTML карточки (нужны для сопоставления с Shopify).
"""
import json
import re
import sys
import time
from pathlib import Path

CDP = Path(__file__).with_name("cdp.json")
sys.stdout.reconfigure(encoding="utf-8")
cdp = json.loads(CDP.read_text(encoding="utf-8"))

ITEM = sys.argv[1] if len(sys.argv) > 1 else "3256805220240301"
PRODUCT_URL = f"https://www.aliexpress.com/item/{ITEM}.html"
FEED = ("https://feedback.aliexpress.com/pc/searchEvaluation.do"
        f"?productId={ITEM}&lang=en_US&country=GB&page=1&pageSize=10&filter=all&sort=complex_default")

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(cdp["url"])
    ctx = b.contexts[0]
    pg = ctx.new_page()

    # --- карточка: картинки ---
    pg.goto(PRODUCT_URL, wait_until="domcontentloaded", timeout=90_000)
    time.sleep(6)
    print("URL после перехода:", pg.url[:110])
    if ".ru" in pg.url.split("/")[2]:
        print("[x] увело на .ru — прокси не тот"); sys.exit(2)
    html = pg.content()
    imgs = sorted(set(re.findall(r"(S[0-9a-f]{32}[A-Za-z])\.(?:jpg|webp|png)", html)))
    print(f"хешей картинок на карточке: {len(imgs)}")
    for i in imgs[:5]:
        print("   ", i)
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    print("заголовок:", (title.group(1)[:80] if title else "?"))

    # --- отзывы ---
    # сырой ответ через контекст браузера — куки и прокси профиля сохраняются
    resp = ctx.request.get(FEED, timeout=60_000)
    body = resp.text()
    print(f"\nстатус фида: {resp.status}, длина {len(body)}")
    try:
        data = json.loads(body)
    except Exception as e:
        print("[x] не JSON:", e)
        pg.close(); sys.exit(1)

    ev = (data.get("data") or {}).get("evaViewList") or []
    print(f"\nотзывов в ответе: {len(ev)}")
    for r in ev[:3]:
        print(f"   {r.get('buyerEval')}/100 | {r.get('buyerCountry')} | "
              f"{r.get('buyerName')} | {str(r.get('buyerFeedback'))[:60]} | "
              f"фото: {len(r.get('images') or [])}")
    total = (data.get("data") or {}).get("totalNum")
    print("всего отзывов у товара:", total)
    pg.close()
