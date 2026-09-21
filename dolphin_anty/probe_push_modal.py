# -*- coding: utf-8 -*-
"""Открываем окно Push to Store и смотрим, что там. Подтверждать НЕ будем."""
import sys, time, json
from pathlib import Path
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding="utf-8")

keep = set()
for ln in Path("check_results.jsonl").read_text(encoding="utf-8").splitlines():
    try:
        d = json.loads(ln)
    except Exception:
        continue
    if d.get("verdict") == "берём":
        keep.add(str(d["pid"]))

api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
ws = "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"])

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(ws)
    ctx = b.contexts[0] if b.contexts else b.new_context()
    pg = ctx.new_page()
    bodies = []
    def on_resp(r):
        if "dsers" in r.url and "search" in r.url:
            try:
                bodies.append(r.text())
            except Exception:
                pass

    pg.on("response", on_resp)
    pg.goto("https://www.dsers.com/application/import_list",
            wait_until="domcontentloaded", timeout=90_000)
    pg.bring_to_front()
    for _ in range(25):
        time.sleep(3)
        if pg.evaluate("() => document.querySelectorAll('button, input').length") > 3:
            break
    time.sleep(8)

    ids = []
    for body in bodies:
        try:
            j = json.loads(body)
        except Exception:
            continue
        for r in (j.get("data") or []):
            if isinstance(r, dict) and str(r.get("supplyProductId")) in keep:
                ids.append(str(r["id"]))
    print("наших на странице:", len(ids), flush=True)

    pg.evaluate(r"""(ids) => {
      const want = new Set(ids);
      for (const cb of document.querySelectorAll('input.ant-checkbox-input')) {
        const v = cb.getAttribute('value');
        if (v && want.has(v) && !cb.checked) (cb.closest('.ant-checkbox') || cb).click();
      }
    }""", ids)
    time.sleep(2)

    pg.evaluate("""() => {
      const b = document.querySelector('button[class*="pushButton"]');
      if (b && !b.disabled) b.click();
    }""")
    time.sleep(6)

    modal = pg.evaluate(r"""() => {
      const m = document.querySelector('.ant-modal-wrap:not([style*="display: none"]), .ant-modal');
      if (!m) return {found: false, body: document.body.innerText.slice(-300)};
      const btns = [...m.querySelectorAll('button')].map(b => ({
        txt: (b.innerText || '').trim().slice(0, 30),
        cls: (typeof b.className === 'string' ? b.className : '').slice(0, 50),
        dis: b.disabled === true}));
      return {found: true,
              text: m.innerText.replace(/\s+/g, ' ').slice(0, 700),
              buttons: btns.slice(0, 10)};
    }""")
    print(json.dumps(modal, ensure_ascii=False, indent=1)[:1800], flush=True)

    pg.keyboard.press("Escape")
    time.sleep(1)
    print("\nокно закрыто, НИЧЕГО НЕ ОТПРАВЛЕНО", flush=True)
