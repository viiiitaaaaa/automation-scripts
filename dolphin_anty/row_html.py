"""Показать HTML строки, содержащей заданный текст, на текущей вкладке.

    python row_html.py "В доставке"
"""
import json, sys
from pathlib import Path

CDP = Path(__file__).with_name("cdp.json")
sys.stdout.reconfigure(encoding="utf-8")
cdp = json.loads(CDP.read_text(encoding="utf-8"))
needle = sys.argv[1]

from playwright.sync_api import sync_playwright

JS = """(needle) => {
  const out = [];
  for (const el of document.querySelectorAll('li, tr, div')) {
    const t = (el.innerText || '').trim();
    if (!t.startsWith(needle)) continue;
    if (el.querySelectorAll('li, tr').length > 1) continue;
    if (t.length > 300) continue;
    out.push(el.outerHTML.slice(0, 1200));
    if (out.length >= 2) break;
  }
  return out;
}"""

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(cdp["url"])
    pg = b.contexts[0].pages[0]
    for h in pg.evaluate(JS, needle):
        print(h)
        print("-" * 70)
