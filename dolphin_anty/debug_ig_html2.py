import sys
import time

from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

PROFILE_ID = 859648353
URL = sys.argv[1] if len(sys.argv) > 1 else "https://www.instagram.com/p/DGLOHrHOz6f/"

api = DolphinLocal(port=DolphinLocal.discover())
data = start_with_retry(api, PROFILE_ID)
auto = data["automation"]
ws = f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(ws)
    ctx = browser.contexts[0] if browser.contexts else browser.new_context()
    page = ctx.new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)
    try:
        page.wait_for_selector("main article, main", timeout=20000)
    except Exception:
        pass
    time.sleep(4)

    result = page.evaluate("""
    () => {
        const svg = document.querySelector('svg[aria-label="Like"], svg[aria-label="Unlike"]');
        if (!svg) return {found: false};
        const btn = svg.closest('[role="button"]');
        if (!btn) return {found: true, btn: false};
        const parent = btn.parentElement;
        const siblingsInfo = Array.from(parent.children).map(c => ({
            tag: c.tagName, text: c.innerText, cls: c.className.slice(0,40)
        }));
        // also go up one more level
        const grandparent = parent.parentElement;
        const gpSiblingsInfo = grandparent ? Array.from(grandparent.children).map(c => ({
            tag: c.tagName, text: c.innerText.slice(0,60)
        })) : null;
        return {found: true, btn: true, siblingsInfo, gpSiblingsInfo};
    }
    """)
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
    browser.close()
