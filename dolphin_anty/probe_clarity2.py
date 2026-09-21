"""Открыть адрес iframe приложения Clarity верхним уровнем и показать, что он отдаёт."""
import json, sys, time
from pathlib import Path

CDP = Path(__file__).with_name("cdp.json")
SHOTS = Path(r"C:\Users\User\AppData\Local\Temp\claude\C--Users-User"
             r"\fe7d07b8-c28f-4c8f-b6c2-711eddff37f2\scratchpad\shots")
sys.stdout.reconfigure(encoding="utf-8")
cdp = json.loads(CDP.read_text(encoding="utf-8"))

from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(cdp["url"])
    ctx = b.contexts[0]
    host = ctx.pages[0]
    host.bring_to_front()
    time.sleep(8)

    # сначала — что стало со страницей приложения спустя время
    SHOTS.mkdir(parents=True, exist_ok=True)
    host.screenshot(path=str(SHOTS / "clarity-after-wait.png"), timeout=180_000)
    print("SHOT 1:", SHOTS / "clarity-after-wait.png")

    src = host.evaluate("""() => {
        const f = [...document.querySelectorAll('iframe')].filter(x => x.clientWidth > 200)[0];
        return f ? f.src : null;
    }""")
    if not src:
        print("[x] iframe не найден")
        sys.exit(1)
    print("iframe src:", src[:130], "...")

    pg = ctx.new_page()
    resp = pg.goto(src, wait_until="domcontentloaded", timeout=90_000)
    time.sleep(6)
    print("\nверхнеуровневый заход:")
    print("  статус:", resp.status if resp else "?")
    print("  URL   :", pg.url[:130])
    if resp:
        h = resp.headers
        for k in ("server", "x-azure-ref", "x-ms-error-code", "cf-ray", "content-type"):
            if k in h:
                print(f"  {k}: {h[k][:120]}")
    print("\n--- ТЕКСТ ---")
    print(pg.evaluate("() => document.body.innerText")[:800])
    pg.screenshot(path=str(SHOTS / "clarity-toplevel.png"), timeout=180_000)
    print("\nSHOT 2:", SHOTS / "clarity-toplevel.png")
    pg.close()
