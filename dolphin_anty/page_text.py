"""Открыть URL в новой вкладке и выгрузить видимый текст в файл.

    python gettext.py https://... out.txt
"""
import json, sys, time
from pathlib import Path

CDP = Path(__file__).with_name("cdp.json")
sys.stdout.reconfigure(encoding="utf-8")
cdp = json.loads(CDP.read_text(encoding="utf-8"))
url, out = sys.argv[1], Path(sys.argv[2])

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(cdp["url"])
    ctx = b.contexts[0]
    pg = ctx.new_page()
    r = pg.goto(url, wait_until="domcontentloaded", timeout=90_000)
    time.sleep(10)
    txt = pg.evaluate("() => document.body.innerText")
    out.write_text(txt, encoding="utf-8")
    print("статус:", r.status if r else "?")
    print("URL   :", pg.url[:120])
    print("символов:", len(txt))
    print("файл  :", out)
    pg.close()
