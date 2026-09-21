"""Сбор отзывов и хешей картинок с карточек AliExpress по списку ссылок.

Возобновляемый: результат пишется в JSONL после каждого товара, повторный запуск
пропускает уже собранные.

    python ali_scrape.py            — весь список
    python ali_scrape.py --limit 5  — только первые 5 (для проверки)
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

import openpyxl

CDP = Path(__file__).with_name("cdp.json")
XLSX = Path(r"C:\Users\User\Desktop\скрины магазинов\Новая папка\ссылки на товары.xlsx")
OUT = Path(r"C:\Users\User\artmellio-system\data\products\ali-reviews.jsonl")

sys.stdout.reconfigure(encoding="utf-8")
LIMIT = None
if "--limit" in sys.argv:
    LIMIT = int(sys.argv[sys.argv.index("--limit") + 1])

FEED = ("https://feedback.aliexpress.com/pc/searchEvaluation.do"
        "?productId={pid}&lang=en_US&country=GB&page={page}&pageSize=20"
        "&filter=all&sort=complex_default")


def load_links():
    wb = openpyxl.load_workbook(XLSX, read_only=True)
    ws = wb["Ссылки"]
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        shop, file, url, dist, conf, name = (list(r) + [None] * 6)[:6]
        if not url:
            continue
        m = re.search(r"/item/(\d+)", str(url))
        if not m:
            continue
        rows.append({"shop": shop, "file": file, "url": str(url),
                     "pid": m.group(1), "conf": conf, "ali_title": name})
    return rows


def done_ids():
    """Успешно собранные. Записи с ошибкой считаем несобранными — их надо повторить."""
    if not OUT.exists():
        return set()
    ids = set()
    for line in OUT.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
            if not r.get("error") and r.get("images"):
                ids.add(r["pid"])
        except Exception:
            pass
    return ids


# только адреса картинок, а не весь HTML — иначе браузер съедает память
IMG_JS = """() => [...document.querySelectorAll('img')]
    .map(i => i.currentSrc || i.src || '')
    .filter(s => s.includes('alicdn'))"""


def main() -> int:
    links = load_links()
    have = done_ids()
    todo = [l for l in links if l["pid"] not in have]
    if LIMIT:
        todo = todo[:LIMIT]
    print(f"Ссылок всего: {len(links)} | уже собрано: {len(have)} | к сбору: {len(todo)}")
    OUT.parent.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright
    cdp = json.loads(CDP.read_text(encoding="utf-8"))

    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(cdp["url"])
        ctx = b.contexts[0]
        pg = ctx.new_page()

        for n, item in enumerate(todo, 1):
            rec = dict(item, images=[], reviews=[], error=None)
            try:
                # каждые 10 товаров — свежая вкладка, иначе память течёт
                if n % 10 == 0:
                    pg.close()
                    pg = ctx.new_page()
                pg.goto(item["url"], wait_until="commit", timeout=60_000)
                try:
                    pg.wait_for_selector("img", timeout=25_000)
                except Exception:
                    pass
                time.sleep(3)
                srcs = pg.evaluate(IMG_JS)
                rec["images"] = sorted(set(
                    h for s in srcs
                    for h in re.findall(r"(S[0-9a-f]{32}[A-Za-z])\.(?:jpg|jpeg|webp|png)", s)))
                # настоящий числовой id берём из финального URL
                m = re.search(r"/item/(\d+)", pg.url)
                pid = m.group(1) if m else item["pid"]

                seen, page = set(), 1
                while page <= 5:
                    r = ctx.request.get(FEED.format(pid=pid, page=page), timeout=60_000)
                    if r.status != 200:
                        break
                    data = json.loads(r.text())
                    ev = (data.get("data") or {}).get("evaViewList") or []
                    if not ev:
                        break
                    for e in ev:
                        key = (e.get("buyerName"), e.get("buyerFeedback"))
                        if key in seen:
                            continue
                        seen.add(key)
                        rec["reviews"].append({
                            "rating": round((e.get("buyerEval") or 0) / 20),
                            "name": e.get("buyerName"),
                            "country": e.get("buyerCountry"),
                            "date": e.get("evalDate"),
                            "text": (e.get("buyerFeedback") or "").strip(),
                            "photos": e.get("images") or [],
                            "sku": e.get("skuInfo"),
                        })
                    page += 1
                    time.sleep(0.8)
            except Exception as e:  # noqa: BLE001
                rec["error"] = str(e)[:200]

            with OUT.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(f"{n:>3}/{len(todo)}  отзывов {len(rec['reviews']):>3}  "
                  f"картинок {len(rec['images']):>2}  {str(item['ali_title'])[:40]}"
                  f"{'  ОШИБКА: ' + rec['error'] if rec['error'] else ''}")
            time.sleep(1.2)

        pg.close()
    print("\nГотово. Файл:", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
