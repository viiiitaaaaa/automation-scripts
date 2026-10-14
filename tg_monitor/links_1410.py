# 14.10: все ссылки из полезных постов и веток чатов одного разбора → study_1410\links.json
# Ссылки берём из текста поста, из страницы t.me/<канал>/<id>?embed=1 (там ссылки под словом «тут») и из сообщений веток чатов.
import json, re, sqlite3, glob, os, sys, concurrent.futures as cf
import requests
from bs4 import BeautifulSoup

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "study_1410"); os.makedirs(OUT, exist_ok=True)
SRC = sys.argv[1:]  # папки с out_*.json разбора
URL = re.compile(r"https?://[^\s\)\]>\"'«»]+")
SKIP = re.compile(r"(t\.me/(?!s/)[^/]+/?$|t\.me/\+|t\.me/addlist|t\.me/joinchat|telegram\.me|cdn\d*\.telesco\.pe|telesco\.pe|"
                  r"youtube\.com/@|instagram\.com|vk\.com/(?!.*\bad)|wildberries|aliexpress|ozon\.ru|tgstat)", re.I)

notes = json.load(open(os.path.join(BASE, "notes.json"), encoding="utf-8"))
keys = []
for d in SRC:
    for f in glob.glob(os.path.join(d, "out_*.json")):
        keys += [k for k, v in json.load(open(f, encoding="utf-8")).items() if v.get("cat") not in (None, "skip")]
db = sqlite3.connect(os.path.join(BASE, "tg_monitor.db"))

def clean(u):
    return u.rstrip(".,;:!?)…")

def embed_links(key):
    ch, pid = key.rsplit("/", 1)
    if ch.startswith("c/"): return []
    try:
        r = requests.get(f"https://t.me/{ch}/{pid}?embed=1", timeout=15)
        soup = BeautifulSoup(r.text, "lxml")
        box = soup.select_one(".tgme_widget_message_text")
        return [a.get("href") for a in box.select("a[href]")] if box else []
    except Exception as e:
        return []

items = {}
def add(u, key):
    u = clean(u)
    if not u.startswith("http") or SKIP.search(u): return
    items.setdefault(u, set()).add(key)

post_keys = [k for k in keys if not notes.get(k, {}).get("cat") == "chat"]
chat_keys = [k for k in keys if notes.get(k, {}).get("cat") == "chat"]
for k in post_keys:
    ch, pid = k.rsplit("/", 1)
    row = db.execute("select text from posts where channel=? and post_id=?", (ch, int(pid))).fetchone()
    for u in URL.findall((row or [""])[0] or ""): add(u, k)
with cf.ThreadPoolExecutor(6) as ex:
    for k, links in zip(post_keys, ex.map(embed_links, post_keys)):
        for u in links: add(u, k)
for k in chat_keys:
    ch, root = k.rsplit("/", 1)
    ids = [int(root)] + [int(x) for x in notes[k].get("replies", []) + notes[k].get("extra_roots", [])]
    for i in ids:
        row = db.execute("select text from chat_msgs where chat=? and msg_id=?", (ch, i)).fetchone()
        for u in URL.findall((row or [""])[0] or ""): add(u, k)
res = [{"link": u, "posts": sorted(v), "for_us": [notes.get(p, {}).get("for_us", "") for p in sorted(v)][:2]} for u, v in items.items()]
json.dump(res, open(os.path.join(OUT, "links.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("постов", len(post_keys), "веток", len(chat_keys), "ссылок", len(res))
