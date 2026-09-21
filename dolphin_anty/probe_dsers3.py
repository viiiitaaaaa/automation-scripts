# -*- coding: utf-8 -*-
"""Ищем кнопку 'Add To DSers' основного товара по всем фреймам страницы."""
import time, json
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

URL = "https://www.aliexpress.com/item/3256809699761884.html"

JS = r"""
() => {
  const res = [];
  const rect = el => { const r = el.getBoundingClientRect();
    return {x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height)}; };
  const walk = (root, path) => {
    let els; try { els = root.querySelectorAll('*'); } catch (e) { return; }
    for (const el of els) {
      const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
      if (/add to dsers/i.test(t) && t.length < 40) {
        const r = rect(el);
        if (r.w > 60 && r.h > 20) {
          res.push({path: path, tag: el.tagName, text: t.slice(0, 30), rect: r,
                    cls: String(el.className || '').slice(0, 50)});
        }
      }
      if (el.shadowRoot) walk(el.shadowRoot, path + '>shadow');
    }
  };
  walk(document, 'root');
  return res;
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
    for i, fr in enumerate(pg.frames):
        try:
            hits = fr.evaluate(JS)
        except Exception as e:
            print("frame %d [%s] ошибка: %s" % (i, (fr.url or "")[:50], str(e)[:60]))
            continue
        if hits:
            print("frame %d url=%s" % (i, (fr.url or "")[:70]))
            for h in hits[:6]:
                print("   ", json.dumps(h, ensure_ascii=False))
    time.sleep(90)
