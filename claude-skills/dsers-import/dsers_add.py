# -*- coding: utf-8 -*-
"""
Нажать кнопку расширения Dsers («Add to Dsers») на страницах товаров AliExpress.

    python dsers_add.py --file links_decor.txt            # открыть и нажать
    python dsers_add.py --file links_decor.txt --probe    # только разведка кнопки

Профиль по умолчанию — 859648353. Кнопку рисует расширение, поэтому
ищем её и в обычном DOM, и в shadow DOM, и во фреймах.
"""
import argparse
import re
import sys
import time
from pathlib import Path

from dolphin import DolphinLocal, start_with_retry

# Ищем всё, что похоже на кнопку Dsers: по тексту, по классу/id, в shadow DOM.
FIND_JS = r"""
() => {
  const hits = [];
  const walk = (root, path) => {
    let els;
    try { els = root.querySelectorAll('*'); } catch (e) { return; }
    for (const el of els) {
      const cls = String((el.className && el.className.baseVal !== undefined)
                          ? el.className.baseVal : (el.className || ''));
      const id  = String(el.id || '');
      const attr = (cls + ' ' + id).toLowerCase();
      const own = Array.from(el.childNodes)
                       .filter(n => n.nodeType === 3)
                       .map(n => n.textContent).join(' ').trim();
      const byText = own && own.length < 60 && /dsers|add to import/i.test(own);
      if (attr.includes('dsers') || byText) {
        const r = el.getBoundingClientRect();
        hits.push({path: path, tag: el.tagName, id: id, cls: cls.slice(0, 70),
                   text: (el.textContent || '').trim().slice(0, 50),
                   w: Math.round(r.width), h: Math.round(r.height),
                   x: Math.round(r.x), y: Math.round(r.y)});
      }
      if (el.shadowRoot) walk(el.shadowRoot, path + '>shadow(' + el.tagName + ')');
      if (hits.length > 40) return;
    }
  };
  walk(document, 'doc');
  return hits;
}
"""

# Кнопка основного товара — BUTTON с текстом РОВНО "Add To DSers", в правой панели
# под Share. Кнопку "Add all to DSers" над блоком Related items НЕ трогаем: она
# добавляет рекламные товары чужих продавцов.
CLICK_JS = r"""
() => {
  const btns = [];
  for (const el of document.querySelectorAll('button')) {
    const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (!/^add to dsers$/i.test(t)) continue;          // "Add all to DSers" отсекается
    const r = el.getBoundingClientRect();
    if (r.width > 60 && r.height > 20) btns.push(el);
  }
  if (!btns.length) return {ok: false, reason: 'кнопка Add To DSers не найдена'};
  const el = btns[0];
  el.scrollIntoView({block: 'center'});
  el.click();
  return {ok: true, label: (el.textContent || '').trim().slice(0, 40), count: btns.length};
}
"""

# Что стало с кнопкой после клика — так видно, приняло расширение товар или нет.
STATE_JS = r"""
() => {
  const out = [];
  for (const el of document.querySelectorAll('button')) {
    const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (/dsers|added|import/i.test(t) && t.length < 40) out.push(t);
  }
  const toast = document.body.innerText.match(/[^\n]*(success|added|failed|error|login|sign in)[^\n]*/i);
  return {buttons: out.slice(0, 5), toast: toast ? toast[0].slice(0, 80) : null};
}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", type=int, default=859648353)
    ap.add_argument("--file", type=Path, required=True)
    ap.add_argument("--probe", action="store_true", help="только показать, что найдено")
    ap.add_argument("--wait", type=float, default=6, help="сек ожидания появления кнопки")
    ap.add_argument("--hours", type=float, default=3, help="сколько держать браузер после работы")
    args = ap.parse_args()

    urls = re.findall(r"https?://\S+", args.file.read_text("utf-8", errors="replace"))
    print("ссылок: %d" % len(urls))

    from playwright.sync_api import sync_playwright

    api = DolphinLocal(port=DolphinLocal.discover() or 3001)
    print("[..] поднимаю профиль %d …" % args.profile)
    auto = start_with_retry(api, args.profile)["automation"]
    print("[ok] CDP %s" % auto["port"])

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(
            "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()

        done = 0
        for i, u in enumerate(urls, 1):
            pg = ctx.new_page()
            try:
                pg.goto(u, wait_until="domcontentloaded", timeout=90_000)
            except Exception as e:
                print("%3d. [x] не открылась: %s" % (i, e))
                continue
            pg.bring_to_front()
            time.sleep(args.wait)          # расширению нужно время, чтобы вставить кнопку
            try:
                pg.mouse.wheel(0, 600)     # кнопка часто появляется после скролла
                time.sleep(1.5)
            except Exception:
                pass

            title = (pg.title() or "")[:45]
            if args.probe:
                hits = pg.evaluate(FIND_JS)
                print("\n%3d. %s" % (i, title))
                print("     фреймы:")
                for f in pg.frames:
                    if f.url and "aliexpress" not in f.url:
                        print("       ", f.url[:100])
                if not hits:
                    print("     [!] ничего похожего на Dsers не найдено")
                for h in hits[:12]:
                    print("      %s %s cls=%s text=%r %dx%d"
                          % (h["path"], h["tag"], h["cls"][:40], h["text"], h["w"], h["h"]))
            else:
                res = pg.evaluate(CLICK_JS)
                if res.get("ok"):
                    time.sleep(4)                      # ждём ответ расширения
                    st = pg.evaluate(STATE_JS)
                    done += 1
                    print("%3d. [ok] нажал «%s» — %s" % (i, res["label"], title))
                    print("      кнопки после клика: %s" % st["buttons"])
                    if st["toast"]:
                        print("      сообщение: %s" % st["toast"])
                else:
                    print("%3d. [x] %s — %s" % (i, res.get("reason"), title))
                time.sleep(2)

        if not args.probe:
            print("\nнажато: %d из %d" % (done, len(urls)))
        print("[i] держу браузер %.1f ч — останови задачу, когда закончишь" % args.hours)
        try:
            time.sleep(args.hours * 3600)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[i] остановлено")
        sys.exit(130)
