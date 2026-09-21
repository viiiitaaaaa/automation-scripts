"""
Сбор постов+рилсов по хэштегу Instagram с порогом по лайкам и скриншотом
каждого прошедшего порог поста (для дашборда по тренду).

Один проход, один браузер, без пересоздания сессии:
python instagram_hashtag_dashboard.py --profile 859648353 --hashtag plaidskirt --min-likes 1000 --max-posts 50
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

LIKE_JS = """
() => {
    const svg = document.querySelector('svg[aria-label="Like"]') || document.querySelector('svg[aria-label="Unlike"]');
    if (!svg) return null;
    const container = svg.closest('section') || svg.parentElement.parentElement.parentElement;
    if (!container) return null;
    const span = container.querySelector('span[role="button"][tabindex="0"]');
    return span ? span.innerText : null;
}
"""


def parse_count_text(text: str | None) -> int | None:
    if not text:
        return None
    text = text.strip().replace(",", "")
    m = re.match(r'^(\d+(?:\.\d+)?)\s*([KM])?$', text, re.I)
    if not m:
        return None
    num = float(m.group(1))
    suffix = (m.group(2) or "").upper()
    mult = {"K": 1_000, "M": 1_000_000, "": 1}[suffix]
    return int(round(num * mult))


def classify_type(url: str, page) -> str:
    # У страницы хэштега /explore/tags/<tag>/ ссылок вида /reel/ не бывает —
    # видео-посты там тоже permalink'аются как /p/. Поэтому reel определяем
    # по наличию <video> в разметке, а не по URL.
    if "/reel/" in url or page.query_selector("video"):
        return "reel"
    html = page.content()
    if 'aria-label="Carousel"' in html or "coreSpriteSidecarIconLarge" in html:
        return "carousel"
    return "photo"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", type=int, required=True)
    ap.add_argument("--hashtag", required=True)
    ap.add_argument("--min-likes", type=int, default=1000)
    ap.add_argument("--max-posts", type=int, default=50)
    ap.add_argument("--max-results", type=int, default=10,
                     help="остановиться, набрав столько постов выше порога лайков")
    ap.add_argument("--reels-only", action="store_true",
                     help="скриншотить и засчитывать в qualified только рилсы (видео-посты)")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    out_dir = Path(args.out_dir or f"C:/Users/User/Desktop/trend_{args.hashtag}")
    out_dir.mkdir(parents=True, exist_ok=True)
    shots_dir = out_dir / "shots"
    shots_dir.mkdir(exist_ok=True)

    api = DolphinLocal(port=DolphinLocal.discover())
    data = start_with_retry(api, args.profile)
    auto = data["automation"]
    ws = f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}"

    hashtag_url = f"https://www.instagram.com/explore/tags/{args.hashtag}/"

    all_results = []
    qualified = []

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws)
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_viewport_size({"width": 1120, "height": 860})

        page.goto(hashtag_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        links: list[str] = []
        seen = set()
        stall_rounds = 0
        for _ in range(50):
            hrefs = page.eval_on_selector_all(
                'a[href^="/p/"], a[href^="/reel/"]',
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
            page.mouse.wheel(0, 2400)
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
                time.sleep(3)
                raw = page.evaluate(LIKE_JS)
                likes = parse_count_text(raw)
                ptype = classify_type(link, page)
                code = link.rstrip("/").rsplit("/", 1)[-1]
                print(f"  [{i}/{len(links)}] {ptype:9} likes={likes}  ({raw!r})  {link}")
                all_results.append({"url": link, "likes": likes, "type": ptype, "code": code})

                if args.reels_only and ptype != "reel":
                    continue

                if likes is not None and likes > args.min_likes:
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
                    qualified.append({
                        "url": link, "likes": likes, "type": ptype,
                        "code": code, "thumb": thumb_path.name,
                    })
                    if len(qualified) >= args.max_results:
                        print(f"[ok] набрано {args.max_results} постов выше порога — стоп")
                        break
            except Exception as e:
                print(f"  [{i}/{len(links)}] ошибка: {e}")
            time.sleep(1)

        browser.close()

    all_results.sort(key=lambda r: (r["likes"] is None, -(r["likes"] or 0)))
    qualified.sort(key=lambda r: -r["likes"])

    with open(out_dir / "all_posts.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    with open(out_dir / "qualified.json", "w", encoding="utf-8") as f:
        json.dump(qualified, f, ensure_ascii=False, indent=2)

    print(f"\n[ok] всего просканировано: {len(all_results)}")
    print(f"[ok] прошли порог >{args.min_likes}: {len(qualified)}")
    print(f"[ok] сохранено в: {out_dir}")


if __name__ == "__main__":
    main()
