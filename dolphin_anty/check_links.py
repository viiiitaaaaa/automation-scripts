# -*- coding: utf-8 -*-
"""Отбор товаров AliExpress по ссылкам: рейтинг, число отзывов, цена.

    py -3.13 check_links.py ссылки.txt
    py -3.13 check_links.py ссылки.txt --limit 8      # проверить на нескольких

Условия отбора задаются здесь:
    отзывы есть (больше нуля), рейтинг не ниже 4.7, цена не выше 75 $.

Возобновляемый: результат дописывается в check_results.jsonl после каждой карточки,
повторный запуск пропускает уже проверенные ссылки.
"""
import json, re, sys, time
from pathlib import Path
import requests
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

MIN_RATING = 4.7
MAX_PRICE = 75.0
NEED_REVIEWS = True

OUT = Path("check_results.jsonl")
PROFILE = 828976678


def links_from(path):
    txt = Path(path).read_text(encoding="utf-8", errors="replace")
    urls, seen = [], set()
    for m in re.finditer(r"https?://[^\s\"'<>]+", txt):
        u = m.group(0).rstrip(".,);")
        if "aliexpress." not in u or "/item/" not in u:
            continue
        pid = re.search(r"/item/(\d+)", u)
        if not pid or pid.group(1) in seen:
            continue
        seen.add(pid.group(1))
        urls.append((pid.group(1), u))
    return urls


def cdp_ws():
    try:
        port = json.load(open("cdp.json"))["port"]
        v = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=5).json()
        return v["webSocketDebuggerUrl"]
    except Exception:
        from dolphin import DolphinLocal, start_with_retry
        api = DolphinLocal(port=DolphinLocal.discover() or 3001)
        auto = start_with_retry(api, PROFILE, no_tabs=True)["automation"]
        json.dump({"port": auto["port"]}, open("cdp.json", "w"))
        return f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}"


JS_LD = """() => {
  const out = [];
  for (const s of document.querySelectorAll('script[type="application/ld+json"]')) {
    try {
      let j = JSON.parse(s.textContent);
      if (Array.isArray(j)) j = j[0];
      if (j && j['@type'] === 'Product') out.push(j);
    } catch (e) {}
  }
  return out;
}"""


def grab(pg, url):
    """Одна карточка -> словарь с цифрами. Ошибку возвращаем, а не роняем прогон."""
    pg.goto(url, wait_until="domcontentloaded", timeout=90_000)
    for _ in range(12):                       # блок данных появляется не мгновенно
        lds = pg.evaluate(JS_LD)
        if lds:
            break
        pg.wait_for_timeout(500)
    if not lds:
        html = pg.content()
        if re.search(r"captcha|punish|_____tmd_____", html[:5000], re.I):
            return {"error": "антибот: показана капча"}
        return {"error": "нет блока данных"}
    j = lds[0]
    ar = j.get("aggregateRating") or {}
    of = j.get("offers") or {}
    if isinstance(of, list):
        of = of[0] if of else {}
    def num(v):
        try:
            return float(str(v).replace(",", ""))
        except Exception:
            return None
    return {
        "title": (j.get("name") or "")[:120],
        "rating": num(ar.get("ratingValue")),
        "reviews": int(num(ar.get("reviewCount")) or 0),
        "price": num(of.get("price")),
        "currency": of.get("priceCurrency"),
        "error": None,
    }


def verdict(r):
    if r.get("error"):
        return "не проверен"
    why = []
    if NEED_REVIEWS and not r["reviews"]:
        why.append("нет отзывов")
    if r["rating"] is None or r["rating"] < MIN_RATING:
        why.append(f"рейтинг {r['rating']}")
    if r["price"] is None or r["price"] > MAX_PRICE:
        why.append(f"цена {r['price']} {r.get('currency') or ''}".strip())
    return "берём" if not why else "мимо: " + ", ".join(why)


def main():
    src = sys.argv[1]
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    todo = links_from(src)
    done = {}
    if OUT.exists():
        for ln in OUT.read_text(encoding="utf-8").splitlines():
            try:
                d = json.loads(ln)
                done[d["pid"]] = d
            except Exception:
                pass
    todo = [(p, u) for p, u in todo if p not in done]
    if limit:
        todo = todo[:limit]
    print(f"ссылок к проверке: {len(todo)} (уже проверено раньше: {len(done)})", flush=True)

    ws = cdp_ws()
    with sync_playwright() as pw:
        b = pw.chromium.connect_over_cdp(ws)
        ctx = b.contexts[0] if b.contexts else b.new_context()
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        with OUT.open("a", encoding="utf-8") as f:
            for i, (pid, url) in enumerate(todo, 1):
                try:
                    r = grab(pg, url)
                except Exception as e:
                    r = {"error": f"{type(e).__name__}: {str(e)[:80]}"}
                r.update({"pid": pid, "url": url})
                r["verdict"] = verdict(r)
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
                f.flush()
                print(f"[{i}/{len(todo)}] {r['verdict']:<28} "
                      f"{(r.get('title') or '')[:45]}", flush=True)
                time.sleep(3.5)               # не долбим сайт очередью без пауз
    print("\nготово. результат в", OUT)


if __name__ == "__main__":
    main()
