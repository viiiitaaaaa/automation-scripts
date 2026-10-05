"""
Мониторинг публичных Telegram-каналов через веб-версию t.me/s/<channel>.
Не требует api_id/api_hash и входа в аккаунт.

Каждый запуск:
  - проходит по каналам из channels.txt
  - забирает последние посты со страницы t.me/s/<channel>
  - новые посты (которых ещё нет в базе) сохраняет в SQLite (tg_monitor.db)
  - фото и видео из новых постов скачивает в media/<channel>/

Запускать раз в час через Планировщик заданий Windows (см. инструкцию ниже).
"""

import os
import re
import sqlite3
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tg_monitor.db")
MEDIA_DIR = os.path.join(BASE_DIR, "media")
CHANNELS_FILE = os.path.join(BASE_DIR, "channels.txt")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 20
REQUEST_DELAY = 2  # пауза между запросами, чтобы не долбить сайт часто
HIDDEN = "[Telegram не показывает этот пост на сайте — открыть в приложении]"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            channel TEXT NOT NULL,
            post_id INTEGER NOT NULL,
            post_date TEXT,
            text TEXT,
            photos TEXT,
            videos TEXT,
            scraped_at TEXT,
            PRIMARY KEY (channel, post_id)
        )
        """
    )
    conn.commit()
    return conn


def load_channels():
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def fetch_page(channel, before=None):
    url = f"https://t.me/s/{channel}"
    params = {"before": before} if before else {}
    resp = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.text


def extract_bg_url(style):
    if not style:
        return None
    m = re.search(r"background-image:url\(['\"]?(.*?)['\"]?\)", style)
    return m.group(1) if m else None


def parse_posts(html):
    soup = BeautifulSoup(html, "lxml")
    posts = []
    for wrap in soup.select("div.tgme_widget_message"):
        data_post = wrap.get("data-post")
        if not data_post or "/" not in data_post:
            continue
        post_id = int(data_post.split("/")[-1])

        time_tag = wrap.select_one("time.time")
        post_date = time_tag.get("datetime") if time_tag else None

        text_tag = wrap.select_one("div.tgme_widget_message_text")
        text = text_tag.get_text("\n").strip() if text_tag else ""
        if not text and wrap.select_one(".message_media_not_supported"):
            text = HIDDEN  # Telegram shows "Please open Telegram to view this post" instead of the content

        photos = []
        for photo_wrap in wrap.select(".tgme_widget_message_photo_wrap"):
            url = extract_bg_url(photo_wrap.get("style"))
            if url:
                photos.append(url)

        videos = []
        for video_tag in wrap.select("video.tgme_widget_message_video"):
            src = video_tag.get("src")
            if src:
                videos.append(src)

        posts.append(
            {
                "post_id": post_id,
                "post_date": post_date,
                "text": text,
                "photos": photos,
                "videos": videos,
            }
        )
    return posts


def download_file(url, dest_path):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        with open(dest_path, "wb") as f:
            f.write(resp.content)
        return True
    except requests.RequestException as e:
        print(f"    ! не удалось скачать {url}: {e}")
        return False


def save_media(channel, post_id, photos, videos):
    channel_dir = os.path.join(MEDIA_DIR, channel)
    os.makedirs(channel_dir, exist_ok=True)

    for i, url in enumerate(photos, start=1):
        ext = ".jpg"
        dest = os.path.join(channel_dir, f"{post_id}_photo{i}{ext}")
        if not os.path.exists(dest):
            download_file(url, dest)

    # 05.10: videos are not downloaded (her «давай пропустим видео») — the panel never shows them, links stay in the db
    for i, url in enumerate(videos if os.environ.get("TG_VIDEOS") else [], start=1):
        ext = ".mp4"
        dest = os.path.join(channel_dir, f"{post_id}_video{i}{ext}")
        if not os.path.exists(dest):
            download_file(url, dest)


def process_channel(conn, channel):
    print(f"[{channel}] проверка...")
    try:
        html = fetch_page(channel)
    except requests.RequestException as e:
        print(f"  ! ошибка загрузки страницы: {e}")
        return

    posts = parse_posts(html)
    if not posts:
        print("  постов не найдено (канал закрыт, не существует, либо изменилась вёрстка)")
        return

    existing_ids = {
        row[0]
        for row in conn.execute(
            "SELECT post_id FROM posts WHERE channel = ?", (channel,)
        )
    }

    new_posts = [p for p in posts if p["post_id"] not in existing_ids]
    if not new_posts:
        print("  новых постов нет")
        return

    now = datetime.now(timezone.utc).isoformat()
    for post in new_posts:
        conn.execute(
            """
            INSERT OR IGNORE INTO posts
                (channel, post_id, post_date, text, photos, videos, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                channel,
                post["post_id"],
                post["post_date"],
                post["text"],
                "\n".join(post["photos"]),
                "\n".join(post["videos"]),
                now,
            ),
        )
        save_media(channel, post["post_id"], post["photos"], post["videos"])

    conn.commit()
    print(f"  новых постов: {len(new_posts)}")


def main():
    os.makedirs(MEDIA_DIR, exist_ok=True)
    conn = init_db()
    channels = load_channels()

    for channel in channels:
        process_channel(conn, channel)
        time.sleep(REQUEST_DELAY)

    conn.close()


if __name__ == "__main__":
    main()
