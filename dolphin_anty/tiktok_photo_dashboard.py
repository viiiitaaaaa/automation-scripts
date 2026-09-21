"""
Сбор трендовых Photo Mode постов TikTok по хэштегу (лайки видны прямо в сетке).

python tiktok_photo_dashboard.py --profile 859648353 --hashtag plaidskirt --min-likes 500 --max-results 15
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright
from PIL import Image

CARD_JS = """
els => els.map(e => {
    const card = e.closest('div[class*="DivItemContainer"]') || e.closest('div[data-e2e]') || e.parentElement.parentElement.parentElement;
    const text = card ? card.innerText : '';
    return {href: e.getAttribute('href'), text: text};
})
"""

LIKE_PATTERN = re.compile(r'^\d+(?:\.\d+)?[KM]?$')


def parse_count_text(text: str) -> int | None:
    text = text.strip().replace(",", "")
    m = re.match(r'^(\d+(?:\.\d+)?)\s*([KM])?$', text, re.I)
    if not m:
        return None
    num = float(m.group(1))
    suffix = (m.group(2) or "").upper()
    mult = {"K": 1_000, "M": 1_000_000, "": 1}[suffix]
    return int(round(num * mult))


def extract_likes(card_text: str) -> int | None:
    for line in card_text.split("\n"):
        line = line.strip()
        if LIKE_PATTERN.match(line):
            return parse_count_text(line)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", type=int, required=True)
    ap.add_argument("--hashtag", required=True)
    ap.add_argument("--min-likes", type=int, default=500)
    ap.add_argument("--max-scroll-rounds", type=int, default=40)
    ap.add_argument("--max-results", type=int, default=15)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    out_dir = Path(args.out_dir or f"C:/Users/User/Desktop/tiktok_photo_{args.hashtag}")
    out_dir.mkdir(parents=True, exist_ok=True)
    shots_dir = out_dir / "shots"
    shots_dir.mkdir(exist_ok=True)

    api = DolphinLocal(port=DolphinLocal.discover())
    data = start_with_retry(api, args.profile)
    auto = data["automation"]
    ws = f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}"

    search_url = f"https://www.tiktok.com/search/photo?q=%23{args.hashtag}"

    all_results = {}

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws)
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})

        page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(10)

        stall_rounds = 0
        for round_i in range(args.max_scroll_rounds):
            items = page.eval_on_selector_all('a[href*="/photo/"]', CARD_JS)
            for it in items:
                href = (it["href"] or "").split("?")[0]
                if not href or href in all_results:
                    continue
                likes = extract_likes(it["text"])
                author = href.split("/@")[1].split("/")[0] if "/@" in href else "?"
                all_results[href] = {"url": href, "likes": likes, "author": author}
            before = len(all_results)
            page.mouse.wheel(0, 2400)
            time.sleep(2)
            after_scroll_items = page.eval_on_selector_all('a[href*="/photo/"]', "els => els.length")
            if after_scroll_items == before:
                stall_rounds += 1
                if stall_rounds >= 4:
                    break
            else:
                stall_rounds = 0

        print(f"[ok] собрано карточек: {len(all_results)}")

        ranked = sorted(
            all_results.values(),
            key=lambda r: (r["likes"] is None, -(r["likes"] or 0)),
        )
        for r in ranked[:40]:
            print(f"  likes={r['likes']}  @{r['author']}  {r['url']}")

        qualified = []
        for r in ranked:
            if r["likes"] is None or r["likes"] <= args.min_likes:
                continue
            code = r["url"].rstrip("/").rsplit("/", 1)[-1]
            try:
                page.goto(r["url"], wait_until="domcontentloaded", timeout=30000)
                time.sleep(6)
                shot_path = shots_dir / f"{code}.png"
                page.screenshot(path=str(shot_path))
                thumb_path = shots_dir / f"{code}.jpg"
                with Image.open(shot_path) as im:
                    im = im.convert("RGB")
                    w, h = im.size
                    new_w = 640
                    new_h = int(h * (new_w / w))
                    im = im.resize((new_w, new_h), Image.LANCZOS)
                    im.save(thumb_path, "JPEG", quality=82)
                shot_path.unlink()
                qualified.append({**r, "code": code, "thumb": thumb_path.name})
                print(f"[shot] {code}  likes={r['likes']}")
                if len(qualified) >= args.max_results:
                    break
            except Exception as e:
                print(f"  ошибка скрина {r['url']}: {e}")
            time.sleep(1)

        browser.close()

    with open(out_dir / "all_photos.json", "w", encoding="utf-8") as f:
        json.dump(ranked, f, ensure_ascii=False, indent=2)
    with open(out_dir / "qualified.json", "w", encoding="utf-8") as f:
        json.dump(qualified, f, ensure_ascii=False, indent=2)

    print(f"\n[ok] всего карточек: {len(all_results)}")
    print(f"[ok] прошли порог >{args.min_likes}: {len(qualified)}")
    print(f"[ok] сохранено в: {out_dir}")


if __name__ == "__main__":
    main()
