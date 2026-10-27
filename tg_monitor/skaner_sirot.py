"""Сканер «сирот и разрывов» данных новостей (23.10.2026, курс learn-harness-engineering, проект P06).

python skaner_sirot.py          # только читает, ничего не меняет; печатает 4 проверки и примеры
Запускать после «новостей» (шаг в tg-news). «Сирота» = запись, у которой потерялась пара.
"""
import json
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
D = Path(__file__).resolve().parent


def show(title, bad, total, sample=5):
    mark = "✅" if not bad else "⚠️"
    print(f"{mark} {title}: {len(bad)} из {total}")
    for x in list(bad)[:sample]:
        print("     ", x)
    return len(bad)


def main():
    nums = json.loads((D / "post_numbers.json").read_text("utf-8"))
    notes = json.loads((D / "notes.json").read_text("utf-8"))
    con = sqlite3.connect(D / "tg_monitor.db")
    posts = {f"{c}/{p}" for c, p in con.execute("select channel, post_id from posts")}
    posts |= {f"{c}/{m}" for c, m in con.execute("select chat, msg_id from chat_msgs")}  # чаты лежат в другой таблице
    fresh = {f"{c}/{p}" for c, p in con.execute("select channel, post_id from posts where post_date >= date('now','-45 day')")}
    bad = 0
    # 1. номер есть, поста в базе нет
    bad += show("номер без поста в базе", [k for k in nums if k not in posts], len(nums))
    # 2. один номер у двух постов
    dup = [f"№{n} ×{c}" for n, c in Counter(nums.values()).items() if c > 1]
    bad += show("номер выдан двум постам", dup, len(set(nums.values())))
    # 3. разметка (notes.json) есть, поста в базе нет
    bad += show("разбор без поста в базе", [k for k in notes if k not in posts and not k.startswith("habr/")], len(notes))
    # 4. принято, но без метки «когда» (потом не поднять через znaniya: событие берётся из when)
    bad += show("принято без метки when", [k for k, v in notes.items() if v.get("noted") and not v.get("when")],
                sum(1 for v in notes.values() if v.get("noted")))
    print(f"\nИтого проблем: {bad}. Ничего не исправлено — решает она.")


if __name__ == "__main__":
    main()
