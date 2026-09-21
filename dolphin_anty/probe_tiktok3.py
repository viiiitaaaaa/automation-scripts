"""
Разведка: страница поиска TikTok по хэштегу (не /tag/), что там за разметка/сортировка.
python probe_tiktok3.py --profile 859648353 --url "https://www.tiktok.com/search?q=%23plaidskirt"
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
        page.set_viewport_size({"width": 1280, "height": 900})

        page.goto(args.url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(8)
        page.screenshot(path="C:/Users/User/dolphin_anty/_tt_search.png")

        links = page.eval_on_selector_all(
            'a[href*="/video/"]',
            "els => els.map(e => e.getAttribute('href'))",
        )
        seen = []
        for l in links:
            f = l.split("?")[0]
            if f not in seen:
                seen.append(f)
        print("unique video links found:", len(seen), seen[:10])

        title = page.title()
        print("page title:", title)

        browser.close()


if __name__ == "__main__":
    main()
