"""
Разведка №3: прямой заход на search keyword URL и просмотр верхних вкладок.
python probe_reels_search3.py --profile 859648353 --hashtag plaidskirt
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

        url = "https://www.instagram.com/explore/search/keyword/?q=%23" + args.hashtag
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)
        page.screenshot(path="C:/Users/User/dolphin_anty/_search_kw_top.png")
        page.mouse.wheel(0, 1500)
        time.sleep(1.5)
        page.screenshot(path="C:/Users/User/dolphin_anty/_search_kw_scroll.png")

        hrefs = page.eval_on_selector_all(
            "a", "els => els.map(e => e.getAttribute('href')).filter(h => h)"
        )
        reel_links = [h for h in hrefs if h.startswith("/reel/")]
        p_links = [h for h in hrefs if h.startswith("/p/")]
        print("reel links found:", len(reel_links), reel_links[:10])
        print("p links found:", len(p_links), p_links[:10])

        browser.close()


if __name__ == "__main__":
    main()
