"""
Пакетная съёмка магазинов AliExpress из списка ссылок, через профиль Dolphin{anty}.

Особенности:
  * Список читается из txt (экспорт переписки): строка с названием, следом ссылка.
  * Короткие ссылки a.aliexpress.com/_xxx разворачиваются сами.
  * Если ссылка ведёт на ТОВАР, а не на магазин — со страницы товара находим
    магазин и снимаем уже его.
  * Прогресс пишется в state.json: при обрыве/лимитах запуск продолжится
    с того места, где остановились (уже снятые магазины пропускаются).
  * Вкладки не плодятся: один магазин = одна вкладка, закрывается сразу после
    съёмки. Лишние вкладки профиля закрываются на старте. Лимит — MAX_TABS.

Запуск:
    python batch.py --profile 828976678 --list "C:\\Users\\User\\Desktop\\сайты али.txt"
    python batch.py --profile 828976678 --pages 4          # продолжить с места остановки
    python batch.py --status                               # что сделано, что осталось
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from dolphin import DolphinLocal, start_with_retry
from shots import (MAX_TABS, autoscroll, close_extra_tabs, first_cards,
                   store_name, switch_page)

LIST_FILE = Path.home() / "Desktop" / "сайты али.txt"
OUT_DIR = Path.home() / "Desktop" / "скрины магазинов"
STATE = Path(__file__).with_name("state.json")
BAD_CHARS = r'[<>:"/\\|?*]'


# --------------------------------------------------------------------------- #
# Список ссылок
# --------------------------------------------------------------------------- #
def parse_list(path: Path) -> list[dict]:
    """Вытащить пары (название, ссылка). Название — ближайшая текстовая строка выше."""
    items, label = [], ""
    for raw in path.read_text("utf-8", errors="replace").splitlines():
        line = re.sub(r"^\s*\d+\s*\t?", "", raw).strip()      # убрать нумерацию
        if not line:
            continue
        if line.startswith("http"):
            items.append({"url": line.split()[0], "label": label})
            continue
        # "[16.08.2026 16:49] VI: HYX Household Items Boutique Store"
        text = re.sub(r"^\[[^\]]*\]\s*", "", line)
        text = re.sub(r"^\w+:\s*", "", text).strip()
        if text and not text.lower().startswith("i just found this"):
            label = text

    seen, uniq = set(), []
    for it in items:
        if it["url"] not in seen:
            seen.add(it["url"])
            uniq.append(it)
    return uniq


# --------------------------------------------------------------------------- #
# Состояние
# --------------------------------------------------------------------------- #
def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text("utf-8"))
    return {"done": {}, "failed": {}}


def save_state(st: dict) -> None:
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=1), "utf-8")


# --------------------------------------------------------------------------- #
# Магазин
# --------------------------------------------------------------------------- #
def to_store_url(page, url: str) -> str | None:
    """Привести любую ссылку (магазин / товар / короткая) к странице всех товаров."""
    page.goto(url, wait_until="domcontentloaded", timeout=90_000)
    time.sleep(3)

    host = re.sub(r"^www\.", "", page.evaluate("location.hostname"))
    if host.endswith(".ru"):
        raise RuntimeError(f"редирект на {host} — у профиля российский IP")

    cur = page.url
    m = re.search(r"/store/(\d+)", cur)
    if not m:
        # это страница товара — ищем на ней ссылку на магазин
        href = page.evaluate("""() => {
            const a = [...document.querySelectorAll('a[href*="/store/"]')]
                .find(x => /\\/store\\/\\d+/.test(x.href));
            return a ? a.href : null;
        }""")
        if not href:
            return None
        m = re.search(r"/store/(\d+)", href)
        if not m:
            return None

    sid = m.group(1)
    return (f"https://www.aliexpress.com/store/{sid}/pages/all-items.html"
            f"?sortType=bestmatch_sort&shop_sortType=bestmatch_sort")


def shoot(ctx, item: dict, pages: int, out_root: Path) -> dict:
    """Снять один магазин. Возвращает запись для state."""
    if len(ctx.pages) >= MAX_TABS:
        raise RuntimeError(f"открыто {len(ctx.pages)} вкладок (лимит {MAX_TABS})")

    page = ctx.new_page()
    try:
        store_url = to_store_url(page, item["url"])
        if not store_url:
            raise RuntimeError("не нашёл магазин по этой ссылке")

        page.goto(store_url, wait_until="domcontentloaded", timeout=90_000)
        # ждём карточки товаров, иначе снимем полупустую страницу без пагинатора
        page.wait_for_selector('a[href*="/item/"]', timeout=60_000)
        time.sleep(2)

        # Название из списка надёжнее заголовка страницы. Но у товарных ссылок
        # в подпись попадает длинное имя товара — тогда берём магазин со страницы.
        label = re.sub(BAD_CHARS, "", item.get("label") or "").strip()
        looks_like_store = label.lower().endswith("store") or len(label) <= 60
        name = label if (label and looks_like_store) else store_name(page, store_url)
        out_dir = out_root / name
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"   магазин: {name}")

        files = []
        for n in range(1, pages + 1):
            if n > 1 and not switch_page(page, n):
                break
            autoscroll(page)
            out = out_dir / f"{name} — страница {n}.png"
            page.screenshot(path=str(out), full_page=True, timeout=180_000)
            files.append(str(out))
            print(f"   [ok] страница {n}  ({first_cards(page)[:38]}…)")

        return {"store": name, "store_url": store_url, "files": files,
                "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
    finally:
        page.close()


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description="Пакетные скрины магазинов AliExpress")
    ap.add_argument("--profile", type=int, default=828976678)
    ap.add_argument("--pages", type=int, default=4)
    ap.add_argument("--list", type=Path, default=LIST_FILE)
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    ap.add_argument("--limit", type=int, help="обработать не больше N магазинов за запуск")
    ap.add_argument("--only", help="номера магазинов из --status через запятую, напр. 3,7,12")
    ap.add_argument("--retry-failed", action="store_true", help="повторить упавшие")
    ap.add_argument("--status", action="store_true", help="показать прогресс и выйти")
    args = ap.parse_args()

    items = parse_list(args.list)
    st = load_state()

    # нумерация магазинов сквозная по файлу — на неё ссылается --only
    for n, it in enumerate(items, 1):
        it["n"] = n

    if args.status:
        print(f"всего ссылок: {len(items)}")
        print(f"снято:        {len(st['done'])}")
        print(f"с ошибкой:    {len(st['failed'])}")
        print("\nномер  статус  магазин")
        for it in items:
            mark = "снят " if it["url"] in st["done"] else (
                   "ошибка" if it["url"] in st["failed"] else "  -   ")
            print(f"{it['n']:>4}  {mark}  {it['label'][:70]}")
        print("\nвыбрать нужные:  python batch.py --only 3,7,12")
        return 0

    if args.only:
        want = {int(x) for x in re.findall(r"\d+", args.only)}
        todo = [i for i in items if i["n"] in want]     # выбранные снимаем даже повторно
    else:
        todo = [i for i in items if i["url"] not in st["done"]]
        if not args.retry_failed:
            todo = [i for i in todo if i["url"] not in st["failed"]]
    if args.limit:
        todo = todo[: args.limit]

    print(f"[i] всего {len(items)}, снято {len(st['done'])}, к обработке {len(todo)}")
    if not todo:
        print("[ok] всё уже снято")
        return 0

    from playwright.sync_api import sync_playwright

    port = DolphinLocal.discover()
    if port is None:
        print("[x] Local API не отвечает — запущено ли приложение Dolphin{anty}?")
        return 1

    api = DolphinLocal(port=port)
    auto = (start_with_retry(api, args.profile).get("automation") or {})
    if not auto.get("port"):
        print("[x] Local API не вернул CDP-порт")
        return 1
    print(f"[ok] CDP порт {auto['port']}")

    args.out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}")
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        close_extra_tabs(ctx)

        for i, item in enumerate(todo, 1):
            print(f"\n[{i}/{len(todo)}] {item['label']}  {item['url']}")
            try:
                st["done"][item["url"]] = shoot(ctx, item, args.pages, args.out)
                st["failed"].pop(item["url"], None)
            except Exception as e:  # noqa: BLE001 — один магазин не должен ронять пачку
                print(f"   [x] {e}")
                st["failed"][item["url"]] = {"label": item["label"], "error": str(e),
                                             "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
            save_state(st)   # пишем после каждого — обрыв не потеряет прогресс

        browser.close()

    print(f"\n[готово] снято {len(st['done'])} из {len(items)}, ошибок {len(st['failed'])}")
    print(f"[i] продолжить: python batch.py --profile {args.profile}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[i] остановлено. Прогресс сохранён, продолжить: python batch.py")
        sys.exit(130)
    except Exception as e:  # noqa: BLE001
        print(f"[x] {e}")
        sys.exit(1)
