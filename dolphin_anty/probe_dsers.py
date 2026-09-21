# -*- coding: utf-8 -*-
"""Разведка: как на странице товара устроена кнопка Dsers."""
import json
from playwright.sync_api import sync_playwright

PORT = 58151

JS = r"""
() => {
  const out = {frames: [], nodes: [], shadow: []};
  // 1. обычный DOM: любые элементы, где встречается dsers
  const all = document.querySelectorAll('*');
  for (const el of all) {
    const txt = (el.textContent || '').trim();
    const cls = (el.className && el.className.baseVal !== undefined ? el.className.baseVal : el.className) || '';
    const id  = el.id || '';
    const hay = (cls + ' ' + id).toLowerCase();
    const isBtnText = txt.length < 60 && /dsers/i.test(txt) && el.children.length === 0;
    if (hay.includes('dsers') || isBtnText) {
      out.nodes.push({tag: el.tagName, id: id, cls: String(cls).slice(0,80), text: txt.slice(0,60)});
      if (out.nodes.length > 25) break;
    }
    if (el.shadowRoot) {
      const h = el.shadowRoot.innerHTML || '';
      if (/dsers/i.test(h)) out.shadow.push({tag: el.tagName, id: id, cls: String(cls).slice(0,60)});
    }
  }
  for (const f of document.querySelectorAll('iframe')) {
    out.frames.push({src: (f.src||'').slice(0,120), id: f.id, cls: String(f.className||'').slice(0,60)});
  }
  return out;
}
"""

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:%d" % PORT)
    ctx = b.contexts[0]
    pages = [pg for pg in ctx.pages if "/item/" in pg.url]
    print("вкладок с товарами:", len(pages))
    pg = pages[0]
    pg.bring_to_front()
    print("страница:", pg.url[:90])
    pg.wait_for_timeout(2000)
    res = pg.evaluate(JS)
    print(json.dumps(res, ensure_ascii=False, indent=1)[:3000])
    print("\n--- фреймы playwright ---")
    for f in pg.frames:
        print("  ", (f.url or "")[:110])
