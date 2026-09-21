"""
Разведка №2: фильтр в /reels/ и поиск через строку поиска (не URL).
python probe_reels_search2.py --profile 859648353 --hashtag plaidskirt
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

        # 1) /reels/ + клик по фильтру
        page.goto("https://www.instagram.com/reels/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)
        filt = page.query_selector('svg[aria-label="Filter"]')
        if filt:
            filt.click()
            time.sleep(2)
            page.screenshot(path="C:/Users/User/dolphin_anty/_reels_filter.png")
            print("[1] filter opened, screenshot saved")
        else:
            print("[1] filter svg not found, trying generic click at bottom-right")

        # 2) Поиск через строку поиска (клик по иконке search, ввод текста)
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(3)
        search_icon = page.query_selector('svg[aria-label="Search"]')
        if search_icon:
            search_icon.click()
            time.sleep(1.5)
            inp = page.query_selector('input[placeholder="Search"]') or page.query_selector('input[aria-label="Search input"]')
            if inp:
                inp.type("#" + args.hashtag, delay=80)
                time.sleep(2.5)
                page.screenshot(path="C:/Users/User/dolphin_anty/_search_typed.png")
                print("[2] search typed, screenshot saved")
            else:
                print("[2] search input not found")
                page.screenshot(path="C:/Users/User/dolphin_anty/_search_noinput.png")
        else:
            print("[2] search icon not found")

        browser.close()


if __name__ == "__main__":
    main()
