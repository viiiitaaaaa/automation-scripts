"""
Разведка: страница хэштега в TikTok, доступна ли без логина, что в разметке.
python probe_tiktok.py --profile 859648353 --hashtag plaidskirt
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

        url = f"https://www.tiktok.com/tag/{args.hashtag}"
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(10)
        page.mouse.wheel(0, 1200)
        time.sleep(3)
        page.screenshot(path="C:/Users/User/dolphin_anty/_tt_tag.png")

        links = page.eval_on_selector_all(
            'a[href*="/video/"]',
            "els => els.map(e => e.getAttribute('href'))",
        )
        print("video links found:", len(links), links[:10])

        all_a = page.eval_on_selector_all(
            "a", "els => els.map(e => e.getAttribute('href')).filter(h=>h)"
        )
        print("total <a> hrefs:", len(all_a))
        print("sample hrefs:", all_a[:15])

        title = page.title()
        print("page title:", title)

        browser.close()


if __name__ == "__main__":
    main()
