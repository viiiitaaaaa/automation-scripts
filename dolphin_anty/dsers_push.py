# -*- coding: utf-8 -*-
"""Отправить отобранные товары из Import list в магазин Shopify.

Отмечает галочками товары, чьи номера AliExpress прошли отбор, и жмёт Push
постранично. Возобновляемый: отправленные записываются в pushed_done.json.
"""
import sys, time, json
from pathlib import Path
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
URL = "https://www.dsers.com/application/import_list"
DONE = Path("pushed_done.json")

keep = set()
for ln in Path("check_results.jsonl").read_text(encoding="utf-8").splitlines():
    try:
        d = json.loads(ln)
    except Exception:
        continue
    if d.get("verdict") == "берём":
        keep.add(str(d["pid"]))
done = set(json.load(open(DONE, encoding="utf-8"))) if DONE.exists() else set()
print("к отправке %d, уже отправлено %d" % (len(keep), len(done)), flush=True)

NEXT_JS = r"""() => {
  const box = document.querySelector('[class*="index_btns"]');
  if (!box) return '';
  const b = box.querySelectorAll('button');
  if (b.length < 2) return '';
  const n = b[b.length - 1];
  if (n.disabled) return '';
  n.click(); return 'ok';
}"""

STATE_JS = r"""() => {
  const p = document.querySelector('[class*="index_pagination"]');
  return p ? p.innerText.replace(/\s+/g, ' ').trim() : '?';
}"""

TICK_JS = r"""(ids) => {
  const want = new Set(ids);
  let ticked = 0;
  for (const cb of document.querySelectorAll('input.ant-checkbox-input')) {
    const v = cb.getAttribute('value');
    if (v && want.has(v) && !cb.checked) {
      (cb.closest('.ant-checkbox') || cb).click();
      ticked++;
    }
  }
  return ticked;
}"""

OPEN_PUSH_JS = r"""() => {
  const b = document.querySelector('button[class*="pushButton"]');
  if (!b || b.disabled) return 'кнопка недоступна';
  b.click(); return 'ok';
}"""

CONFIRM_JS = r"""() => {
  const btns = [...document.querySelectorAll('button')];
  const hit = btns.find(b => /push to stores/i.test((b.innerText || '').trim()) && !b.disabled);
  if (!hit) return 'кнопка подтверждения не найдена';
  hit.click(); return 'ok';
}"""

CLEAR_JS = r"""() => {
  for (const cb of document.querySelectorAll('input.ant-checkbox-input')) {
    if (cb.checked) (cb.closest('.ant-checkbox') || cb).click();
  }
}"""


def page_records(bodies, frm):
    out = []
    for body in bodies[frm:]:
        try:
            j = json.loads(body)
        except Exception:
            continue
        for r in (j.get("data") or []):
            if isinstance(r, dict) and r.get("id") and r.get("supplyProductId"):
                out.append((str(r["id"]), str(r["supplyProductId"]), r.get("title", "")))
    return out


api = DolphinLocal(port=DolphinLocal.discover() or 3001)
auto = start_with_retry(api, 836461485)["automation"]
ws = "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"])
print("[ok] профиль поднят", flush=True)

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
    pg.goto(URL, wait_until="domcontentloaded", timeout=90_000)
    pg.bring_to_front()
    for _ in range(25):
        time.sleep(3)
        if pg.evaluate("() => document.querySelectorAll('button, input').length") > 3:
            break
    time.sleep(8)
    print("[ok] листалка:", pg.evaluate(STATE_JS), flush=True)

    seen = 0
    for page_no in range(1, 40):
        pg.mouse.wheel(0, 4000)
        time.sleep(2)
        recs = page_records(bodies, seen)
        seen = len(bodies)
        mine = [(d, a, t) for d, a, t in recs if a in keep and a not in done]
        print("   стр.%d: записей %d, к отправке %d | %s"
              % (page_no, len(recs), len(mine), pg.evaluate(STATE_JS)), flush=True)

        if mine:
            n = pg.evaluate(TICK_JS, [d for d, a, t in mine])
            time.sleep(2)
            r1 = pg.evaluate(OPEN_PUSH_JS)
            time.sleep(7)
            r2 = pg.evaluate(CONFIRM_JS) if r1 == "ok" else "-"
            time.sleep(10)
            print("      отмечено %d | панель: %s | отправка: %s" % (n, r1, r2), flush=True)
            if r2 == "ok":
                done |= {a for d, a, t in mine}
                json.dump(sorted(done), open(DONE, "w"), indent=0)
            try:
                pg.keyboard.press("Escape")
                time.sleep(1)
                pg.evaluate(CLEAR_JS)
                time.sleep(1)
            except Exception:
                pass

        if not pg.evaluate(NEXT_JS):
            print("   листалка кончилась", flush=True)
            break
        time.sleep(6)

print("\nГОТОВО. отправлено всего: %d из %d" % (len(done), len(keep)), flush=True)
