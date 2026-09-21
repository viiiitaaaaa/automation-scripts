"""
Узнать автора поста и проверить, есть ли у него рилсы.
python probe_ig_author.py --profile 859648353 --post-url "https://www.instagram.com/p/CL3FYksH3PV/"
"""
from __future__ import annotations

import argparse
import time

from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", type=int, required=True)
    ap.add_argument("--post-url", required=True)
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

        page.goto(args.post_url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)

        author_link = page.query_selector('header a[role="link"]')
        username = None
        if author_link:
            href = author_link.get_attribute("href")
            username = href.strip("/").split("/")[-1] if href else None
        print("author username:", username)

        if username:
            reels_url = f"https://www.instagram.com/{username}/reels/"
            page.goto(reels_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(5)
            page.screenshot(path="C:/Users/User/dolphin_anty/_ig_author_reels.png")
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

            followers = page.query_selector('header')
            if followers:
                txt = followers.inner_text()
                safe = txt.encode("ascii", "backslashreplace").decode("ascii")
                print("header text:", safe[:300])

        browser.close()


if __name__ == "__main__":
    main()
