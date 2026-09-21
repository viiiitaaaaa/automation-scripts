# -*- coding: utf-8 -*-
"""Разведка: в каком виде на карточке AliExpress лежат рейтинг/отзывы/цена.
Вывод намеренно короткий - только найденные куски, не вся страница."""
import json, sys
from dolphin import DolphinLocal, start_with_retry
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
PROFILE = 828976678
ITEM = sys.argv[1] if len(sys.argv) > 1 else "3256811359728907"

api = DolphinLocal()
auto = start_with_retry(api, PROFILE, no_tabs=True)["automation"]
url = f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}"
json.dump({"url": url, "port": auto["port"]}, open("cdp.json", "w"))
print("[ok] профиль поднят, порт", auto["port"], flush=True)

JS = """
async (item) => {
  const r = await fetch(`https://www.aliexpress.com/item/${item}.html`,
                        {credentials: 'include'});
  const h = await r.text();
  const out = {status: r.status, len: h.length, hits: {}};
  const pats = {
    averageStar:      /"averageStar"\s*:\s*"?([\d.]+)"?/,
    evarageStar:      /"evarageStar"\s*:\s*"?([\d.]+)"?/,
    starRating:       /"starRating"\s*:\s*"?([\d.]+)"?/,
    ratingValue:      /"ratingValue"\s*:\s*"?([\d.]+)"?/,
    totalValidNum:    /"totalValidNum"\s*:\s*"?(\d+)"?/,
    reviewCount:      /"reviewCount"\s*:\s*"?(\d+)"?/,
    tradeCount:       /"tradeCount"\s*:\s*"?([\d,]+)"?/,
    formatTradeCount: /"formatTradeCount"\s*:\s*"([^"]{1,20})"/,
    minPrice:         /"minActivityAmount"\s*:\s*\{[^}]*"value"\s*:\s*([\d.]+)/,
    formatedPrice:    /"formatedActivityPrice"\s*:\s*"([^"]{1,30})"/,
    formatedAmount:   /"formatedAmount"\s*:\s*"([^"]{1,30})"/,
    currency:         /"currency"\s*:\s*"([A-Z]{3})"/,
    subject:          /"subject"\s*:\s*"([^"]{1,60})"/
  };
  for (const [k, re] of Object.entries(pats)) {
    const m = h.match(re);
    if (m) out.hits[k] = m[1];
  }
  out.hasRunParams = h.includes('window.runParams');
  out.blocked = /captcha|punish|_____tmd_____/i.test(h.slice(0, 4000));
  return out;
}
"""

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp(url)
    ctx = b.contexts[0]
    pg = ctx.new_page()
    pg.goto("https://www.aliexpress.com/", wait_until="domcontentloaded", timeout=90_000)
    print("[ok] вкладка AliExpress открыта:", pg.url[:60], flush=True)
    res = pg.evaluate(JS, ITEM)
    print(json.dumps(res, ensure_ascii=False, indent=1))
