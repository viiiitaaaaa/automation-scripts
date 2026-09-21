"""
Сбор постов по хэштегу Instagram: лайки, тип (фото/видео/рилс), ссылка.
Фильтр: likes > MIN_LIKES. Результат -> CSV + консоль.

python instagram_hashtag_likes.py --profile 859648353 --hashtag plaidskirt --min-likes 1000 --max-posts 60
"""
from __future__ import annotations

import argparse
import csv
import re
import time

from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright


DATE_RE = re.compile(
    r'^(January|February|March|April|May|June|July|August|September|October|November|December)'
    r'\s+\d{1,2},\s+\d{4}$'
)


def parse_like_count(page) -> int | None:
    """Ищем точное число лайков.

    Новый интерфейс Instagram не пишет текст "X likes" на странице поста —
    вместо этого под кнопками (сердце/комментарий/репост) идут голые числа.
    Они стоят подряд прямо перед строкой даты поста ("February 17, 2025"),
    в порядке: лайки, комментарии, репосты. Берём первое (самое верхнее)
    число этого блока — это и есть лайки.
    """
    html = page.content()

    # 1) точное число в title="1,234" рядом с "likes" (старый формат)
    m = re.search(r'title="([\d,]+)"[^>]*>[\s\S]{0,40}?like', html, re.I)
    if m:
        return int(m.group(1).replace(",", ""))

    text = page.inner_text("body")
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]

    # 2) блок голых чисел прямо перед датой поста (новый формат)
    for i, ln in enumerate(lines):
        if DATE_RE.match(ln):
            j = i - 1
            digit_run = []
            while j >= 0 and re.fullmatch(r'[\d,]+', lines[j]):
                digit_run.append(lines[j])
                j -= 1
            if digit_run:
                digit_run.reverse()  # теперь в порядке: лайки, комментарии, репосты
                return int(digit_run[0].replace(",", ""))
            break

    # 3) текст "1,234 likes" / "1,234 others" (старый формат)
    m = re.search(r'([\d][\d,]*)\s+likes\b', text, re.I)
    if m:
        return int(m.group(1).replace(",", ""))

    # 4) сокращённое "12.3K likes" / "1.2M likes"
    m = re.search(r'([\d]+(?:\.\d+)?)\s*([KM])\s+likes\b', text, re.I)
    if m:
        num = float(m.group(1))
        mult = 1000 if m.group(2).upper() == "K" else 1_000_000
        return int(num * mult)

    return None


def classify_type(url: str, page) -> str:
    if "/reel/" in url:
        return "reel"
    html = page.content()
    if 'aria-label="Carousel"' in html or "coreSpriteSidecarIconLarge" in html:
        return "carousel"
    if page.query_selector("video"):
        return "video"
    return "photo"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", type=int, required=True)
    ap.add_argument("--hashtag", required=True, help="без решётки, напр. plaidskirt")
    ap.add_argument("--min-likes", type=int, default=1000)
    ap.add_argument("--max-posts", type=int, default=60, help="сколько ссылок собрать из сетки")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    out_path = args.out or f"C:/Users/User/Desktop/instagram_{args.hashtag}_likes.csv"

    api = DolphinLocal(port=DolphinLocal.discover())
    data = start_with_retry(api, args.profile)
    auto = data["automation"]
    ws = f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}"

    hashtag_url = f"https://www.instagram.com/explore/search/keyword/?q=%23{args.hashtag}"

    results = []

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws)
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(hashtag_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        # Собираем уникальные ссылки на посты/рилсы, прокручивая сетку
        links: list[str] = []
        seen = set()
        stall_rounds = 0
        for _ in range(40):
            hrefs = page.eval_on_selector_all(
                'a[href*="/p/"], a[href*="/reel/"]',
                "els => els.map(e => e.getAttribute('href'))",
            )
            for h in hrefs:
                if not h:
                    continue
                full = "https://www.instagram.com" + h.split("?")[0]
                if full not in seen:
                    seen.add(full)
                    links.append(full)
            if len(links) >= args.max_posts:
                break
            before = len(links)
            page.mouse.wheel(0, 2200)
            time.sleep(1.5)
            if len(links) == before:
                stall_rounds += 1
                if stall_rounds >= 4:
                    break
            else:
                stall_rounds = 0

        links = links[: args.max_posts]
        print(f"[ok] собрано ссылок: {len(links)}")

        for i, link in enumerate(links, 1):
            try:
                page.goto(link, wait_until="domcontentloaded", timeout=30000)
                time.sleep(2)
                likes = parse_like_count(page)
                ptype = classify_type(link, page)
                print(f"  [{i}/{len(links)}] {ptype:9} likes={likes}  {link}")
                if likes is not None and likes > args.min_likes:
                    results.append({"url": link, "likes": likes, "type": ptype})
            except Exception as e:
                print(f"  [{i}/{len(links)}] ошибка: {e}")
            time.sleep(1)

        browser.close()

    results.sort(key=lambda r: r["likes"], reverse=True)
    with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["url", "likes", "type"])
        w.writeheader()
        w.writerows(results)

    print(f"\n[ok] постов с likes > {args.min_likes}: {len(results)}")
    print(f"[ok] сохранено: {out_path}")
    for r in results:
        print(f"  {r['likes']:>7}  {r['type']:9}  {r['url']}")


if __name__ == "__main__":
    main()
