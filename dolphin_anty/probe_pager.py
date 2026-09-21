# -*- coding: utf-8 -*-
"""Смотрим текущую (отфильтрованную) вкладку Import list: сколько видно и чем листать.
Ничего не перезагружаем - фильтры пользователя должны остаться."""
import sys, json, re, requests
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")

# ищем живой CDP-порт уже запущенного профиля
import subprocess
out = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True).stdout
ports = sorted({int(m.group(1)) for m in
                (re.search(r"127\.0\.0\.1:(\d+)\s+.*LISTENING", ln) for ln in out.splitlines()) if m})
ws = None
for p in ports:
    try:
        v = requests.get(f"http://127.0.0.1:{p}/json/version", timeout=1)
        if v.status_code != 200 or "webSocketDebuggerUrl" not in v.text:
            continue
        tabs = requests.get(f"http://127.0.0.1:{p}/json/list", timeout=3).json()
        urls = [t.get("url", "") for t in tabs]
        print(f"  порт {p}: вкладок {len(tabs)}", [u[:45] for u in urls][:4])
        if any("dsers.com" in u for u in urls):
            ws = v.json()["webSocketDebuggerUrl"]
            print("[ok] это наш браузер, порт", p)
            break
    except Exception:
        pass
if not ws:
    print("[x] вкладка Dsers не найдена ни на одном порту")
    raise SystemExit(1)

with sync_playwright() as pw:
    b = pw.chromium.connect_over_cdp(ws)
    pages = [pg for c in b.contexts for pg in c.pages]
    print("вкладок открыто:", len(pages))
    target = None
    for pg in pages:
        if "import_list" in pg.url:
            target = pg; break
    if not target:
        print("[x] вкладка Import list не найдена. Открыто:", [p.url[:60] for p in pages][:6])
        raise SystemExit(1)

    info = target.evaluate("""() => {
      const txt = document.body.innerText;
      const res = (txt.match(/Results:\s*([\d,]+)/) || [])[1] || '?';
      const aliA = document.querySelectorAll('a[href*="aliexpress"]').length;
      const cards = document.querySelectorAll('[class*="productCard"],[class*="product-card"],[class*="listItem"]').length;
      // ищем всё, что похоже на листалку
      const pag = [];
      for (const el of document.querySelectorAll('ul,div')) {
        const c = el.className || '';
        if (typeof c === 'string' && /pagin|pager/i.test(c) && el.innerText.trim()) {
          pag.push({cls: c.slice(0, 70), txt: el.innerText.replace(/\s+/g, ' ').slice(0, 90)});
        }
      }
      // сколько товаров реально в разметке (по номерам AliExpress)
      const ids = new Set();
      const rx = /(\d{13,})/g; let m;
      while ((m = rx.exec(document.body.innerHTML))) ids.add(m[1]);
      return {results: res, aliLinks: aliA, cards, ids: ids.size,
              pagers: pag.slice(0, 5), tail: txt.trim().slice(-160)};
    }""")
    print(json.dumps(info, ensure_ascii=False, indent=1))
