# -*- coding: utf-8 -*-
"""Ссылки AliExpress из отфильтрованного Import list Dsers - за один заход.

Номера товаров берём не из разметки страницы (там внутренние номера Dsers),
а из ответов сервера, которые приложение получает при листании.
"""
import sys, time, json, re
from pathlib import Path
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path("dsers_links.txt")
RAW = Path("dsers_raw.json")
URL = "https://www.dsers.com/application/import_list"

NEXT_JS = r"""() => {
  const box = document.querySelector('[class*="index_btns"]');
  if (!box) return '';
  const b = box.querySelectorAll('button');
  if (b.length < 2) return '';
  const nxt = b[b.length - 1];
  if (nxt.disabled) return '';
  nxt.click();
  return 'ok';
}"""

STATE_JS = r"""() => {
  const p = document.querySelector('[class*="index_pagination"]');
  return p ? p.innerText.replace(/\s+/g, ' ').trim() : '?';
}"""

PATS = {
    "ссылка aliexpress": r"aliexpress\.[a-z.]+/item/(\d{10,})",
    "ali product id":    r'"ali[_A-Za-z]*[Pp]roduct[_A-Za-z]*[Ii]d"\s*:\s*"?(\d{10,})',
    "supplier id":       r'"supplier[_A-Za-z]*[Ii]d"\s*:\s*"?(\d{10,})',
    "productId":         r'"productId"\s*:\s*"?(\d{10,})',
    "номера 3256/1005":  r"\b((?:3256|1005|32[0-9]{2})\d{8,})\b",
}


def main():
    api = DolphinLocal(port=DolphinLocal.discover() or 3001)
    auto = start_with_retry(api, 836461485)["automation"]
    ws = "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"])
    print("[ok] профиль поднят", flush=True)

    bodies = []
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(ws)
        ctx = b.contexts[0] if b.contexts else b.new_context()
        pg = ctx.new_page()

        def on_resp(r):
            """Ответы со списком товаров - в них настоящие номера AliExpress."""
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

        for page_no in range(1, 40):
            for _ in range(4):
                pg.mouse.wheel(0, 5000)
                time.sleep(1.0)
            print("   стр.%d | ответов перехвачено %d | %s"
                  % (page_no, len(bodies), pg.evaluate(STATE_JS)), flush=True)
            if not pg.evaluate(NEXT_JS):
                print("   листалка кончилась", flush=True)
                break
            time.sleep(6)

    blob = "\n".join(bodies)
    RAW.write_text(blob[:2000000], encoding="utf-8")
    print("\nперехвачено ответов: %d, объём %d знаков" % (len(bodies), len(blob)), flush=True)

    best, best_n, best_name = set(), 0, ""
    for name, rx in PATS.items():
        got = set(re.findall(rx, blob))
        print("   %-20s -> %d" % (name, len(got)), flush=True)
        if len(got) > best_n:
            best, best_n, best_name = got, len(got), name

    if best_n < 50:
        print("\nнастоящих номеров в ответах не нашлось - смотри dsers_raw.json", flush=True)
        return

    links = ["https://www.aliexpress.com/item/%s.html" % i for i in sorted(best)]
    OUT.write_text("\n".join(links), encoding="utf-8")
    print("\nГОТОВО: %d ссылок (способ: %s) -> %s" % (len(links), best_name, OUT), flush=True)


if __name__ == "__main__":
    main()
