# -*- coding: utf-8 -*-
"""Сверка: какие из наших ссылок реально лежат в Import list."""
import re, time, sys
from pathlib import Path
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

LINKS = Path(r"C:\Users\User\dolphin_anty\links_import.txt")

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

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()
    pg.goto("https://www.dsers.com/application/import_list", wait_until="domcontentloaded", timeout=90000)
    pg.bring_to_front()
    for _ in range(20):
        time.sleep(3)
        if pg.evaluate("() => document.querySelectorAll('button, input').length") > 3:
            break
    time.sleep(5)

    # переключаем размер страницы на максимум, чтобы не листать
    try:
        pg.evaluate("""() => {
          for (const el of document.querySelectorAll('.ant-select-selection-item, .ant-pagination-options')) {
            if (/page/i.test(el.textContent || '')) { el.click(); return true; }
          }
          return false;
        }""")
        time.sleep(2)
        pg.evaluate("""() => {
          for (const el of document.querySelectorAll('.ant-select-item-option')) {
            if (/100/.test(el.textContent || '')) { el.click(); return true; }
          }
          return false;
        }""")
        time.sleep(6)
    except Exception as e:
        print("не удалось увеличить страницу:", str(e)[:60])

    found = set()
    for page_no in range(1, 12):
        time.sleep(3)
        found |= set(pg.evaluate(IDS_JS))
        print("страница %d: всего собрано id %d" % (page_no, len(found)))
        moved = pg.evaluate("""() => {
          const nxt = document.querySelector('.ant-pagination-next:not(.ant-pagination-disabled)');
          if (nxt) { nxt.click(); return true; }
          return false;
        }""")
        if not moved:
            break
        time.sleep(5)

    ours = re.findall(r"/item/(\d+)\.html", LINKS.read_text("utf-8"))
    ours_set = list(dict.fromkeys(ours))
    missing = [i for i in ours_set if i not in found]
    print("\nнаших ссылок: %d" % len(ours_set))
    print("найдено в Import list: %d" % sum(1 for i in ours_set if i in found))
    print("НЕ найдено: %d" % len(missing))
    for m in missing:
        print("   https://www.aliexpress.com/item/%s.html" % m)
