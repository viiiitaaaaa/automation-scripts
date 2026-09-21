"""
Разведка: поиск рилс в Instagram через реальный интерфейс поиска (не URL),
с обработкой возможных баннеров/диалогов.
python probe_ig_reels2.py --profile 859648353 --hashtag plaidskirt
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

        page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(4)
        page.screenshot(path="C:/Users/User/dolphin_anty/_ig_home.png")

        # попытка закрыть возможный диалог уведомлений
        for label in ["Not Now", "Not now", "Cancel", "Close"]:
            btn = page.query_selector(f'button:has-text("{label}")')
            if btn:
                btn.click()
                time.sleep(1)
                print("closed dialog:", label)

        search_icon = page.query_selector('svg[aria-label="Search"]')
        print("search icon found:", bool(search_icon))
        if search_icon:
            try:
                search_icon.click(timeout=5000)
            except Exception as e:
                print("click failed, trying JS click:", e)
                page.evaluate("(el) => el.closest('a,div[role=link],div').click()", search_icon)
            time.sleep(2)
            page.screenshot(path="C:/Users/User/dolphin_anty/_ig_after_search_click.png")

            inp = page.query_selector('input[placeholder="Search"]')
            print("input found:", bool(inp))
            if inp:
                inp.focus()
                page.keyboard.type(args.hashtag, delay=100)
                time.sleep(2.5)
                page.screenshot(path="C:/Users/User/dolphin_anty/_ig_typed.png")

                # текст выпадающего списка результатов
                texts = page.eval_on_selector_all(
                    'a, span, div[role="button"]',
                    "els => els.map(e=>e.innerText).filter(t=>t && t.length>0 && t.length<40)"
                )
                uniq = list(dict.fromkeys(texts))
                safe = " | ".join(uniq[:80]).encode("ascii", "backslashreplace").decode("ascii")
                print("dropdown texts:", safe)

        browser.close()


if __name__ == "__main__":
    main()
