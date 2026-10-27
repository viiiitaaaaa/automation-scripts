"""Сборщик сайтов-источников (RSS/Atom) — рядом с Telegram-сборщиком.

Запуск:  python rss_sources.py          -> новое с прошлого раза в rss_novoe.md
         python rss_sources.py --vse    -> показать всё, что в лентах сейчас
Список лент — rss_sources.json. Уже виденное помнит rss_seen.json.
"""
import json, sys, urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "rss_sources.json"
SEEN = HERE / "rss_seen.json"
OUT = HERE / "rss_novoe.md"
UA = {"User-Agent": "Mozilla/5.0"}


def tag(el):
    return el.tag.split("}")[-1]


def read_feed(url):
    xml = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20).read()
    try:
        root = ET.fromstring(xml)
    except ET.ParseError:  # лента с битым XML (бывает у PYMNTS) — берём заголовки и ссылки регуляркой
        import re
        txt = xml.decode("utf-8", "replace")
        out = []
        for blk in re.findall(r"<item>(.*?)</item>", txt, re.S):
            g = lambda n: (re.search(rf"<{n}[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{n}>", blk, re.S) or [0, ""])[1].strip()
            out.append({"title": g("title"), "link": g("link"), "date": g("pubDate")})
        return out
    items = []
    for el in root.iter():
        if tag(el) not in ("item", "entry"):
            continue
        d = {tag(c): (c.text or "").strip() for c in el}
        link = d.get("link", "")
        if not link:  # у Atom ссылка лежит в атрибуте href
            for c in el:
                if tag(c) == "link" and c.get("href"):
                    link = c.get("href")
                    break
        date = d.get("pubDate") or d.get("updated") or d.get("published") or ""
        items.append({"title": d.get("title", ""), "link": link, "date": date})
    return items


def main():
    show_all = "--vse" in sys.argv
    sources = json.loads(SRC.read_text(encoding="utf-8"))
    seen = set(json.loads(SEEN.read_text(encoding="utf-8"))) if SEEN.exists() else set()
    lines, total = [], 0
    manual = [s for s in sources if s.get("manual")]
    sources = [s for s in sources if not s.get("manual")]
    for s in sources:
        try:
            items = read_feed(s["url"])[: s.get("limit", 15)]
        except Exception as e:
            lines.append(f"## {s['name']}\n⚠️ не открылась лента: {e}\n")
            continue
        kw = [k.lower() for k in s.get("filter", [])]
        new = []
        for it in items:
            if it["link"] in seen and not show_all:
                continue
            if kw and not any(k in it["title"].lower() for k in kw):
                seen.add(it["link"])
                continue
            new.append(it)
            seen.add(it["link"])
        if new:
            lines.append(f"## {s['name']} — {s['theme']}")
            lines += [f"- {i['title']} ({i['date'][:16]}) {i['link']}" for i in new]
            lines.append("")
            total += len(new)
    if manual:
        lines.append("## Зайти вручную в Chrome (ленты нет), раз в 1–2 недели")
        lines += [f"- {m['name']} {m['url']} — {m['theme']}. Смотреть: {m['look']}" for m in manual]
    OUT.write_text(f"# Новое на сайтах-источниках: {total}\n\n" + "\n".join(lines), encoding="utf-8")
    if total:  # копия в архив: rss_novoe.md перезаписывается каждым запуском
        arh = HERE / "rss_arhiv"
        arh.mkdir(exist_ok=True)
        import datetime
        (arh / f"{datetime.datetime.now():%Y-%m-%d_%H%M}.md").write_text(OUT.read_text(encoding="utf-8"), encoding="utf-8")
    SEEN.write_text(json.dumps(sorted(seen)), encoding="utf-8")
    print(f"новых: {total} -> {OUT}")


if __name__ == "__main__":
    main()
