"""Приём новостей из облака на ПК (17.10.2026). Запускать перед «новости»: python cloud_import.py

1. git fetch — забрать ветку claude/news, которую пишет облачный распорядок «Новости».
2. posts_*.json → tg_monitor.db (INSERT OR IGNORE), notes_*.json → notes.json (только новые ключи, копия до правки).
3. Обновить cloud/bookmarks.json по базе и копию правил разбора (.claude/skills) → commit + push в main,
   чтобы следующий облачный сбор начал с правильного места.
Принятые файлы помнит cloud/imported.json (только на ПК, в git не идёт).
"""
import json
import shutil
import sqlite3
import subprocess
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent
CLOUD = BASE / "cloud"
DONE = CLOUD / "imported.json"
NOTES = BASE / "notes.json"
BRANCH = "origin/claude/news"
SKILLS = Path.home() / ".claude" / "skills"
SKILL_COPIES = {"tg-news": ["SKILL.md"], "noted-news": ["SKILL.md"]}  # правила разбора — облако своих скиллов не видит


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=BASE, capture_output=True, text=True, encoding="utf-8", check=check).stdout


def from_branch():
    if subprocess.run(["git", "fetch", "origin", "claude/news"], cwd=BASE, capture_output=True).returncode:
        print("ветки claude/news пока нет — облако ещё не собирало")
        return [], []
    names = git("ls-tree", "--name-only", BRANCH, "cloud/").split()
    load = lambda n: json.loads(git("show", f"{BRANCH}:{n}"))
    posts = [n for n in names if Path(n).name.startswith("posts_")]
    notes = [n for n in names if Path(n).name.startswith("notes_")]
    return [(n, load(n)) for n in posts], [(n, load(n)) for n in notes]


def main():
    CLOUD.mkdir(exist_ok=True)
    done = set(json.loads(DONE.read_text(encoding="utf-8"))) if DONE.exists() else set()
    posts, notes = from_branch()
    conn = sqlite3.connect(BASE / "tg_monitor.db")
    n_posts = 0
    for name, data in posts:
        if name in done:
            continue
        for p in data["posts"]:
            cur = conn.execute("INSERT OR IGNORE INTO posts (channel, post_id, post_date, text, photos, videos, scraped_at) "
                               "VALUES (?,?,?,?,?,?,?)", (p["channel"], p["post_id"], p["post_date"], p["text"],
                                                          "\n".join(p.get("photos", [])), "", data["collected_at"]))
            n_posts += cur.rowcount
        if data.get("unread"):
            print(f"  облако не прочитало: {', '.join(data['unread'])}")
        done.add(name)
    conn.commit()
    new_notes = {}
    for name, data in notes:
        if name not in done:
            new_notes.update(data)
            done.add(name)
    if new_notes:
        cur = json.loads(NOTES.read_text(encoding="utf-8"))
        shutil.copy(NOTES, BASE / f"notes.backup_{datetime.now():%Y%m%d_%H%M}_cloud.json")
        added = 0
        for k, v in new_notes.items():
            if k not in cur:
                cur[k] = v
                added += 1
        NOTES.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  заметок из облака добавлено: {added}")
    DONE.write_text(json.dumps(sorted(done), ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ИТОГ: постов из облака в базу {n_posts}")

    marks = {ch: mx for ch, mx in conn.execute("SELECT channel, max(post_id) FROM posts GROUP BY channel")}
    (CLOUD / "bookmarks.json").write_text(json.dumps(marks, ensure_ascii=False, indent=1), encoding="utf-8")
    for skill, files in SKILL_COPIES.items():
        dst = BASE / ".claude" / "skills" / skill
        dst.mkdir(parents=True, exist_ok=True)
        for f in files:
            shutil.copy(SKILLS / skill / f, dst / f)
    git("add", "cloud/bookmarks.json", ".claude/skills", "notes.json")
    if git("status", "--porcelain", "cloud/bookmarks.json", ".claude/skills", "notes.json").strip():
        git("commit", "-m", "Закладки и правила разбора для облачного сбора новостей", "--",
            "cloud/bookmarks.json", ".claude/skills", "notes.json")
        push = subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=BASE, capture_output=True, text=True)
        print("  закладки отправлены в GitHub" if not push.returncode else f"  ! push не прошёл: {push.stderr.strip()}")


if __name__ == "__main__":
    main()
