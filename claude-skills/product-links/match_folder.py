# -*- coding: utf-8 -*-
"""
Ссылки на товары для папки со сборной подборкой.

Файлы названы по магазину (`<Магазин>-001.png`), поэтому магазин определяется
из имени файла, его ссылка берётся из state_tabs.json, каталог обходится один
раз на магазин, а результат сводится в один Excel.

    python match_folder.py --folder "C:\\...\\Новая папка"
    python match_folder.py --folder "..." --out "ссылки.xlsx"
"""
import argparse
import io
import json
import os
import re
import sys
import time
from collections import OrderedDict
from pathlib import Path

import requests
from PIL import Image
import imagehash
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import DolphinLocal, start_with_retry   # noqa: E402
from shots import switch_page, autoscroll            # noqa: E402

PROFILE = 828976678
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state_tabs.json")
MATCH_GOOD, MATCH_MAYBE = 8, 16

EXTRACT_JS = r"""
() => {
  const seen = new Set(), out = [];
  for (const a of document.querySelectorAll('a[href*="/item/"]')) {
    const img = a.querySelector('img');
    if (!img) continue;
    const src = img.currentSrc || img.src || img.getAttribute('data-src') || '';
    if (!src) continue;
    const href = a.href.split('?')[0];
    if (seen.has(href)) continue;
    seen.add(href);
    out.push({url: href, img: src, title: (img.getAttribute('alt') || '').trim()});
  }
  return out;
}
"""


def shop_of(filename):
    """Имя магазина = всё до '-NNN' в конце имени файла."""
    stem = Path(filename).stem
    m = re.match(r"^(.*?)[-—]\s*\d+$", stem)
    return (m.group(1) if m else stem).strip()


def store_urls():
    if not os.path.exists(STATE):
        return {}
    data = json.load(io.open(STATE, encoding="utf-8"))
    return {k: v.get("url", "") for k, v in data.items() if isinstance(v, dict)}


def settle(page):
    """Дождаться, пока страница перестанет редиректить (магазин любит прыгать на .us)."""
    last = None
    for _ in range(10):
        try:
            cur = page.url
        except Exception:
            time.sleep(1); continue
        if cur == last:
            break
        last = cur
        time.sleep(1.5)
    try:
        page.wait_for_selector('a[href*="/item/"]', timeout=60000)
    except Exception:
        print("     карточки не появились")


def scrape(page, url, max_pages):
    products = {}
    page.goto(url, wait_until="domcontentloaded", timeout=90000)
    settle(page)
    page.wait_for_timeout(2000)
    for n in range(1, max_pages + 1):
        if n > 1 and not switch_page(page, n):
            break
        # редирект во время прокрутки убивает контекст — пробуем ещё раз
        items = []
        for attempt in (1, 2):
            try:
                autoscroll(page)
                page.wait_for_selector('a[href*="/item/"]', timeout=30000)
                items = page.evaluate(EXTRACT_JS)
                break
            except Exception as e:
                print("     попытка %d не удалась (%s)" % (attempt, str(e)[:60]))
                time.sleep(3)
                settle(page)
        new = sum(1 for it in items if it["url"] not in products)
        for it in items:
            products.setdefault(it["url"], it)
        print("     стр %d: %d карточек, новых %d, всего %d" % (n, len(items), new, len(products)))
        if not items:
            break
    return list(products.values())


def hash_products(items):
    ses = requests.Session()
    ses.headers["User-Agent"] = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                 "(KHTML, like Gecko) Chrome/120 Safari/537.36")
    for i, it in enumerate(items, 1):
        src = it["img"]
        if src.startswith("//"):
            src = "https:" + src
        try:
            r = ses.get(src, timeout=20)
            r.raise_for_status()
            it["phash"] = imagehash.phash(Image.open(io.BytesIO(r.content)).convert("RGB"))
        except Exception:
            it["phash"] = None
        if i % 100 == 0 or i == len(items):
            print("     превью %d/%d" % (i, len(items)))


def save_xlsx(rows, path):
    wb = Workbook()
    ws = wb.active
    ws.title = "Ссылки"
    ws.append(["Магазин", "Файл", "Ссылка на товар", "Расстояние", "Уверенность", "Название"])
    for c in ws[1]:
        c.font = Font(bold=True)
    for r in rows:
        ws.append(r)
    for col, w in zip("ABCDEF", (45, 45, 60, 12, 20, 60)):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for row in ws.iter_rows(min_row=2, min_col=6, max_col=6):
        for c in row:
            c.alignment = Alignment(wrap_text=False)
    wb.save(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", required=True)
    ap.add_argument("--profile", type=int, default=PROFILE)
    ap.add_argument("--pages", type=int, default=60)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    folder = Path(args.folder)
    out_xlsx = args.out or str(folder / "ссылки на товары.xlsx")

    exts = {".png", ".jpg", ".jpeg", ".webp"}
    groups = OrderedDict()
    for f in sorted(folder.iterdir()):
        if f.suffix.lower() in exts:
            groups.setdefault(shop_of(f.name), []).append(f)
    if not groups:
        print("В папке нет картинок."); sys.exit(1)

    print("Магазинов в папке: %d" % len(groups))
    urls = store_urls()
    for shop, files in groups.items():
        print("  %-55s фото: %3d  %s" % (shop, len(files),
                                         "ссылка есть" if urls.get(shop) else "ССЫЛКА НЕ НАЙДЕНА"))

    api = DolphinLocal(port=DolphinLocal.discover() or 3001)
    print("\nПоднимаю профиль %d…" % args.profile)
    auto = start_with_retry(api, args.profile)["automation"]
    print("  CDP %s" % auto["port"])

    from playwright.sync_api import sync_playwright
    rows = []
    with sync_playwright() as pw:
        browser = pw.chromium.connect_over_cdp("ws://127.0.0.1:%s%s" % (auto["port"], auto["wsEndpoint"]))
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()

        for shop, files in groups.items():
            url = urls.get(shop)
            print("\n=== %s" % shop)
            if not url:
                for f in files:
                    rows.append([shop, f.name, "ССЫЛКА НА МАГАЗИН НЕ НАЙДЕНА", "", "", ""])
                continue
            page = ctx.new_page()
            try:
                try:
                    items = scrape(page, url, args.pages)
                except Exception as e:
                    print("   [x] магазин не собрался: %s" % str(e)[:80])
                    for f in files:
                        rows.append([shop, f.name, "ОШИБКА ОБХОДА КАТАЛОГА", "", "", ""])
                    save_xlsx(rows, out_xlsx)
                    continue
                print("   товаров в каталоге: %d" % len(items))
                hash_products(items)
                scored = [it for it in items if it.get("phash") is not None]
                for f in files:
                    try:
                        h = imagehash.phash(Image.open(f).convert("RGB"))
                    except Exception as e:
                        rows.append([shop, f.name, "не открылось: %s" % e, "", "", ""]); continue
                    cand = sorted(((it, h - it["phash"]) for it in scored), key=lambda t: t[1])[:2]
                    if not cand:
                        rows.append([shop, f.name, "НЕ НАЙДЕНО", "", "", ""]); continue
                    best, dist = cand[0]
                    conf = ("высокая" if dist <= MATCH_GOOD else
                            "средняя" if dist <= MATCH_MAYBE else "низкая — проверить")
                    rows.append([shop, f.name, best["url"], dist, conf, best["title"]])
                save_xlsx(rows, out_xlsx)          # сохраняем после каждого магазина
                print("   сохранено в Excel: %d строк" % len(rows))
            finally:
                page.close()
                time.sleep(1)

    save_xlsx(rows, out_xlsx)

    found = sum(1 for r in rows if str(r[2]).startswith("http"))
    print("\nГотово: %s" % out_xlsx)
    print("строк: %d, ссылок найдено: %d" % (len(rows), found))


if __name__ == "__main__":
    main()
