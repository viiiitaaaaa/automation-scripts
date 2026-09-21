"""Что именно отдаёт 403 на странице приложения Microsoft Clarity в Shopify.

Ловим сетевые ответы, находим iframe приложения, смотрим статус, заголовки и тело.
"""
import json, sys, time
from pathlib import Path

CDP = Path(__file__).with_name("cdp.json")
SHOTS = Path(r"C:\Users\User\AppData\Local\Temp\claude\C--Users-User"
             r"\fe7d07b8-c28f-4c8f-b6c2-711eddff37f2\scratchpad\shots")
sys.stdout.reconfigure(encoding="utf-8")
cdp = json.loads(CDP.read_text(encoding="utf-8"))

URL = "https://admin.shopify.com/store/kmfmxn-r4/apps/microsoft-clarity-prod"

from playwright.sync_api import sync_playwright

interesting = []

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(cdp["url"])
    ctx = b.contexts[0]
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    pg.bring_to_front()

    def on_resp(r):
        try:
            if r.status >= 400 or "clarity" in r.url.lower():
                interesting.append((r.status, r.url[:160], dict(r.headers)))
        except Exception:
            pass

    pg.on("response", on_resp)
    pg.goto(URL, wait_until="domcontentloaded", timeout=90_000)
    time.sleep(12)

    print("URL страницы:", pg.url[:120])
    src = pg.evaluate("""() => [...document.querySelectorAll('iframe')]
        .map(f => ({src: f.src, w: f.clientWidth, h: f.clientHeight}))""")
    print("\niframe на странице:")
    for f in src:
        print(f"   {f['w']}x{f['h']}  {f['src'][:150]}")

    print(f"\nОтветы 4xx/5xx и всё про clarity ({len(interesting)}):")
    seen = set()
    for status, url, hdrs in interesting:
        key = (status, url.split("?")[0])
        if key in seen:
            continue
        seen.add(key)
        print(f"\n  [{status}] {url}")
        for h in ("server", "x-azure-ref", "x-ms-error-code", "cf-ray",
                  "content-type", "www-authenticate", "x-frame-options",
                  "content-security-policy"):
            if h in hdrs:
                print(f"      {h}: {hdrs[h][:140]}")

    SHOTS.mkdir(parents=True, exist_ok=True)
    pg.screenshot(path=str(SHOTS / "clarity-403.png"), timeout=180_000)
    print("\nSHOT:", SHOTS / "clarity-403.png")
