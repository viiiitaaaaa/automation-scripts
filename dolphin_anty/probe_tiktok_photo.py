"""
Разведка: страница TikTok Photo Mode search по хэштегу.
python probe_tiktok_photo.py --profile 859648353 --hashtag plaidskirt
"""
from __future__ import annotations

import argparse
import re
import time

from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

CARD_JS = """
els => els.map(e => {
    const card = e.closest('div[class*="DivItemContainer"]') || e.closest('div[data-e2e]') || e.parentElement.parentElement.parentElement;
    const text = card ? card.innerText : '';
    return {href: e.getAttribute('href'), text: text};
})
"""


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

        url = f"https://www.tiktok.com/search/photo?q=%23{args.hashtag}"
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(10)
        page.screenshot(path="C:/Users/User/dolphin_anty/_tt_photo.png")

        all_hrefs = page.eval_on_selector_all(
            "a", "els => els.map(e => e.getAttribute('href')).filter(h=>h)"
        )
        print("all hrefs sample:", all_hrefs[:25])

        links = page.eval_on_selector_all('a[href*="/photo/"]', CARD_JS)
        seen = set()
        uniq = []
        for it in links:
            h = (it["href"] or "").split("?")[0]
            if h and h not in seen:
                seen.add(h)
                uniq.append(it)
        print("unique items found:", len(uniq))
        for it in uniq[:12]:
            safe = it["text"].encode("ascii", "backslashreplace").decode("ascii")
            print("---", it["href"], repr(safe[:150]))

        browser.close()


if __name__ == "__main__":
    main()
