"""
Разведка: как достать число лайков на странице отдельного видео TikTok.
python probe_tiktok2.py --profile 859648353 --url "https://www.tiktok.com/@danignzlzz1/video/7678595872023711006"
"""
from __future__ import annotations

import argparse
import time

from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", type=int, required=True)
    ap.add_argument("--url", required=True)
    args = ap.parse_args()

    api = DolphinLocal(port=DolphinLocal.discover())
    data = start_with_retry(api, args.profile)
    auto = data["automation"]
    ws = f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}"

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws)
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_viewport_size({"width": 1120, "height": 860})

        page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(10)
        page.screenshot(path="C:/Users/User/dolphin_anty/_tt_video.png")

        like_el = page.query_selector('[data-e2e="like-count"]')
        comment_el = page.query_selector('[data-e2e="comment-count"]')
        share_el = page.query_selector('[data-e2e="share-count"]')
        print("like:", like_el.inner_text() if like_el else None)
        print("comment:", comment_el.inner_text() if comment_el else None)
        print("share:", share_el.inner_text() if share_el else None)

        browser.close()


if __name__ == "__main__":
    main()
