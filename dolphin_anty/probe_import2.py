# -*- coding: utf-8 -*-
"""Import list: ищем поле «paste AliExpress URL» и кнопку OK."""
import time
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

SHOT = r"C:\Users\User\AppData\Local\Temp\claude\C--Users-User\01751d72-549c-49dc-8269-5150f5435db9\scratchpad\dsers_import2.png"

JS = r"""
() => {
  const vis = el => { const r = el.getBoundingClientRect(); return r.width > 20 && r.height > 10; };
  const btns = [];
  for (const el of document.querySelectorAll('button, .ant-btn, div[role=button], span')) {
    const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (t && t.length < 45 && vis(el)) btns.push(t);
  }
  const inputs = [];
  for (const el of document.querySelectorAll('input, textarea')) {
    const r = el.getBoundingClientRect();
    inputs.push({tag: el.tagName, ph: el.placeholder || '', cls: String(el.className||'').slice(0,40),
                 w: Math.round(r.width), h: Math.round(r.height)});
  }
  return {url: location.href, buttons: [...new Set(btns)].slice(0, 40), inputs: inputs.slice(0, 15)};
}
"""

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
print("CDP", auto["port"])
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()
    pg.goto("https://www.dsers.com/application/import_list", wait_until="domcontentloaded", timeout=90000)
    pg.bring_to_front()
    # ждём, пока уйдёт спиннер и появится содержимое
    for i in range(20):
        time.sleep(3)
        n = pg.evaluate("() => document.querySelectorAll('button, input, .ant-btn').length")
        if n > 3:
            print("контент появился через %d с (элементов %d)" % ((i + 1) * 3, n))
            break
    time.sleep(3)
    res = pg.evaluate(JS)
    print("URL:", res["url"][:110])
    print("Кнопки:", res["buttons"])
    print("Поля:")
    for i in res["inputs"]:
        print("   ", i)
    pg.screenshot(path=SHOT)
    print("скриншот:", SHOT)
    time.sleep(240)
