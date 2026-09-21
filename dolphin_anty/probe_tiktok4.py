"""
Разведка: вытащить лайки прямо из сетки поиска TikTok (без захода в видео).
python probe_tiktok4.py --profile 859648353 --hashtag plaidskirt
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

        url = f"https://www.tiktok.com/search?q=%23{args.hashtag}"
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        time.sleep(12)
        page.screenshot(path="C:/Users/User/dolphin_anty/_tt_search2.png")

        # каждый видео-элемент в сетке: контейнер вокруг ссылки на /video/
        items = page.eval_on_selector_all(
            'a[href*="/video/"]',
            """els => els.map(e => {
                const card = e.closest('div[class*="DivItemContainer"]') || e.closest('div[data-e2e]') || e.parentElement.parentElement.parentElement;
                const text = card ? card.innerText : '';
                return {href: e.getAttribute('href'), text: text.slice(0, 200)};
            })"""
        )
        seen = set()
        uniq = []
        for it in items:
            h = it["href"].split("?")[0]
            if h not in seen:
                seen.add(h)
                uniq.append(it)
        for it in uniq[:12]:
            print("---")
            print(it["href"])
            safe = it["text"].encode("ascii", "backslashreplace").decode("ascii")
            print(repr(safe))

        browser.close()


if __name__ == "__main__":
    main()
