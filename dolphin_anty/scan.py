"""
Быстрая разведка списка магазинов: сколько у каждого страниц и товаров.
Без скринов и прокрутки — только открыть, прочитать пагинатор, закрыть вкладку.

    python scan.py --profile 828976678
    python scan.py --profile 828976678 --only 6,9,20
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

from dolphin import DolphinLocal, start_with_retry
from batch import LIST_FILE, parse_list, to_store_url
from shots import MAX_TABS, close_extra_tabs, store_name

SCAN = Path(__file__).with_name("scan.json")


def scan_one(ctx, item: dict) -> dict:
    if len(ctx.pages) >= MAX_TABS:
        raise RuntimeError(f"открыто {len(ctx.pages)} вкладок (лимит {MAX_TABS})")

    page = ctx.new_page()
    try:
        store_url = to_store_url(page, item["url"])
        if not store_url:
            raise RuntimeError("не нашёл магазин по этой ссылке")

        page.goto(store_url, wait_until="domcontentloaded", timeout=90_000)
        page.wait_for_selector('a[href*="/item/"]', timeout=60_000)
        time.sleep(1.5)

        info = page.evaluate("""() => {
            const nums = [...document.querySelectorAll('a')]
                .map(a => (a.innerText || '').trim())
                .filter(t => /^\\d{1,3}$/.test(t))
                .map(Number);
            const items = document.body.innerText.match(/([\\d,]+)\\s+items?/i);
            return {pages: nums.length ? Math.max(...nums) : 1,
                    items: items ? items[1] : null};
        }""")

        sid = re.search(r"/store/(\d+)", store_url)
        return {
            "n": item["n"],
            "store": (item["label"] if item["label"].lower().endswith("store")
                      else store_name(page, store_url)),
            "store_id": sid.group(1) if sid else None,
            "pages": info["pages"],
            "items": info["items"],
            "store_url": store_url,
        }
    finally:
        page.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="Разведка: сколько страниц у магазинов")
    ap.add_argument("--profile", type=int, default=828976678)
    ap.add_argument("--list", type=Path, default=LIST_FILE)
    ap.add_argument("--only", help="номера через запятую")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    items = parse_list(args.list)
    for n, it in enumerate(items, 1):
        it["n"] = n
    if args.only:
        want = {int(x) for x in re.findall(r"\d+", args.only)}
        items = [i for i in items if i["n"] in want]

    port = DolphinLocal.discover()
    if port is None:
        print("[x] Local API не отвечает")
        return 1
    api = DolphinLocal(port=port)
    auto = start_with_retry(api, args.profile)["automation"]
    print(f"[ok] CDP порт {auto['port']}\n")

    rows, seen = [], {}
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}")
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        close_extra_tabs(ctx)

        for it in items:
            try:
                r = scan_one(ctx, it)
                dup = seen.get(r["store_id"])
                r["dup_of"] = dup
                seen.setdefault(r["store_id"], r["n"])
                mark = f"  = дубль #{dup}" if dup else ""
                print(f"{r['n']:>4}  страниц: {r['pages']:<3} товаров: {str(r['items'] or '?'):<6}"
                      f" {r['store'][:45]}{mark}")
            except Exception as e:  # noqa: BLE001
                r = {"n": it["n"], "store": it["label"][:45], "error": str(e)}
                print(f"{it['n']:>4}  [x] {e}")
            rows.append(r)
            SCAN.write_text(json.dumps(rows, ensure_ascii=False, indent=1), "utf-8")

        browser.close()

    ok = [r for r in rows if not r.get("error") and not r.get("dup_of")]
    total = sum(r["pages"] for r in ok)
    print(f"\nуникальных магазинов: {len(ok)}, суммарно страниц: {total}")
    print(f"примерное время съёмки: ~{total * 0.6:.0f} мин")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:  # noqa: BLE001
        print(f"[x] {e}")
        sys.exit(1)
