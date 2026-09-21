# -*- coding: utf-8 -*-
"""
Поиск ссылок на товары AliExpress по локальным фото.

Обходит каталог магазина в профиле Dolphin{anty}, скачивает превью карточек,
считает phash и сопоставляет с фото из вашей папки.

    python match_products.py --store 1105084156 --folder "<папка с фото>"
    python match_products.py --store 1105084156 --folder "<папка>" --out result.csv

Профиль по умолчанию — рабочий 828976678. Токен Local API не нужен.
Домен всегда aliexpress.com: .ru в этом браузере запрещён.
"""
import argparse
import csv
import io
import os
import re
import sys
from pathlib import Path

import requests
from PIL import Image
import imagehash

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dolphin import DolphinLocal, start_with_retry   # noqa: E402
from shots import switch_page, autoscroll            # noqa: E402

DEFAULT_PROFILE = 828976678
TOP_N = 3
MATCH_GOOD = 8        # расстояние phash: почти наверняка тот же товар
MATCH_MAYBE = 16      # похоже, но стоит глянуть глазами

# Карточки берём прямо из DOM: любая ссылка на /item/ с картинкой внутри.
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


def store_url(store):
    """Тот же адрес каталога, на котором снимались скрины."""
    sid = re.search(r"(\d+)", str(store)).group(1)
    return ("https://www.aliexpress.com/store/%s/pages/all-items.html"
            "?sortType=bestmatch_sort&shop_sortType=bestmatch_sort" % sid)


def scrape(page, store, max_pages):
    """Листаем каталог кликом по пагинатору — адрес с &page=N его не переключает."""
    products = {}
    page.goto(store_url(store), wait_until="domcontentloaded", timeout=90000)
    try:
        page.wait_for_selector('a[href*="/item/"]', timeout=60000)
    except Exception:
        print("    карточки не появились за 60с")
    print("  открыто: %s" % page.url)
    print("  заголовок: %s" % (page.title() or "")[:80])
    page.wait_for_timeout(2000)

    for n in range(1, max_pages + 1):
        if n > 1 and not switch_page(page, n):
            print("    страницы закончились на %d" % (n - 1))
            break
        autoscroll(page)
        try:
            page.wait_for_selector('a[href*="/item/"]', timeout=30000)
        except Exception:
            pass
        try:
            items = page.evaluate(EXTRACT_JS)
        except Exception as e:
            print("    ошибка разбора: %s" % e)
            items = []
        new = 0
        for it in items:
            if it["url"] not in products:
                products[it["url"]] = it
                new += 1
        print("  страница %d: карточек %d, новых %d, всего %d" % (n, len(items), new, len(products)))
        if not items:
            print("    пусто — каталог закончился")
            break
    return list(products.values())


def hash_local(folder):
    exts = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
    out = []
    for f in sorted(Path(folder).iterdir()):
        if f.suffix.lower() in exts:
            try:
                out.append((f, imagehash.phash(Image.open(f).convert("RGB"))))
            except Exception as e:
                print("  не открылось %s: %s" % (f.name, e))
    return out


def hash_products(items, page):
    """Превью тянем через сам браузер Dolphin — тем же IP и куками, что и каталог."""
    ses = requests.Session()
    ses.headers["User-Agent"] = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                 "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36")
    ok = 0
    for i, it in enumerate(items, 1):
        src = it["img"]
        if src.startswith("//"):
            src = "https:" + src
        data = None
        try:
            r = ses.get(src, timeout=20)
            r.raise_for_status()
            data = r.content
        except Exception:
            pass
        if data:
            try:
                it["phash"] = imagehash.phash(Image.open(io.BytesIO(data)).convert("RGB"))
                ok += 1
            except Exception:
                it["phash"] = None
        else:
            it["phash"] = None
        if i % 50 == 0 or i == len(items):
            print("  превью: %d/%d (успешно %d)" % (i, len(items), ok))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--store", required=True, help="ID магазина или ссылка на него")
    ap.add_argument("--folder", required=True, help="папка с локальными фото товаров")
    ap.add_argument("--profile", type=int, default=DEFAULT_PROFILE)
    ap.add_argument("--pages", type=int, default=60)
    ap.add_argument("--out", default=None, help="куда сохранить CSV")
    args = ap.parse_args()

    out_csv = args.out or os.path.join(args.folder, "ссылки на товары.csv")

    print("Считаю хеши локальных фото…")
    locals_ = hash_local(args.folder)
    print("  фото: %d" % len(locals_))
    if not locals_:
        print("В папке нет изображений."); sys.exit(1)

    api = DolphinLocal()
    print("Поднимаю профиль %d…" % args.profile)
    info = start_with_retry(api, args.profile)
    port = (info.get("automation") or {}).get("port") or info.get("port")
    print("  CDP порт: %s" % port)

    from playwright.sync_api import sync_playwright
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.connect_over_cdp("http://127.0.0.1:%s" % port)
            ctx = browser.contexts[0] if browser.contexts else browser.new_context()
            page = ctx.new_page()

            print("Собираю каталог магазина…")
            items = scrape(page, args.store, args.pages)
            print("  товаров: %d" % len(items))
            if not items:
                print("Каталог пуст — проверьте, не открылась ли вместо магазина заглушка."); return

            print("Скачиваю превью и считаю хеши…")
            hash_products(items, page)
            page.close()

            scored = [it for it in items if it.get("phash") is not None]
            print("Сопоставляю…")
            rows = []
            for path, h in locals_:
                cand = sorted(((it, h - it["phash"]) for it in scored), key=lambda t: t[1])[:TOP_N]
                rows.append((path, cand))

            with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, delimiter=";")
                w.writerow(["Файл", "Ссылка", "Расстояние", "Уверенность", "Название",
                            "Кандидат 2", "Расст. 2", "Кандидат 3", "Расст. 3"])
                for path, cand in rows:
                    if not cand:
                        w.writerow([path.name, "НЕ НАЙДЕНО", "", "", "", "", "", "", ""]); continue
                    best, dist = cand[0]
                    conf = ("высокая" if dist <= MATCH_GOOD else
                            "средняя" if dist <= MATCH_MAYBE else "низкая — проверить глазами")
                    row = [path.name, best["url"], dist, conf, best["title"]]
                    for c in cand[1:3]:
                        row += [c[0]["url"], c[1]]
                    row += [""] * (9 - len(row))
                    w.writerow(row)

            print("\nГотово: %s\n" % out_csv)
            for path, cand in rows:
                if cand:
                    print("  %-50s -> %s  (%d)" % (path.name[:50], cand[0][0]["url"], cand[0][1]))
                else:
                    print("  %-50s -> не найдено" % path.name[:50])
    finally:
        print("Профиль оставляю запущенным (гасить: python dolphin.py --profile %d --stop --no-automation)"
              % args.profile)


if __name__ == "__main__":
    main()
