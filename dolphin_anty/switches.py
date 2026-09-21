"""Показать переключатели на текущей вкладке: подпись, состояние, координаты.

    python switches.py [подстрока-фильтр]
"""
import json, sys
from pathlib import Path

CDP = Path(__file__).with_name("cdp.json")
sys.stdout.reconfigure(encoding="utf-8")
cdp = json.loads(CDP.read_text(encoding="utf-8"))
needle = sys.argv[1].lower() if len(sys.argv) > 1 else ""

from playwright.sync_api import sync_playwright

JS = """() => {
  const out = [];
  const nodes = document.querySelectorAll(
    '[role=switch], input[type=checkbox], [class*=Switch], [class*=switch], [class*=Toggle], [class*=toggle]');
  for (const n of nodes) {
    const row = n.closest('li, tr, [class*=Item], [class*=item]') || n.parentElement;
    const label = (row ? row.innerText : '').trim().split('\\n')[0].slice(0, 70);
    const checked = n.getAttribute('aria-checked')
      ?? (n.type === 'checkbox' ? String(n.checked) : (n.getAttribute('aria-pressed') ?? '-'));
    const r = n.getBoundingClientRect();
    if (!r.width && !r.height) continue;
    out.push({tag: n.tagName, cls: (n.className || '').toString().slice(0, 30),
              label, checked, x: Math.round(r.x + r.width/2), y: Math.round(r.y + r.height/2)});
  }
  return out;
}"""

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(cdp["url"])
    pg = b.contexts[0].pages[0]
    rows = pg.evaluate(JS)
    print(f"найдено: {len(rows)}")
    for s in rows:
        if needle and needle not in s["label"].lower():
            continue
        print(f"[{s['checked']:5}] ({s['x']:4},{s['y']:5}) {s['tag']}.{s['cls']} | {s['label']}")
