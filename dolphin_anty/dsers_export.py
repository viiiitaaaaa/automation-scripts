# -*- coding: utf-8 -*-
"""Выгрузка ссылок на AliExpress из Dsers в файл dsers_links.txt.

Обходит Import list и My Products, листает страницы, собирает номера товаров.
    py -3.13 dsers_export.py
"""
import re, sys, time
from pathlib import Path
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
PROFILE = 836461485
OUT = Path("dsers_links.txt")
PAGES = {
    "Import list": "https://www.dsers.com/application/import_list",
    "My Products": "https://www.dsers.com/application/my_product",
}

IDS_JS = r"""
() => {
  const ids = new Set();
  const rx = /(\d{10,})\.html|item\/(\d{10,})|"productId"\s*:\s*"?(\d{10,})/g;
  const html = document.body.innerHTML;
  let m;
  while ((m = rx.exec(html))) ids.add(m[1] || m[2] || m[3]);
  for (const a of document.querySelectorAll('a[href*="aliexpress"]')) {
    const mm = (a.href || '').match(/(\d{10,})/);
    if (mm) ids.add(mm[1]);
  }
  return [...ids];
}
"""

def bump_page_size(pg):
    """Ставим 100 товаров на страницу, чтобы меньше листать."""
    try:
        pg.evaluate("""() => {
          for (const el of document.querySelectorAll('.ant-select-selection-item, .ant-pagination-options')) {
            if (/page/i.test(el.textContent || '')) { el.click(); return true; }
          } return false; }""")
        time.sleep(2)
        pg.evaluate("""() => {
          for (const el of document.querySelectorAll('.ant-select-item-option')) {
            if (/100/.test(el.textContent || '')) { el.click(); return true; }
          } return false; }""")
        time.sleep(6)
    except Exception as e:
        print("   размер страницы не сменился:", str(e)[:50], flush=True)

def harvest(pg, name, url, found):
    print(f"\n== {name} ==", flush=True)
    pg.goto(url, wait_until="domcontentloaded", timeout=90_000)
    pg.bring_to_front()
    for _ in range(20):                      # ждём, пока приложение прорисуется
        time.sleep(3)
        if pg.evaluate("() => document.querySelectorAll('button, input').length") > 3:
            break
    time.sleep(5)
    bump_page_size(pg)
    before = len(found)
    for page_no in range(1, 15):
        time.sleep(3)
        found |= set(pg.evaluate(IDS_JS))
        print(f"   страница {page_no}: собрано всего {len(found)}", flush=True)
        moved = pg.evaluate("""() => {
          const n = document.querySelector('.ant-pagination-next:not(.ant-pagination-disabled)');
          if (n) { n.click(); return true; } return false; }""")
        if not moved:
            break
        time.sleep(5)
    print(f"   с этой вкладки прибавилось: {len(found) - before}", flush=True)

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, PROFILE)["automation"]
found = set()
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()
    for name, url in PAGES.items():
        try:
            harvest(pg, name, url, found)
        except Exception as e:
            print(f"   {name}: сбой - {type(e).__name__}: {str(e)[:70]}", flush=True)

links = [f"https://www.aliexpress.com/item/{i}.html" for i in sorted(found)]
OUT.write_text("\n".join(links), encoding="utf-8")
print(f"\nГОТОВО. уникальных товаров: {len(links)} -> {OUT}", flush=True)
