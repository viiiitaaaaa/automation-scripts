"""
Скрины страниц магазинов AliExpress через профиль Dolphin{anty} (с его прокси).

Зачем именно так: страница магазина живёт на aliexpress.COM и с российского IP
отдаёт редирект на .ru + 404. Нужен профиль с не-российским прокси — его и
поднимаем через Local API, цепляемся по CDP и снимаем полностраничные скрины.

Файлы подписываются названием магазина: "<магазин> — страница N.png".

Работа с вкладками: на каждый магазин открывается РОВНО ОДНА вкладка, после
съёмки она закрывается — система не нагружается. Больше MAX_TABS вкладок
одновременно скрипт не допускает.

Требует automation=true в Local API => план Base/Team (на Free будет HTTP 402).

Установка:
    pip install requests playwright

Запуск:
    python shots.py --profile 828976678
    python shots.py --profile 828976678 --pages 4
    python shots.py --profile 828976678 --url ССЫЛКА1 --url ССЫЛКА2
    python shots.py --profile 828976678 --urls-file links.txt --out "C:\\Users\\User\\Desktop\\скрины"
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

from dolphin import DolphinLocal, start_with_retry  # переиспользуем клиент Local API

STORE_URL = (
    "https://www.aliexpress.com/store/1103380252/pages/all-items.html"
    "?spm=a2g0o.store_pc_home.pcShopHead_2007656784738.99"
    "&sortType=bestmatch_sort&shop_sortType=bestmatch_sort"
)
DEFAULT_OUT = Path.home() / "Desktop" / "скрины магазина"

MAX_TABS = 10          # больше вкладок одновременно не открываем
BAD_CHARS = r'[<>:"/\\|?*]'


# --------------------------------------------------------------------------- #
# Имя магазина
# --------------------------------------------------------------------------- #
def store_name(page, url: str) -> str:
    """Название магазина: из <title>, иначе ID магазина из ссылки."""
    title = page.title() or ""
    # "Shop1103380251 Store - Amazing products with exclusive discounts on AliExpress"
    name = re.split(r"\s+[-–|]\s+", title)[0].strip()
    if not name or "aliexpress" in name.lower():
        m = re.search(r"/store/(\d+)", url)
        name = f"магазин {m.group(1)}" if m else "магазин"
    return re.sub(BAD_CHARS, "", name)[:80].strip()


# --------------------------------------------------------------------------- #
# Страница
# --------------------------------------------------------------------------- #
def first_cards(page) -> str:
    """Отпечаток текущей страницы: заголовки первых товаров."""
    return page.evaluate("""() =>
        [...document.querySelectorAll('a[href*="/item/"]')]
            .slice(0, 5).map(e => (e.innerText || '').trim()).join('|')
    """)


def switch_page(page, n: int, timeout: float = 45) -> bool:
    """Кликнуть по номеру страницы в пагинаторе и дождаться смены товаров.

    Пагинация у магазина клиентская: это <a> без href с JS-обработчиком,
    URL при этом не меняется — поэтому проверяем смену по содержимому карточек.
    """
    before = first_cards(page)

    link = page.locator(f"xpath=//a[normalize-space(text())='{n}']").last
    if not link.is_visible():
        print(f"   [x] в пагинаторе нет страницы {n} — дальше страниц нет")
        return False
    link.scroll_into_view_if_needed()
    time.sleep(0.5)
    link.click()

    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(1)
        now = first_cards(page)
        if now and now != before:
            return True
    print(f"   [x] товары не сменились за {timeout:.0f}с — страница {n} не переключилась")
    return False


def page_numbers(page) -> list[int]:
    """Номера страниц, доступные в пагинаторе прямо сейчас."""
    raw = page.evaluate("""() =>
        [...document.querySelectorAll('a')]
            .map(e => (e.innerText || '').trim())
            .filter(t => /^\\d{1,4}$/.test(t))
    """)
    return sorted({int(t) for t in raw})


def goto_page(page, target: int) -> bool:
    """Доскакать до страницы `target` прыжками по видимым номерам пагинатора.

    Пагинатор показывает только окно номеров вокруг текущей страницы, поэтому
    на 43-ю с первой одним кликом не попасть: жмём максимальный доступный
    номер, не превышающий цели, и повторяем — окно сдвигается вперёд.
    """
    cur = 1
    while cur != target:
        nums = [n for n in page_numbers(page) if cur < n <= target]
        if not nums:
            print(f"   [x] из страницы {cur} не дотянуться до {target} — страниц меньше")
            return False
        nxt = max(nums)
        print(f"   [..] прыжок {cur} -> {nxt}")
        if not switch_page(page, nxt):
            return False
        cur = nxt
        time.sleep(1)
    return True


def autoscroll(page, step: int = 900, pause: float = 0.45, limit: int = 60) -> None:
    """Прокрутить страницу до низа, чтобы догрузились ленивые картинки товаров."""
    last = -1
    for _ in range(limit):
        page.mouse.wheel(0, step)
        time.sleep(pause)
        h = page.evaluate("document.body.scrollHeight")
        pos = page.evaluate("window.scrollY + window.innerHeight")
        if pos >= h and h == last:
            break
        last = h
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(0.6)


# --------------------------------------------------------------------------- #
# Один магазин = одна вкладка, которая закрывается после съёмки
# --------------------------------------------------------------------------- #
def close_extra_tabs(ctx, keep: int = 1) -> None:
    """Закрыть лишние вкладки профиля, оставив не больше `keep`.

    Профиль при старте восстанавливает свои сохранённые вкладки — они копятся
    и грузят систему. Оставляем одну, остальные закрываем.
    """
    extra = ctx.pages[keep:]
    for pg in extra:
        try:
            pg.close()
        except Exception:  # noqa: BLE001 — вкладка могла закрыться сама
            pass
    if extra:
        print(f"[ok] закрыл лишних вкладок: {len(extra)} (осталось {len(ctx.pages)})")


def shoot_store(ctx, url: str, pages: int, out_dir: Path, start_page: int = 1) -> list[Path]:
    open_tabs = len(ctx.pages)
    if open_tabs >= MAX_TABS:
        raise RuntimeError(
            f"открыто {open_tabs} вкладок (лимит {MAX_TABS}) — "
            f"закрой лишние в браузере, чтобы не нагружать систему"
        )

    page = ctx.new_page()
    saved: list[Path] = []
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=90_000)

        host = re.sub(r"^www\.", "", page.evaluate("location.hostname"))
        if host.endswith(".ru"):
            raise RuntimeError(
                f"редирект на {host} — у профиля российский IP. "
                f"Поставь профилю не-российский прокси."
            )

        # ждём именно карточки товаров, а не просто DOMContentLoaded:
        # иначе снимем полупустую страницу и не увидим пагинатор
        page.wait_for_selector('a[href*="/item/"]', timeout=60_000)
        time.sleep(2)

        name = store_name(page, url)
        print(f"   магазин: {name}")

        if start_page > 1:
            autoscroll(page)              # пагинатор внизу — сначала прокрутим
            if not goto_page(page, start_page):
                raise RuntimeError(f"не удалось дойти до страницы {start_page}")

        # pages <= 0 -> снимаем до конца, пока в пагинаторе есть следующий номер
        last = start_page + pages - 1 if pages > 0 else 10**6
        for n in range(start_page, last + 1):
            if n > start_page and not switch_page(page, n):
                break

            autoscroll(page)   # догрузить ленивые картинки товаров

            out = out_dir / f"{name} — страница {n}.png"
            # вся область, не только экран. Страница ~10000px в высоту,
            # дефолтных 30с Playwright не хватает — даём 3 минуты.
            page.screenshot(path=str(out), full_page=True, timeout=180_000)
            saved.append(out)
            print(f"   [ok] {out.name}  (первый товар: {first_cards(page)[:40]}…)")
    finally:
        page.close()   # вкладку за собой убираем сразу
        print(f"   [ok] вкладка закрыта (осталось открыто: {len(ctx.pages)})")

    return saved


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="Полностраничные скрины магазинов через Dolphin{anty}")
    ap.add_argument("--profile", type=int, required=True, help="ID профиля Dolphin{anty}")
    ap.add_argument("--pages", type=int, default=4,
                    help="сколько страниц снять с каждого магазина (0 — до конца)")
    ap.add_argument("--start-page", type=int, default=1,
                    help="с какой страницы начать (докликиваемся по пагинатору)")
    ap.add_argument("--url", action="append", default=[], help="ссылка на магазин (можно повторять)")
    ap.add_argument("--urls-file", type=Path, help="файл со ссылками, по одной в строке")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="папка для скринов")
    ap.add_argument("--port", type=int, help="порт Local API (по умолчанию автопоиск)")
    ap.add_argument("--stop", action="store_true", help="погасить профиль в конце")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    urls = list(args.url)
    if args.urls_file:
        urls += [ln.strip() for ln in args.urls_file.read_text("utf-8").splitlines()
                 if ln.strip() and not ln.startswith("#")]
    if not urls:
        urls = [STORE_URL]

    port = args.port or DolphinLocal.discover()
    if port is None:
        print("[x] Local API не отвечает. Запущено ли приложение Dolphin{anty}?")
        return 1

    api = DolphinLocal(port=port)
    print(f"[..] стартую профиль {args.profile} с automation=true …")
    auto = (start_with_retry(api, args.profile).get("automation") or {})
    if not auto.get("port"):
        print("[x] Local API не вернул CDP-порт")
        return 1
    print(f"[ok] CDP порт {auto['port']}")

    args.out.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    failed: list[tuple[str, str]] = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}")
            ctx = browser.contexts[0] if browser.contexts else browser.new_context()
            close_extra_tabs(ctx)   # профиль восстанавливает свои вкладки — убираем лишние

            for i, url in enumerate(urls, 1):
                print(f"\n[{i}/{len(urls)}] {url}")
                try:
                    saved += shoot_store(ctx, url, args.pages, args.out, args.start_page)
                except Exception as e:  # noqa: BLE001 — один магазин не должен ронять всю пачку
                    print(f"   [x] {e}")
                    failed.append((url, str(e)))

            browser.close()
    finally:
        if args.stop:
            print(f"[ok] stop -> {api.stop(args.profile)}")

    print(f"\n[готово] {len(saved)} скринов в {args.out}")
    if failed:
        print(f"[!] не получилось: {len(failed)}")
        for url, err in failed:
            print(f"    {url}\n      {err}")
    return 0 if saved else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:  # noqa: BLE001
        print(f"[x] {e}")
        sys.exit(1)
