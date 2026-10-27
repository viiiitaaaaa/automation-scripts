"""Одна кнопка «новости» для всего, что не требует браузера: сайты-источники + журнал (Хабр, Selectel).

Запуск:  python vse_novosti.py
Telegram-каналы идут отдельно (news.py + Telegram Web) — порядок в скилле tg-news.
Итог: rss_novoe.md (сайты) и ..\\zhurnal\\data\\lenta.json (журнал).
"""
import subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent
ZHURNAL = Path.home() / "zhurnal"


def run(title, cmd, cwd):
    print(f"--- {title}")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    print((r.stdout or "").strip()[-600:] or "(пусто)")
    if r.returncode:
        print(f"⚠️ код {r.returncode}: {(r.stderr or '').strip()[-300:]}")


run("сайты-источники", [sys.executable, "rss_sources.py"], HERE)
if (ZHURNAL / "sbor.py").exists():
    run("журнал: Хабр и Selectel", [sys.executable, "sbor.py"], ZHURNAL)
print("--- готово: сайты в rss_novoe.md, журнал в zhurnal\\data\\lenta.json; Telegram — по шагам tg-news")
