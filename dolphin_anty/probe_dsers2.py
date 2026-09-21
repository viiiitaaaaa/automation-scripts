# -*- coding: utf-8 -*-
"""Точная разведка: где кнопка Dsers основного товара относительно Share."""
import time, json
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

URL = "https://www.aliexpress.com/item/3256809699761884.html"
SHOT = r"C:\Users\User\AppData\Local\Temp\claude\C--Users-User\01751d72-549c-49dc-8269-5150f5435db9\scratchpad\dsers.png"

JS = r"""
() => {
  const out = {dsers: [], share: []};
  const rect = el => { const r = el.getBoundingClientRect();
    return {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height)}; };
  for (const el of document.querySelectorAll('*')) {
    const own = Array.from(el.childNodes).filter(n => n.nodeType === 3)
                     .map(n => n.textContent).join(' ').trim();
    const cls = String((el.className && el.className.baseVal !== undefined)
                        ? el.className.baseVal : (el.className || ''));
    if (/^add to dsers$/i.test(own) || (cls.includes('dsersImportButton'))) {
      const r = rect(el);
      const p = el.parentElement;
      out.dsers.push({tag: el.tagName, cls: cls.slice(0,60), rect: r,
                      parentCls: String(p ? (p.className || '') : '').slice(0,60),
                      display: getComputedStyle(el).display,
                      vis: getComputedStyle(el).visibility,
                      opacity: getComputedStyle(el).opacity});
    }
    if (/^share$/i.test(own)) out.share.push({tag: el.tagName, cls: cls.slice(0,60), rect: rect(el)});
  }
  return out;
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
    time.sleep(8)
    res = pg.evaluate(JS)
    print("SHARE:", json.dumps(res["share"][:5], ensure_ascii=False))
    print("DSERS (первые 12):")
    for d in res["dsers"][:12]:
        print("  ", json.dumps(d, ensure_ascii=False))
    pg.screenshot(path=SHOT)
    print("скриншот:", SHOT)
    time.sleep(120)
