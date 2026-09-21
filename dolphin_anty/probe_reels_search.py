"""
Разведка: как искать именно рилсы по хэштегу через поиск/раздел Reels в Instagram.
python probe_reels_search.py --profile 859648353 --hashtag plaidskirt
"""
from __future__ import annotations

import argparse
import time

from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", type=int, required=True)
    ap.add_argument("--hashtag", required=True)
    args = ap.parse_args()

    api = DolphinLocal(port=DolphinLocal.discover())
    data = start_with_retry(api, args.profile)
    auto = data["automation"]
    ws = f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}"

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws)
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_viewport_size({"width": 1280, "height": 900})

        # 1) Обычный поиск по хэштегу через поисковую строку
        page.goto("https://www.instagram.com/explore/search/keyword/?q=%23" + args.hashtag,
                   wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)
        page.screenshot(path="C:/Users/User/dolphin_anty/_reels_search1.png")
        print("[1] search keyword page saved")

        # 2) Раздел Reels напрямую
        page.goto("https://www.instagram.com/reels/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)
        page.screenshot(path="C:/Users/User/dolphin_anty/_reels_tab.png")
        print("[2] /reels/ page saved")

        # 3) hashtag page с проверкой наличия вкладок сверху (Top/Reels/Tagged и т.п.)
        page.goto(f"https://www.instagram.com/explore/tags/{args.hashtag}/",
                   wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)
        tabs_text = page.eval_on_selector_all(
            'a, div[role="tab"], span',
            "els => els.map(e=>e.innerText).filter(t=>t && t.length<20)"
        )
        print("[3] visible short texts on hashtag page (sample):", list(dict.fromkeys(tabs_text))[:60])
        page.screenshot(path="C:/Users/User/dolphin_anty/_reels_hashtag.png")

        browser.close()


if __name__ == "__main__":
    main()
