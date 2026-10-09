"""Хук «большие файлы не читать целиком» — по схеме Spotify Portal (engineering.atspotify.com, 09.2026;
vibecoding_tg/3819, пост 538). НЕ установлен: ставить только по её слову через скилл update-config.

Что делает: Claude Code перед каждым вызовом инструмента Read передаёт хуку JSON. Если файл длиннее
порога (по умолчанию 350 строк, переменная SHUNT_MIN_LINES) и чтение идёт целиком (без offset/limit),
хук блокирует чтение (код выхода 2, причина в stderr — её видит Claude) и подсказывает: прочитать
нужный кусок через offset/limit или отдать файл субагенту Explore, который вернёт короткую выжимку.
Чтение кусками проходит. У Spotify так экономилось ~90% токенов на чтении больших файлов;
минус — задержка, и рассуждение дешёвой модели доверять нельзя (она пропустила баг, Claude нашёл).

Как подключить (settings.json → hooks):
  "PreToolUse": [{"matcher": "Read", "hooks": [{"type": "command",
     "command": "python C:\\\\Users\\\\User\\\\.claude\\\\skills\\\\knowledge-library\\\\scripts\\\\big_read_guard.py"}]}]

Самопроверка: python big_read_guard.py --test
"""
import json
import os
import sys

LIMIT = int(os.environ.get("SHUNT_MIN_LINES", "350"))
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".ipynb"}  # картинки/PDF Read читает иначе


def count_lines(path, stop):
    n = 0
    with open(path, "rb") as f:
        for _ in f:
            n += 1
            if n > stop:
                break
    return n


def decide(event):
    """Вернуть (код, сообщение): 0 — пропустить, 2 — заблокировать."""
    if event.get("tool_name") != "Read":
        return 0, ""
    ti = event.get("tool_input") or {}
    path = ti.get("file_path") or ""
    if ti.get("offset") or ti.get("limit") or not path:
        return 0, ""
    if os.path.splitext(path)[1].lower() in SKIP_EXT or not os.path.isfile(path):
        return 0, ""
    n = count_lines(path, LIMIT)
    if n <= LIMIT:
        return 0, ""
    return 2, (f"Файл {path} длиннее {LIMIT} строк — целиком не читаем (экономия лимита). "
               f"Либо Grep по нужному слову и Read с offset/limit, либо отдай файл субагенту Explore "
               f"с вопросом и попроси короткую выжимку.")


def _selftest():
    import tempfile
    d = tempfile.mkdtemp()
    small, big = os.path.join(d, "small.py"), os.path.join(d, "big.py")
    open(small, "w").write("x\n" * 10)
    open(big, "w").write("x\n" * 1000)
    cases = [
        ("маленький файл целиком — пропуск", {"tool_name": "Read", "tool_input": {"file_path": small}}, 0),
        ("большой файл целиком — блок", {"tool_name": "Read", "tool_input": {"file_path": big}}, 2),
        ("большой файл кусками — пропуск", {"tool_name": "Read", "tool_input": {"file_path": big, "offset": 1, "limit": 100}}, 0),
        ("другой инструмент — пропуск", {"tool_name": "Bash", "tool_input": {"command": "ls"}}, 0),
        ("нет файла — пропуск", {"tool_name": "Read", "tool_input": {"file_path": os.path.join(d, "nope.txt")}}, 0),
    ]
    ok = True
    for name, ev, want in cases:
        got = decide(ev)[0]
        print(("ОК   " if got == want else "СБОЙ ") + name)
        ok &= got == want
    return 0 if ok else 1


def main():
    if "--test" in sys.argv:
        return _selftest()
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0  # не мешать работе, если пришло что-то непонятное
    code, msg = decide(event)
    if msg:
        print(msg, file=sys.stderr)
    return code


if __name__ == "__main__":
    sys.exit(main())
