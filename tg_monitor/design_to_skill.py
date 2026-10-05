"""Пополняет скилл site-design из notes.json: все полезные заметки по дизайну сайтов (tool/soft) → приёмы.md и ссылки.md.
Запуск после каждого разбора новостей: python design_to_skill.py   (её правило 05.10: «по дизайну кушаешь всё, сохраняешь,
пишешь в скиллы; полезные ссылки и сайты — напомнишь по запросу»). Файлы пересобираются целиком, notes.json не меняется."""
import json, os, re, sqlite3, sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.expanduser(r"~\.claude\skills\site-design")
DESIGN_CHANNELS = {"intelligentdesign", "sitodel", "uxlive", "tproger_web"}
URL = re.compile(r"https?://[^\s`)\]>«»\"']+")

notes = json.load(open(os.path.join(HERE, "notes.json"), encoding="utf-8"))
dates = {f"{c}/{i}": d[:10] for c, i, d in sqlite3.connect(os.path.join(HERE, "tg_monitor.db"))
         .execute("SELECT channel, post_id, post_date FROM posts")}
dates.update({f"{c}/{i}": d[:10] for c, i, d in sqlite3.connect(os.path.join(HERE, "tg_monitor.db"))
              .execute("SELECT chat, msg_id, date FROM chat_msgs")})  # ветки чатов с пометкой "design"
items = [(dates.get(k, ""), k, v) for k, v in notes.items()
         if isinstance(v, dict) and v.get("cat") in ("tool", "soft", "biz", "course", "chat")
         and (k.split("/")[0] in DESIGN_CHANNELS or v.get("design"))]
items.sort(reverse=True)

out = ["# Приёмы по дизайну и вёрстке сайтов — из новостей\n",
       "Собирается автоматически (`tg_monitor/design_to_skill.py`) из разобранных постов. ★ — применимо сразу, без звезды — для кругозора.\n"]
links = {}
for d, k, v in items:
    star = "★ " if v["cat"] in ("tool", "biz", "course", "chat") else ""
    out.append(f"\n## {star}{v.get('headline', k)}\n{d} · [пост](https://t.me/{k})\n")
    out += [s + "\n" for s in v.get("summary", [])]
    if v.get("for_us"):
        out.append(f"**Для нашего сайта:** {v['for_us']}\n")
    for u in URL.findall(" ".join(v.get("summary", []) + [v.get("for_us", "")])):
        links.setdefault(u.rstrip(".,;:"), (v.get("headline", k), k, d))
open(os.path.join(SKILL, "приёмы.md"), "w", encoding="utf-8").write("".join(out))
# ссылки, спрятанные под словами (Сайтодел): в тексте базы их нет — берём из страницы поста, кэш не перекачивается
import requests
from bs4 import BeautifulSoup
CACHE = os.path.join(HERE, "design_links_cache.json")
cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
SKIP_HOSTS = ("t.me/", "telegram.org", "telegram.me", "tg://", "telegra.ph/file")
for n, (d, k, v) in enumerate(items, 1):
    if k not in cache:
        try:
            html = requests.get(f"https://t.me/{k}?embed=1&mode=tme", timeout=20, headers={"User-Agent": "Mozilla/5.0"}).text
            body = BeautifulSoup(html, "lxml").select_one(".tgme_widget_message_text")
            cache[k] = sorted({a["href"] for a in (body.select("a[href]") if body else []) if a["href"].startswith("http")})
        except Exception as e:
            print("не скачан", k, e); continue
        if n % 10 == 0: print(f"  ссылки из постов: {n} из {len(items)}")
    for u in cache.get(k, []):
        if not any(h in u for h in SKIP_HOSTS):
            links.setdefault(u.rstrip(".,;:"), (v.get("headline", k), k, d))
json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


manual = os.path.join(SKILL, "ссылки_ручные.md")  # что добавлено руками — не перезаписывается
lk = ["# Полезные ссылки и сайты по дизайну сайтов\n",
      "Напоминать ей по запросу («какие были ссылки/сайты по дизайну», «чем сделать …»). Автосписок из новостей; "
      "добавленное вручную — в `ссылки_ручные.md`.\n\n| Ссылка | Что это | Дата | Пост |\n|---|---|---|---|\n"]
lk += [f"| {u} | {h} | {d} | [пост](https://t.me/{k}) |\n" for u, (h, k, d) in sorted(links.items(), key=lambda x: x[1][2], reverse=True)]
open(os.path.join(SKILL, "ссылки.md"), "w", encoding="utf-8").write("".join(lk))
if not os.path.exists(manual):
    open(manual, "w", encoding="utf-8").write("# Ссылки, добавленные вручную\n\n| Ссылка | Что это | Когда и откуда |\n|---|---|---|\n")
print(f"site-design: приёмов {len(items)}, ссылок {len(links)}")
