"""Приёмник постов из Telegram Web (tg_web_reader.js) -> tg_monitor.db.

python tg_web_import.py --serve      ждёт один POST на http://127.0.0.1:8765/import и выходит
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


def plan():
    conn = sqlite3.connect(DB)
    out = [[ch, mid] for ch, mid in conn.execute(
        "SELECT channel, min(post_id) FROM posts WHERE text=? GROUP BY channel", (tm.HIDDEN,))]
    readable = {r[0] for r in conn.execute("SELECT DISTINCT channel FROM posts")}
    for ch in tm.load_channels():
        if ch not in readable:
            last = conn.execute("SELECT max(post_id) FROM posts WHERE channel=?", (ch,)).fetchone()[0]
            out.append([ch, (last or 0) + 1])
    # closed channels that already got posts through Telegram Web: continue after the last one
    for ch in ("anita_bold", "moda_po_sprosu"):
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
        msg = save(json.loads(body.decode("utf-8")))
        print(msg, flush=True)
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(msg.encode("utf-8"))
        self.server.done = True


if __name__ == "__main__":
    if "--plan" in sys.argv:
        plan()
    else:
        srv = HTTPServer(("127.0.0.1", PORT), Handler)
        srv.done = False
        srv.timeout = 600
        print(f"Жду посты из Telegram Web на {PORT}...", flush=True)
        while not srv.done:
            srv.handle_request()
