"""Выгрузить видимый текст ТЕКУЩЕЙ вкладки, без открытия новой.

    python cur_text.py out.txt
"""
import json, sys
from pathlib import Path

CDP = Path(__file__).with_name("cdp.json")
sys.stdout.reconfigure(encoding="utf-8")
cdp = json.loads(CDP.read_text(encoding="utf-8"))
out = Path(sys.argv[1])

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(cdp["url"])
    ctx = b.contexts[0]
    pg = ctx.pages[0]
    txt = pg.evaluate("() => document.body.innerText")
    out.write_text(txt, encoding="utf-8")
    print("URL   :", pg.url[:120])
    print("символов:", len(txt))
    print("файл  :", out)
