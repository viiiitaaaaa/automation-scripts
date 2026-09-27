# -*- coding: utf-8 -*-
"""
Добавить товары в Import List на dsers.com по ссылкам.

    python dsers_import.py --file links_import.txt --limit 3     # проверка
    python dsers_import.py --file links_import.txt               # все

Поле ввода на странице Import list — единственный input с плейсхолдером
«Please enter the product link here…», рядом кнопка OK.
"""
import argparse
import re
import sys
import time
from pathlib import Path

from dolphin import DolphinLocal, start_with_retry

PROFILE = 859648353          # единственный профиль (там залогинен Dsers)
IMPORT_URL = "https://www.dsers.com/application/import_list"
PLACEHOLDER = "Please enter the product link"

# Кнопка OK, стоящая рядом с полем ссылки (а не «Product Name OK» в фильтрах).
CLICK_OK_JS = r"""
(inputRect) => {
  const cands = [];
  for (const el of document.querySelectorAll('button, .ant-btn')) {
    const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (!/^ok$/i.test(t)) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 20 || r.height < 15) continue;
    // та же строка, что и поле, и правее него
    const dy = Math.abs((r.y + r.height / 2) - (inputRect.y + inputRect.height / 2));
    if (dy < 40 && r.x > inputRect.x) cands.push({el: el, dx: r.x - inputRect.x, dy: dy});
  }
  if (!cands.length) return {ok: false};
  cands.sort((a, b) => a.dx - b.dx);
  cands[0].el.click();
  return {ok: true};
}
"""

# Карточек товара на странице: по чекбоксу в каждой. Растёт — значит товар принят.
CARDS_JS = r"""
() => document.querySelectorAll('.ant-checkbox-input').length
"""

STATE_JS = r"""
() => {
  let count = null;
  for (const el of document.querySelectorAll('a[href*="import_list"], li, span')) {
    const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    const m = t.match(/^Import list\s*(\d+)$/i);
    if (m) { count = parseInt(m[1]); break; }
  }
  const msg = document.querySelector('.ant-message, .ant-notification, .ant-message-notice-content');
  return {count: count, msg: msg ? msg.textContent.replace(/\s+/g,' ').trim().slice(0, 90) : null};
}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", type=Path, required=True)
    ap.add_argument("--profile", type=int, default=PROFILE)
    ap.add_argument("--limit", type=int, default=0, help="взять только первые N ссылок")
    ap.add_argument("--pause", type=float, default=2, help="пауза между товарами, сек")
    ap.add_argument("--timeout", type=float, default=25, help="сколько ждать появления товара, сек")
    args = ap.parse_args()

    urls = re.findall(r"https?://\S+", args.file.read_text("utf-8", errors="replace"))
    if args.limit:
        urls = urls[:args.limit]
    print("ссылок к импорту: %d" % len(urls))

    from playwright.sync_api import sync_playwright

    api = DolphinLocal(port=DolphinLocal.discover() or 3001)
    print("[..] поднимаю профиль %d …" % args.profile)
    auto = start_with_retry(api, args.profile)["automation"]
    print("[ok] CDP %s" % auto["port"])

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(
            "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        pg = ctx.new_page()
        pg.goto(IMPORT_URL, wait_until="domcontentloaded", timeout=90_000)
        pg.bring_to_front()

        # страница тяжёлая, ждём появления поля
        field = pg.locator("input[placeholder*='%s']" % PLACEHOLDER)
        field.wait_for(timeout=90_000)
        print("[ok] поле ввода найдено")

        st = pg.evaluate(STATE_JS)
        start_count = st["count"]
        print("[i] в Import list сейчас: %s" % start_count)

        ok = fail = 0
        for i, u in enumerate(urls, 1):
            try:
                before = pg.evaluate(CARDS_JS)
                field.fill("")
                field.fill(u)
                box = field.bounding_box()
                res = pg.evaluate(CLICK_OK_JS, box)
                if not res.get("ok"):
                    print("%3d. [x] кнопка OK не найдена" % i)
                    fail += 1
                    continue
                # Считать карточки на странице бесполезно: их всегда максимум 20
                # (пагинация 20/page), поэтому просто даём Dsers время принять ссылку,
                # а итог сверяем в конце по счётчику после перезагрузки.
                waited = 0.0
                while waited < args.timeout:
                    time.sleep(1.5)
                    waited += 1.5
                    if pg.evaluate(CARDS_JS) > before or waited >= args.pause:
                        break
                st = pg.evaluate(STATE_JS)
                mark = st["msg"] or ""
                if re.search(r"fail|error|invalid|limit", mark, re.I):
                    fail += 1
                    print("%3d. [x] %s — %s" % (i, mark[:60], u.split('/')[-1]))
                else:
                    ok += 1
                    print("%3d. [ok] %s  (%.0f с)  %s" % (i, u.split('/')[-1], waited, mark[:40]))
            except Exception as e:
                fail += 1
                print("%3d. [x] ошибка: %s" % (i, str(e)[:70]))
                try:
                    field = pg.locator("input[placeholder*='%s']" % PLACEHOLDER)
                    field.wait_for(timeout=30_000)
                except Exception:
                    print("     поле пропало — прекращаю")
                    break

        print("\nотправлено: %d, отказов: %d" % (ok, fail))
        # счётчик в меню не реактивный — перезагружаем страницу и читаем заново
        pg.reload(wait_until="domcontentloaded", timeout=90_000)
        for _ in range(20):
            time.sleep(3)
            if pg.evaluate("() => document.querySelectorAll('button, input').length") > 3:
                break
        time.sleep(4)
        st = pg.evaluate(STATE_JS)
        print("Import list было %s, стало %s" % (start_count, st["count"]))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[i] остановлено")
        sys.exit(130)
