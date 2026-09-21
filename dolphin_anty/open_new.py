"""
Открыть вкладками магазины AliExpress, пропуская уже отсканированные.

Отличия от open_links.py:
  * цепляется к УЖЕ ОТКРЫТОМУ профилю, если он жив (пользователь открыл сам);
  * разворачивает короткие ссылки и приводит товарные ссылки к их магазину;
  * пропускает магазины, которые уже есть в state_tabs.json / state.json —
    сверка по ID магазина, а не по названию (названия повторяются, ID нет);
  * держит браузер живым, пока работает процесс.

    python open_new.py --file links_new.txt
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

from batch import to_store_url

HERE = Path(__file__).parent
STATE_TABS = HERE / "state_tabs.json"
STATE = HERE / "state.json"
REPORT = HERE / "open_new.json"


def known_ids() -> dict[str, str]:
    """ID уже отснятых магазинов -> название, из обоих файлов прогресса."""
    ids: dict[str, str] = {}
    if STATE_TABS.exists():
        for name, rec in json.loads(STATE_TABS.read_text("utf-8")).items():
            m = re.search(r"/store/(\d+)", rec.get("url", ""))
            if m:
                ids[m.group(1)] = name
    if STATE.exists():
        for rec in json.loads(STATE.read_text("utf-8")).get("done", {}).values():
            m = re.search(r"/store/(\d+)", rec.get("store_url", ""))
            if m:
                ids[m.group(1)] = rec.get("store", "?")
    return ids


def parse_links(path: Path) -> list[tuple[str, str]]:
    """Файл вида «название / ссылка» -> пары (название, ссылка)."""
    out: list[tuple[str, str]] = []
    name = "?"
    for ln in path.read_text("utf-8", errors="replace").splitlines():
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("http"):
            out.append((name, ln))
        else:
            name = ln
    return out


def find_cdp() -> str:
    """Живой CDP уже запущенного браузера (порт Dolphin выдаёт случайный)."""
    import subprocess
    out = subprocess.run(["netstat", "-ano", "-p", "TCP"],
                         capture_output=True, text=True).stdout
    ports = sorted({int(m.group(1)) for m in
                    (re.search(r"127\.0\.0\.1:(\d+)\s+.*LISTENING", ln)
                     for ln in out.splitlines()) if m})
    for p in ports:
        try:
            r = requests.get(f"http://127.0.0.1:{p}/json/version", timeout=1)
            if r.status_code == 200 and "webSocketDebuggerUrl" in r.text:
                return r.json()["webSocketDebuggerUrl"]
        except Exception:  # noqa: BLE001
            pass
    raise RuntimeError("живого CDP нет")


def main() -> int:
    ap = argparse.ArgumentParser(description="Открыть новые магазины вкладками")
    ap.add_argument("--file", type=Path, required=True)
    ap.add_argument("--profile", type=int, default=828976678)
    ap.add_argument("--hours", type=float, default=6)
    ap.add_argument("--no-hold", action="store_true",
                    help="выйти сразу; браузер тогда погаснет вместе с процессом")
    ap.add_argument("--max-tabs", type=int, default=40)
    args = ap.parse_args()

    links = parse_links(args.file)
    done_ids = known_ids()
    print(f"[i] ссылок: {len(links)}; уже отснятых магазинов в базе: {len(done_ids)}")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        started = False
        try:
            browser = p.chromium.connect_over_cdp(find_cdp())
            print("[ok] прицепился к уже открытому профилю")
        except Exception as e:  # noqa: BLE001
            print(f"[i] живого браузера нет ({type(e).__name__}) — поднимаю профиль")
            from dolphin import DolphinLocal, start_with_retry
            api = DolphinLocal(port=DolphinLocal.discover() or 3001)
            auto = start_with_retry(api, args.profile)["automation"]
            browser = p.chromium.connect_over_cdp(
                f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}")
            started = True
            print(f"[ok] профиль поднят, CDP {auto['port']}")

        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        opened: list[dict] = []
        skipped: list[dict] = []
        failed: list[dict] = []
        # Магазины, чьи вкладки уже висят в окне: прицепившись к живому браузеру,
        # мы иначе откроем их по второму разу и получим кучу дублей.
        seen: set[str] = {m.group(1) for m in
                          (re.search(r"/store/(\d+)", pg.url) for pg in ctx.pages) if m}
        if seen:
            print(f"[i] уже открыто вкладок с магазинами: {len(seen)} — их пропущу")

        scout = ctx.new_page()   # одна служебная вкладка на все развороты ссылок
        for i, (name, url) in enumerate(links, 1):
            try:
                store_url = to_store_url(scout, url)
            except Exception as e:  # noqa: BLE001
                print(f"{i:>3}. [x] {name} — {str(e)[:70]}")
                failed.append({"name": name, "url": url, "error": str(e)[:200]})
                continue
            if not store_url:
                print(f"{i:>3}. [x] {name} — магазин не определился")
                failed.append({"name": name, "url": url, "error": "магазин не найден"})
                continue

            sid = re.search(r"/store/(\d+)", store_url).group(1)
            if sid in done_ids:
                print(f"{i:>3}. [-] {name} — уже сканировали ({done_ids[sid]}, id {sid})")
                skipped.append({"name": name, "id": sid, "as": done_ids[sid]})
                continue
            if sid in seen:
                print(f"{i:>3}. [-] {name} — дубль в списке (id {sid})")
                skipped.append({"name": name, "id": sid, "as": "дубль в списке"})
                continue
            if len(opened) >= args.max_tabs:
                print(f"{i:>3}. [!] лимит {args.max_tabs} вкладок — остальное не открываю")
                break

            seen.add(sid)
            pg = ctx.new_page()
            try:
                pg.goto(store_url, wait_until="domcontentloaded", timeout=90_000)
                pg.wait_for_selector('a[href*="/item/"]', timeout=60_000)
                cnt = pg.evaluate("""() => {
                    const m = document.body.innerText.match(/([\\d,]+)\\s+items?/i);
                    return m ? m[1] : null;
                }""")
                print(f"{i:>3}. [ok] {name} (id {sid}) — товаров: {cnt or '?'}")
                opened.append({"name": name, "id": sid, "url": store_url, "items": cnt})
            except Exception as e:  # noqa: BLE001
                print(f"{i:>3}. [x] {name} — {str(e)[:70]}")
                failed.append({"name": name, "url": store_url, "error": str(e)[:200]})
            REPORT.write_text(json.dumps(
                {"opened": opened, "skipped": skipped, "failed": failed},
                ensure_ascii=False, indent=1), "utf-8")

        scout.close()
        print(f"\n[итог] открыто {len(opened)}, пропущено {len(skipped)}, "
              f"с ошибкой {len(failed)}; вкладок в окне: {len(ctx.pages)}")

        # Держим окно живым ВСЕГДА, а не только когда профиль подняли мы:
        # если прицепились к чужому браузеру, чей процесс-хозяин уже умер,
        # он погаснет сразу после нашего выхода — вкладки пропадут.
        if not args.no_hold:
            print(f"[i] держу браузер {args.hours} ч "
                  f"(профиль {'поднят мной' if started else 'был уже открыт'}) — "
                  f"останови задачу, когда закончишь")
            try:
                time.sleep(args.hours * 3600)
            except KeyboardInterrupt:
                pass
        browser.close()   # рвёт только CDP, вкладки остаются

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[i] остановлено")
        sys.exit(130)
    except Exception as e:  # noqa: BLE001
        print(f"[x] {e}")
        sys.exit(1)
