"""Открыть встроенное приложение (Flow) отдельной вкладкой.

Playwright не видит кросс-доменные iframe через CDP, поэтому берём src фрейма
и открываем его верхнеуровнево — тогда с приложением можно работать обычными
селекторами.
"""
import json, sys, time
from pathlib import Path

CDP = Path(__file__).with_name("cdp.json")
sys.stdout.reconfigure(encoding="utf-8")
cdp = json.loads(CDP.read_text(encoding="utf-8"))

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(cdp["url"])
    ctx = b.contexts[0]
    host = ctx.pages[0]
    host.bring_to_front()
    time.sleep(2)

    src = host.evaluate("""() => {
        const f = [...document.querySelectorAll('iframe')]
            .filter(x => x.clientWidth > 200)
            .sort((a, b) => b.clientWidth - a.clientWidth)[0];
        return f ? f.src : null;
    }""")
    if not src:
        print("[x] iframe приложения не найден")
        sys.exit(1)
    print("src:", src[:120], "...")

    pg = ctx.new_page()
    pg.goto(src, wait_until="domcontentloaded", timeout=90_000)
    time.sleep(6)
    print("URL  :", pg.url[:120])
    print("TITLE:", pg.title())
    txt = pg.evaluate("() => document.body.innerText")
    print("--- ТЕКСТ ---")
    print(txt[:1200])
