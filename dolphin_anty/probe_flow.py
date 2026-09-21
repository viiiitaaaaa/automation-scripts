"""Разведка DOM встроенного приложения: iframe, shadow root, кнопки."""
import json, sys, time
from pathlib import Path

CDP = Path(__file__).with_name("cdp.json")
sys.stdout.reconfigure(encoding="utf-8")
cdp = json.loads(CDP.read_text(encoding="utf-8"))

from playwright.sync_api import sync_playwright

PROBE = """() => {
  const out = {iframes: [], shadowHosts: [], buttons: []};
  document.querySelectorAll('iframe').forEach(f =>
      out.iframes.push({src: (f.src||'').slice(0,100), w: f.clientWidth, h: f.clientHeight}));

  // обход с заходом в shadow root
  const seen = new Set();
  const walk = (root, depth) => {
    if (depth > 12) return;
    root.querySelectorAll('*').forEach(el => {
      if (el.shadowRoot && !seen.has(el)) {
        seen.add(el);
        out.shadowHosts.push(el.tagName.toLowerCase());
        walk(el.shadowRoot, depth + 1);
      }
      const tag = el.tagName.toLowerCase();
      if (tag === 'button' || tag === 'a' || el.getAttribute('role') === 'button') {
        const t = (el.innerText||el.textContent||'').trim().replace(/\\s+/g,' ');
        if (t && t.length < 60) out.buttons.push(t);
      }
    });
  };
  walk(document, 0);
  out.shadowHosts = [...new Set(out.shadowHosts)];
  out.buttons = [...new Set(out.buttons)];
  return out;
}"""

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(cdp["url"])
    pg = b.contexts[0].pages[int(sys.argv[1]) if len(sys.argv) > 1 else 0]
    pg.bring_to_front()
    time.sleep(2)
    r = pg.evaluate(PROBE)
    print("URL:", pg.url)
    print(f"\niframe: {len(r['iframes'])}")
    for f in r["iframes"]:
        print("   ", f)
    print(f"\nshadow-хосты ({len(r['shadowHosts'])}):", ", ".join(r["shadowHosts"][:25]))
    print(f"\nкнопки ({len(r['buttons'])}):")
    for t in r["buttons"][:60]:
        print("   -", t)
