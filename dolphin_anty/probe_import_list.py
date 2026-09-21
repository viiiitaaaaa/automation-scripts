# -*- coding: utf-8 -*-
"""Разведка Import list: переходим кликом по меню, ищем поле для ссылок."""
import time
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

START = "https://www.dsers.com/application/my_products"
SHOT = r"C:\Users\User\AppData\Local\Temp\claude\C--Users-User\01751d72-549c-49dc-8269-5150f5435db9\scratchpad\dsers_import.png"

JS = r"""
() => {
  const vis = el => { const r = el.getBoundingClientRect(); return r.width > 20 && r.height > 10; };
  const btns = [];
  for (const el of document.querySelectorAll('button, a[role=button], div[role=button], .ant-btn')) {
    const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (t && t.length < 45 && vis(el)) btns.push(t);
  }
  const inputs = [];
  for (const el of document.querySelectorAll('input, textarea')) {
    const r = el.getBoundingClientRect();
    if (r.width > 40) inputs.push({tag: el.tagName, ph: el.placeholder || '',
                                   w: Math.round(r.width), h: Math.round(r.height)});
  }
  return {url: location.href, buttons: [...new Set(btns)].slice(0, 25), inputs: inputs.slice(0, 12)};
}
"""

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
print("CDP", auto["port"])
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()
    pg.goto(START, wait_until="domcontentloaded", timeout=90000)
    pg.bring_to_front()
    time.sleep(10)

    # клик по пункту меню «Import list»
    clicked = pg.evaluate("""() => {
      for (const el of document.querySelectorAll('a, li, div, span')) {
        const t = (el.textContent || '').replace(/\\s+/g,' ').trim();
        if (/^import list\\s*\\d*$/i.test(t)) {
          const r = el.getBoundingClientRect();
          if (r.width > 20 && r.height > 10) { el.click(); return t; }
        }
      }
      return null;
    }""")
    print("клик по меню:", clicked)
    time.sleep(10)

    res = pg.evaluate(JS)
    print("URL:", res["url"][:110])
    print("Кнопки:", res["buttons"])
    print("Поля:")
    for i in res["inputs"]:
        print("   ", i)
    pg.screenshot(path=SHOT)
    print("скриншот:", SHOT)
    time.sleep(240)
