# 20.10: ссылки всех принятых карточек (noted + skill) → study_links_2010\links_all.json
# Ссылки: из текста поста в базе, со страницы t.me/<канал>/<id>?embed=1 и из сообщений веток чатов.
import json, re, sqlite3, os, concurrent.futures as cf
import requests
from bs4 import BeautifulSoup

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "study_links_2010"); os.makedirs(OUT, exist_ok=True)
SKILLS = {"claude-code-priemy", "trend-radar", "sourcing-1688", "b2b-sbor", "knowledge-library", "kursy-konspekty",
          "dela", "pc-check", "dogovorennosti", "site-design", "dropship-lessons"}
URL = re.compile(r"https?://[^\s\)\]>\"'«»]+")
# пропуск без записи: другие посты t.me, профили соцсетей, маркетплейсы, картинки телеграма
SKIP = re.compile(r"(t\.me/|telegram\.(me|org)|telesco\.pe|youtube\.com/@|youtube\.com/(c|channel|user)/|instagram\.com|"
                  r"vk\.com|vk\.cc|facebook\.com|tiktok\.com/@|(twitter|x)\.com/[^/]+/?$|threads\.net|linkedin\.com/in/|"
                  r"wildberries|aliexpress|ozon\.ru|tgstat|dzen\.ru/(?!a/)|boosty\.to|taplink|linktr\.ee)", re.I)

notes = json.load(open(os.path.join(BASE, "notes.json"), encoding="utf-8"))
cards = {k: v for k, v in notes.items() if v.get("noted") and v.get("skill") in SKILLS}
db = sqlite3.connect(os.path.join(BASE, "tg_monitor.db"), check_same_thread=False)

def clean(u):
    return u.rstrip(".,;:!?)…*_")

def embed_links(key):
    if "/" not in key: return None
    ch, pid = key.rsplit("/", 1)
    if ch.startswith("c/") or not pid.isdigit(): return None
    for _ in range(3):
        try:
            r = requests.get(f"https://t.me/{ch}/{pid}?embed=1", timeout=20)
            soup = BeautifulSoup(r.text, "lxml")
            box = soup.select_one(".tgme_widget_message_text")
            return [a.get("href") for a in box.select("a[href]")] if box else []
        except Exception:
            pass
    return []

items, closed = {}, []
def add(u, key):
    u = clean(u or "")
    if not u.startswith("http") or SKIP.search(u): return
    items.setdefault(u, set()).add(key)

keys = sorted(cards)
emb = {}
with cf.ThreadPoolExecutor(8) as ex:
    for k, links in zip(keys, ex.map(lambda k: embed_links(k) if cards[k].get("cat") != "chat" else None, keys)):
        emb[k] = links
for k in keys:
    v = cards[k]
    if v.get("url"): add(v["url"], k)
    ch, pid = k.rsplit("/", 1) if "/" in k else (k, "")
    if ch.startswith("c/"):
        closed.append(k)
    if v.get("cat") == "chat" and pid.isdigit():
        ids = [int(pid)] + [int(x) for x in v.get("replies", []) + v.get("extra_roots", [])]
        for i in ids:
            row = db.execute("select text from chat_msgs where chat=? and msg_id=?", (ch, i)).fetchone()
            for u in URL.findall((row or [""])[0] or ""): add(u, k)
    elif pid.isdigit():
        row = db.execute("select text from posts where channel=? and post_id=?", (ch, int(pid))).fetchone()
        for u in URL.findall((row or [""])[0] or ""): add(u, k)
        for u in emb.get(k) or []: add(u, k)

res = []
for u, ks in items.items():
    ks = sorted(ks)
    sk = sorted({cards[k]["skill"] for k in ks})
    res.append({"link": u, "posts": ks, "skills": sk,
                "headline": cards[ks[0]].get("headline", ""), "for_us_card": cards[ks[0]].get("for_us", "")})
json.dump(res, open(os.path.join(OUT, "links_all.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(closed, open(os.path.join(OUT, "closed.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("карточек", len(cards), "ссылок", len(res), "закрытых каналов", len(closed))
