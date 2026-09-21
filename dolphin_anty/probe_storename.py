"""Разведка: откуда взять название магазина на странице."""
import json
import sys
import time

from playwright.sync_api import sync_playwright

from dolphin import DolphinLocal, start_with_retry
from shots import STORE_URL

PROFILE = int(sys.argv[1]) if len(sys.argv) > 1 else 828976678

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, PROFILE)["automation"]

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}")
    ctx = b.contexts[0] if b.contexts else b.new_context()
    page = ctx.new_page()
    page.goto(STORE_URL, wait_until="domcontentloaded", timeout=90_000)
    time.sleep(6)

    print(json.dumps(page.evaluate("""() => ({
        title: document.title,
        ogTitle: document.querySelector('meta[property="og:title"]')?.content,
        h1: [...document.querySelectorAll('h1,h2')].slice(0,5).map(e => e.innerText.trim()),
        storeish: [...document.querySelectorAll('[class*="store" i],[class*="shop" i]')]
            .map(e => (e.innerText || '').trim())
            .filter(t => t && t.length < 60)
            .slice(0, 12)
    })""" ), ensure_ascii=False, indent=1))
    page.close()
    b.close()
