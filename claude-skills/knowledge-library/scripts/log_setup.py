"""Один вызов — нормальный лог для наших сборщиков (tg_monitor, радар, 1688, бот «Дела»).

Источник приёма: python2day/8107, пост 299, 25.08.2026 («логирование вместо print»).

Как подключить в своём скрипте (скопировать файл рядом или добавить путь):
    import sys; sys.path.insert(0, r"C:\\Users\\User\\.claude\\skills\\knowledge-library\\scripts")
    from log_setup import get_logger
    log = get_logger("tg_news")                 # -> <папка скрипта>\\logs\\tg_news.log
    log.info("Собрано %s постов из %s каналов", n, k)   # %s, а не f-строка
    try: ...
    except Exception: log.exception("Канал %s упал", ch)  # в лог попадёт traceback

Что делает: в консоль — INFO и выше; в файл — DEBUG и выше, с датой-временем, UTF-8,
файл не растёт бесконечно (5 файлов по 2 МБ). Повторный вызов не дублирует строки.
Ключи/токены в лог не писать: логи читаем вместе с Claude (🟡 только ПК).
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

FMT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def get_logger(name, folder=None, console_level=logging.INFO):
    log = logging.getLogger(name)
    if log.handlers:
        return log
    log.setLevel(logging.DEBUG)
    folder = Path(folder) if folder else Path(sys.argv[0] or ".").resolve().parent / "logs"
    folder.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter(FMT)

    fh = RotatingFileHandler(folder / f"{name}.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(console_level)
    ch.setFormatter(fmt)
    try:  # кириллица в консоли Windows (cp1251) не ломает вывод
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    log.addHandler(fh)
    log.addHandler(ch)
    log.propagate = False
    return log


if __name__ == "__main__":
    import tempfile
    lg = get_logger("selftest", folder=tempfile.mkdtemp())
    lg.debug("только в файл")
    lg.info("проверка: %s", "ок")
    try:
        1 / 0
    except ZeroDivisionError:
        lg.exception("пример ошибки с traceback")
    print("лог:", lg.handlers[0].baseFilename)
