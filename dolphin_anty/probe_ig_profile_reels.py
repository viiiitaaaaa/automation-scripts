"""
Разведка: вкладка Reels в профиле конкретного аккаунта Instagram.
python probe_ig_profile_reels.py --profile 859648353 --username plaidskirt_looks
"""
from __future__ import annotations

import argparse
import time

from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", type=int, required=True)
    ap.add_argument("--username", required=True)
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

        url = f"https://www.instagram.com/{args.username}/reels/"
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)
        page.screenshot(path="C:/Users/User/dolphin_anty/_ig_profile_reels.png")

        links = page.eval_on_selector_all(
            'a[href*="/reel/"]',
            "els => els.map(e => e.getAttribute('href'))",
        )
        seen = []
        for l in links:
            f = l.split("?")[0]
            if f not in seen:
                seen.append(f)
        print("reel links found:", len(seen), seen[:15])

        browser.close()


if __name__ == "__main__":
    main()
