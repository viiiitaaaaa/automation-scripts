"""Приёмник постов из Telegram Web (tg_web_reader.js) -> tg_monitor.db.

python tg_web_import.py --serve      ждёт один POST на http://127.0.0.1:8765/import и выходит
python tg_web_import.py --serve --keep  принимает несколько POST подряд (выход — Ctrl+C / 10 мин тишины)
python tg_web_import.py --plan --full  все каналы за всё окно (исчерпывающий сбор) + границы чатов
python tg_web_import.py --plan       печатает список [канал, minId] для tgWebSync: каналы со скрытыми
                                     постами (с самого старого скрытого) и закрытые каналы (0)

Посты, которые сайт t.me/s показал заглушкой (tm.HIDDEN), получают настоящий текст; посты из
закрытых каналов добавляются. Уже нормальные тексты не трогаем.
"""
import json
import sqlite3
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import tg_monitor as tm

DB = Path(__file__).parent / "tg_monitor.db"
PORT = 8765
# group chats read with readChat (the same list as CHATS in news.py). 14.10 she: «чаты тоже нужны» — WB/Ozon seller chats
CHATS = ["shopify_chat", "vibecoding_community", "redmilliard_chat", "sellermpchat", "c/1777935062", "c/1554685217",
         "chat_wildbox", "polagushin_chat", "ChatMaxProWb", "billionwb_chat", "ozon_chat_mp", "chatggecom"]
# hundreds-thousands of messages a day: the first read only for a few days, then incremental by minId
CHAT_DAYS = {"redmilliard_chat": 3, "sellermpchat": 3, "c/1777935062": 7, "ChatMaxProWb": 7, "polagushin_chat": 7,
             "chat_wildbox": 7, "ozon_chat_mp": 7, "c/1554685217": 7, "billionwb_chat": 14}
# discussion groups without @address: Telegram Web finds them through the channel they belong to
CHAT_PARENT = {"c/1777935062": "marketplace_hogwarts", "c/1554685217": "wbsharks"}


def save(posts):
    conn = sqlite3.connect(DB)
    now = datetime.now(timezone.utc).isoformat()
    added = fixed = 0
    for p in posts:
        text = p.get("text") or ""
        row = conn.execute("SELECT text FROM posts WHERE channel=? AND post_id=?", (p["channel"], p["id"])).fetchone()
        if row is None and not text:
            continue  # album parts: the caption sits on the first photo, the rest are empty
        if row is None:
            conn.execute("INSERT INTO posts (channel, post_id, post_date, text, photos, videos, scraped_at) "
                         "VALUES (?,?,?,?,?,?,?)", (p["channel"], p["id"], p["date"], text, "", "", now))
            added += 1
        elif row[0] in ("", None, tm.HIDDEN) and text:
            conn.execute("UPDATE posts SET text=? WHERE channel=? AND post_id=?", (text, p["channel"], p["id"]))
            fixed += 1
    conn.commit()
    return f"новых {added}, дочитано скрытых {fixed}"


def save_chat(msgs):
    """Group chats (shopify_chat): every message + which message it answers -> table chat_msgs."""
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS chat_msgs (chat TEXT, msg_id INTEGER, date TEXT, text TEXT, reply_to INTEGER, "
                 "author TEXT, scraped_at TEXT, PRIMARY KEY (chat, msg_id))")
    now = datetime.now(timezone.utc).isoformat()
    n = 0
    for m in msgs:
        cur = conn.execute("INSERT OR IGNORE INTO chat_msgs VALUES (?,?,?,?,?,?,?)",
                           (m["chat"], m["id"], m["date"], m.get("text") or "", m.get("reply_to"), m.get("author") or "", now))
        n += cur.rowcount
    conn.commit()
    return f"чат: новых сообщений {n}"


def plan():
    conn = sqlite3.connect(DB)
    if "--full" in sys.argv:  # 29.09 «исчерпывающий сбор»: every channel, whole window, hidden posts included
        print(json.dumps([[ch, 0] for ch in tm.load_channels()], ensure_ascii=False))
        chats = {c: conn.execute("SELECT min(msg_id), max(msg_id) FROM chat_msgs WHERE chat=?", (c,)).fetchone()
                 for c in CHATS}
        print("чаты (min, max):", json.dumps(chats))
        print("чаты-план readChat (имя, дней, minId, offsetId, канал-родитель):",
              json.dumps([[c, CHAT_DAYS.get(c, 45), (chats[c][1] or 0) + 1 if chats[c][1] else 0, 0, CHAT_PARENT.get(c, "")]
                          for c in CHATS], ensure_ascii=False))
        return
    out = [[ch, mid] for ch, mid in conn.execute(
        "SELECT channel, min(post_id) FROM posts WHERE text=? GROUP BY channel", (tm.HIDDEN,))]
    readable = {r[0] for r in conn.execute("SELECT DISTINCT channel FROM posts")}
    for ch in tm.load_channels():
        if ch not in readable:
            last = conn.execute("SELECT max(post_id) FROM posts WHERE channel=?", (ch,)).fetchone()[0]
            out.append([ch, (last or 0) + 1])
    # closed channels that already got posts through Telegram Web: continue after the last one
    for ch in ["anita_bold", "moda_po_sprosu"] + [c for c in tm.load_channels() if c.startswith("c/")]:  # 09.10: c/<id> = private
        last = conn.execute("SELECT max(post_id) FROM posts WHERE channel=?", (ch,)).fetchone()[0]
        if last and [ch, last + 1] not in out and ch in tm.load_channels():
            out.append([ch, last + 1])
    print(json.dumps(out, ensure_ascii=False))


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "https://web.telegram.org")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        data = json.loads(body.decode("utf-8"))
        msg = save_chat(data) if self.path.startswith("/chat") else save(data)
        print(msg, flush=True)
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(msg.encode("utf-8"))
        self.server.done = "--keep" not in sys.argv  # --keep: accept several POSTs (channels, then each chat)


if __name__ == "__main__":
    if "--plan" in sys.argv:
        plan()
    else:
        srv = HTTPServer(("127.0.0.1", PORT), Handler)
        srv.done = False
        srv.idle = False
        srv.timeout = 600
        srv.handle_timeout = lambda: setattr(srv, "idle", True)  # 10 min without a POST -> stop
        print(f"Жду посты из Telegram Web на {PORT}...", flush=True)
        while not srv.done and not srv.idle:
            srv.handle_request()
