# -*- coding: utf-8 -*-
"""Ищем рабочий способ снять рейтинг: XHR внутри страницы или обычный переход."""
import json, sys, re, requests
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
port = json.load(open("cdp.json"))["port"]
ws = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=5).json()["webSocketDebuggerUrl"]
ITEM = sys.argv[1] if len(sys.argv) > 1 else "3256811359728907"

XHR = """
(item) => new Promise((res) => {
  const x = new XMLHttpRequest();
  x.open('GET', `https://www.aliexpress.com/item/${item}.html`, true);
  x.withCredentials = true;
  x.onload  = () => res({ok: true, status: x.status, len: x.responseText.length,
                          head: x.responseText.slice(0, 200)});
  x.onerror = () => res({ok: false, err: 'xhr error'});
  x.timeout = 30000;
  x.ontimeout = () => res({ok: false, err: 'timeout'});
  x.send();
})
"""

PATS = {
 "averageStar": r'"averageStar"\s*:\s*"?([\d.]+)"?',
 "evarageStar": r'"evarageStar"\s*:\s*"?([\d.]+)"?',
 "ratingValue": r'"ratingValue"\s*:\s*"?([\d.]+)"?',
 "totalValidNum": r'"totalValidNum"\s*:\s*"?(\d+)"?',
 "reviewCount": r'"reviewCount"\s*:\s*"?(\d+)"?',
 "formatTradeCount": r'"formatTradeCount"\s*:\s*"([^"]{1,20})"',
 "formatedAmount": r'"formatedAmount"\s*:\s*"([^"]{1,30})"',
 "minAmount": r'"minActivityAmount"\s*:\s*\{[^}]*"value"\s*:\s*([\d.]+)',
 "subject": r'"subject"\s*:\s*"([^"]{1,60})"',
}

def scan(html, tag):
    print(f"--- {tag}: длина {len(html)}")
    if re.search(r"captcha|punish|_____tmd_____", html[:5000], re.I):
        print("    !! страница-заглушка (антибот)")
    for k, p in PATS.items():
        m = re.search(p, html)
        if m:
            print(f"    {k:18s} = {m.group(1)[:40]}")

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(ws)
    ctx = b.contexts[0]
    pg = ctx.pages[0] if ctx.pages else ctx.new_page()
    if "aliexpress.com" not in pg.url:
        pg.goto("https://www.aliexpress.com/", wait_until="domcontentloaded", timeout=90_000)

    print("== СПОСОБ 1: XHR изнутри страницы ==", flush=True)
    r = pg.evaluate(XHR, ITEM)
    print("   ", {k: v for k, v in r.items() if k != "head"})
    if r.get("ok") and r.get("len", 0) > 5000:
        h = pg.evaluate("""(item)=>new Promise(res=>{const x=new XMLHttpRequest();
            x.open('GET',`https://www.aliexpress.com/item/${item}.html`,true);
            x.withCredentials=true;x.onload=()=>res(x.responseText);
            x.onerror=()=>res('');x.send();})""", ITEM)
        scan(h, "XHR")

    print("\n== СПОСОБ 2: обычный переход на карточку ==", flush=True)
    pg.goto(f"https://www.aliexpress.com/item/{ITEM}.html",
            wait_until="domcontentloaded", timeout=90_000)
    pg.wait_for_timeout(2500)
    html = pg.content()
    scan(html, "goto")
    print("\n   заголовок вкладки:", pg.title()[:70])
