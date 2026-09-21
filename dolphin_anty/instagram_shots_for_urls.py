"""
Скрины конкретных постов Instagram по списку URL (без пересканирования хэштега).
python instagram_shots_for_urls.py --profile 859648353 --out-dir "C:/Users/User/Desktop/trend_plaidskirt_reels"
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright
from PIL import Image

URLS = [
    "https://www.instagram.com/p/CL3FYksH3PV/",
    "https://www.instagram.com/p/BpCJDG-gaPZ/",
    "https://www.instagram.com/p/DBl7VlNi-nA/",
    "https://www.instagram.com/p/BbjppOrhH4Z/",
    "https://www.instagram.com/p/DcwMAc9DfSF/",
    "https://www.instagram.com/p/BrJmvyjla7P/",
    "https://www.instagram.com/p/DOYPzTjgNSX/",
    "https://www.instagram.com/p/DcVWK12ijZw/",
    "https://www.instagram.com/p/B6gCA-shahk/",
    "https://www.instagram.com/p/DSPxdUEiAdE/",
    "https://www.instagram.com/p/BdBNNZylaiC/",
    "https://www.instagram.com/p/DQzaTn-gYZ5/",
    "https://www.instagram.com/p/DFCooqdN4QD/",
    "https://www.instagram.com/p/DXPl-80jDil/",
    "https://www.instagram.com/p/DYbAIkRDJeY/",
    "https://www.instagram.com/p/By-j9rCgbbv/",
    "https://www.instagram.com/p/CpiEc80OH_g/",
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", type=int, required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    shots_dir = out_dir / "shots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    api = DolphinLocal(port=DolphinLocal.discover())
    data = start_with_retry(api, args.profile)
    auto = data["automation"]
    ws = f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}"

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws)
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.set_viewport_size({"width": 1120, "height": 860})

        for i, link in enumerate(URLS, 1):
            code = link.rstrip("/").rsplit("/", 1)[-1]
            try:
                page.goto(link, wait_until="domcontentloaded", timeout=30000)
                time.sleep(4)
                shot_path = shots_dir / f"{code}.png"
                page.screenshot(path=str(shot_path))
                thumb_path = shots_dir / f"{code}.jpg"
                with Image.open(shot_path) as im:
                    im = im.convert("RGB")
                    w, h = im.size
                    new_w = 640
                    new_h = int(h * (new_w / w))
                    im = im.resize((new_w, new_h), Image.LANCZOS)
                    im.save(thumb_path, "JPEG", quality=82)
                shot_path.unlink()
                print(f"[{i}/{len(URLS)}] ok {code}")
            except Exception as e:
                print(f"[{i}/{len(URLS)}] ошибка {code}: {e}")
            time.sleep(1)

        browser.close()


if __name__ == "__main__":
    main()
