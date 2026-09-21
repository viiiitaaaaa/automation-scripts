# -*- coding: utf-8 -*-
"""Разведка страницы Dsers: как добавить товар по ссылке в Import List."""
import time
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

URL = "https://www.dsers.com/application/my_products"
SHOT = r"C:\Users\User\AppData\Local\Temp\claude\C--Users-User\01751d72-549c-49dc-8269-5150f5435db9\scratchpad\dsers_site.png"

JS = r"""
() => {
  const vis = el => { const r = el.getBoundingClientRect(); return r.width > 30 && r.height > 15; };
  const btns = [];
  for (const el of document.querySelectorAll('button, a[role=button], div[role=button], .ant-btn')) {
    const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (t && t.length < 40 && vis(el)) btns.push(t);
  }
  const tabs = [];
  for (const el of document.querySelectorAll('[role=tab], .ant-tabs-tab, li')) {
    const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (t && t.length < 40 && vis(el)) tabs.push(t);
  }
  return {url: location.href, title: document.title,
          buttons: [...new Set(btns)].slice(0, 30),
          tabs: [...new Set(tabs)].slice(0, 25),
          inputs: document.querySelectorAll('input,textarea').length};
}
"""

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
print("CDP", auto["port"])
with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()
    pg.goto(URL, wait_until="domcontentloaded", timeout=90000)
    pg.bring_to_front()
    time.sleep(12)
    res = pg.evaluate(JS)
    print("URL:", res["url"][:100])
    print("Заголовок:", res["title"][:70])
    print("Полей ввода:", res["inputs"])
    print("Кнопки:", res["buttons"])
    print("Вкладки:", res["tabs"])
    pg.screenshot(path=SHOT, full_page=False)
    print("скриншот:", SHOT)
    time.sleep(240)
