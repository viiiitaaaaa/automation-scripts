"""Сбор новостей в облаке Claude Code (17.10.2026, её «давай попробуем с новостей»).

Базы tg_monitor.db в облаке нет (она только на ПК), поэтому сбор идёт «с закладки»:
cloud/bookmarks.json = последний известный номер поста каждого канала (его пишет cloud_import.py на ПК).
Итог: cloud/posts_<время>.json — новые посты. Картинки и видео не качаем, ключей не нужно.
Закрытые каналы c/… через t.me/s не читаются — их по-прежнему дочитывает ПК (Telegram Web).
"""
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

import tg_monitor as tm

BASE = Path(__file__).resolve().parent
CLOUD = BASE / "cloud"
BOOKMARKS = CLOUD / "bookmarks.json"
MAX_PAGES = 5        # ~100 постов на канал за раз; больше — значит, давно не собирали, догонит ПК
NEW_CHANNEL_DAYS = 3  # канал без закладки — берём только свежие дни


def main():
    try:  # 17.10: в облаке t.me был закрыт сетью — сборщик 12 минут повторял запросы по всем каналам
        requests.get("https://t.me/s/telegram", headers=tm.HEADERS, timeout=15).raise_for_status()
    except requests.RequestException as e:
        sys.exit(f"t.me не открывается — проверить доступ к сети в настройках облачной среды ({e})")
    marks =json.loads(BOOKMARKS.read_text(encoding="utf-8")) if BOOKMARKS.exists() else {}
    horizon = datetime.now(timezone.utc) - timedelta(days=NEW_CHANNEL_DAYS)
    chans = [c for c in tm.load_channels() if not c.startswith("c/")]
    out, unread = [], []
    for idx, ch in enumerate(chans, 1):
        last = marks.get(ch, 0)
        before, new, pages = None, [], 0
        while pages < MAX_PAGES:
            try:
                posts = tm.parse_posts(tm.fetch_page(ch, before))
            except requests.RequestException as e:
                print(f"  [{ch}] ошибка загрузки: {e}")
                if not pages:
                    unread.append(ch)
                break
            pages += 1
            if not posts:
                break
            fresh = [p for p in posts if p["post_id"] > last]
            if not last:  # новый канал: только последние дни
                fresh = [p for p in fresh if p["post_date"] and datetime.fromisoformat(p["post_date"]) > horizon]
            new += fresh
            if len(fresh) < len(posts):
                break  # дошли до закладки
            before = min(p["post_id"] for p in posts)
            time.sleep(tm.REQUEST_DELAY)
        for p in new:
            p.pop("videos", None)
            out.append({"channel": ch, **p})
        print(f"  {idx} из {len(chans)} [{ch}] новых: {len(new)}")
        time.sleep(tm.REQUEST_DELAY)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    CLOUD.mkdir(exist_ok=True)
    path = CLOUD / f"posts_{stamp}.json"
    path.write_text(json.dumps({"collected_at": datetime.now(timezone.utc).isoformat(), "unread": unread,
                                "posts": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ИТОГ: новых постов {len(out)}, файл {path.name}")
    if unread:
        print(f"НЕ ПРОЧИТАНЫ ({len(unread)}): {', '.join(unread)}")
    if len(unread) == len(chans):
        sys.exit("t.me не открывается — проверить доступ к сети в настройках облачной среды")


if __name__ == "__main__":
    main()
