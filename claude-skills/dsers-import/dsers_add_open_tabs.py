# -*- coding: utf-8 -*-
"""
Нажать «Add To DSers» на уже ОТКРЫТЫХ вкладках AliExpress (не открывает новых
вкладок и никуда не переходит — только работает с тем, что уже есть в окне).

    python dsers_add_open_tabs.py --profile 859648353            # нажать на всех подходящих вкладках
    python dsers_add_open_tabs.py --profile 859648353 --probe    # только разведка, что нашли

Профиль по умолчанию — тот, что укажешь через --profile (свой на каждый запуск,
единого умолчания нет, чтобы не перепутать с "Декор" 859648353 из dsers_add.py).
"""
import argparse
import sys
import time

from dolphin import DolphinLocal, start_with_retry

# Кнопка основного товара — BUTTON с текстом РОВНО "Add To DSers", в правой панели
# под Share. Кнопку "Add all to DSers" над Related items НЕ трогаем — она тянет
# рекламные товары чужих продавцов.
CLICK_JS = r"""
() => {
  const btns = [];
  for (const el of document.querySelectorAll('button')) {
    const t = (el.textContent || '').replace(/\s+/g, ' ').trim();
    if (!/^add to dsers$/i.test(t)) continue;
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
    ap.add_argument("--profile", type=int, required=True)
    ap.add_argument("--probe", action="store_true", help="только показать, что нашли, не нажимать")
    ap.add_argument("--wait", type=float, default=6, help="сек ожидания перед кликом на вкладке")
    ap.add_argument("--close-after", action="store_true",
                     help="закрывать вкладку сразу после обработки — освобождает память, "
                          "когда открыто много товаров разом")
    ap.add_argument("--limit", type=int, default=0, help="обработать не больше N вкладок за запуск (0 = все)")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    api = DolphinLocal(port=DolphinLocal.discover() or 3001)
    print("[..] подключаюсь к профилю %d …" % args.profile)
    auto = start_with_retry(api, args.profile)["automation"]
    print("[ok] CDP %s" % auto["port"])

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(
            "ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()

        all_pages = list(ctx.pages)
        blank = sum(1 for pg in all_pages if not (pg.url or ""))
        print("[ok] всего вкладок: %d (из них пустых/непрогруженных: %d — восстановлю reload'ом по ходу)"
              % (len(all_pages), blank))

        # Предварительно фильтровать по URL нельзя — после падения браузера от
        # перегруза памяти все вкладки показывают пустой url, реальный адрес
        # восстанавливается только через reload() внутри цикла ниже.
        pages = all_pages

        if not pages:
            print("[!] нет ни одной открытой вкладки")
            return

        if args.limit:
            pages = pages[: args.limit]
            print("[i] ограничиваю запуск первыми %d вкладками" % len(pages))

        done = 0
        for i, pg in enumerate(pages, 1):
            try:
                pg.bring_to_front()
                if not (pg.url or ""):
                    # вкладка "пустая" — так бывает после падения браузера от перегруза
                    # памяти; страница на самом деле жива, просто не отрисована. Пере-
                    # загружаем — история навигации сохраняется, урл восстанавливается.
                    pg.reload(wait_until="domcontentloaded", timeout=30_000)
                    time.sleep(5)
            except Exception as e:
                print("%3d. [x] не смогла восстановить вкладку: %s" % (i, e))
                continue

            try:
                url_short = (pg.url or "")[:80]
                title = (pg.title() or "")[:50]
            except Exception as e:
                print("%3d. [x] вкладка недоступна (возможно, браузер перегружен): %s" % (i, e))
                continue

            if "aliexpress" not in url_short or "/item/" not in url_short:
                print("%3d. [-] пропускаю, это не карточка товара: %s" % (i, url_short))
                if args.close_after:
                    try:
                        pg.close()
                    except Exception:
                        pass
                continue

            try:
                time.sleep(args.wait)
                pg.mouse.wheel(0, 600)
                time.sleep(1.5)
            except Exception as e:
                print("%3d. [x] не смогла подготовить вкладку: %s" % (i, e))
                continue

            if args.probe:
                print("%3d. %s — %s" % (i, title, url_short))
                continue

            try:
                res = pg.evaluate(CLICK_JS)
            except Exception as e:
                print("%3d. [x] ошибка клика: %s" % (i, e))
                continue

            if res.get("ok"):
                time.sleep(4)
                try:
                    st = pg.evaluate(STATE_JS)
                except Exception:
                    st = {"buttons": [], "toast": None}
                done += 1
                print("%3d. [ok] нажал «%s» — %s" % (i, res["label"], title))
                print("      кнопки после клика: %s" % st["buttons"])
                if st["toast"]:
                    print("      сообщение: %s" % st["toast"])
            else:
                print("%3d. [x] %s — %s" % (i, res.get("reason"), title))

            if args.close_after:
                try:
                    pg.close()
                except Exception:
                    pass

            time.sleep(2)

        if not args.probe:
            print("\nнажато: %d из %d" % (done, len(pages)))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[i] остановлено")
        sys.exit(130)
