#!/usr/bin/env python3
"""
Извлечение данных из виртуальной таблицы Ant Design в CSV.
Читает текст ячеек из DOM — без распознавания картинок, без ошибок.

Chrome с --remote-debugging-port=9222 открыт на странице с таблицей.

    python wb_table_data.py prices.csv
    python wb_table_data.py prices.csv --pause 1.5
"""

import argparse
import csv
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

HOLDER = "div.ant-table-tbody-virtual-holder"

JS_HEADERS = """
const ths = document.querySelectorAll(
    '.ant-table-header th, .ant-table-thead th');
return Array.from(ths).map(th => th.innerText.trim().replace(/\\s+/g, ' '));
"""

JS_PREP = """
const el = document.querySelector(arguments[0]);
if (!el) return {found: false};
el.scrollTop = 0;
window.scrollTo(0, 0);
return {found: true, client: el.clientHeight, scroll: el.scrollHeight};
"""

JS_SCROLL = """
const el = document.querySelector(arguments[0]);
el.scrollTop = arguments[1];
return {top: el.scrollTop, max: el.scrollHeight - el.clientHeight,
        scroll: el.scrollHeight};
"""

# Собираем видимые строки. Ключ строки — data-row-key, он уникален
# и не меняется при перерисовке, поэтому дубли отсеиваются надёжно.
JS_ROWS = """
const holder = document.querySelector(arguments[0]);
const rows = holder.querySelectorAll('[data-row-key], .ant-table-row');
const out = [];
rows.forEach(tr => {
    const key = tr.getAttribute('data-row-key') || tr.innerText.slice(0, 60);
    const cells = Array.from(tr.querySelectorAll('td, .ant-table-cell'))
        .map(td => td.innerText.replace(/\\u00a0/g, ' ')
                              .replace(/\\s*\\n\\s*/g, ' | ')
                              .trim());
    // ссылки на товар полезны отдельно
    const link = tr.querySelector('a[href]');
    out.push({key: key, cells: cells, href: link ? link.href : ''});
});
return out;
"""


def attach(port):
    o = Options()
    o.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    return webdriver.Chrome(options=o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output", nargs="?", default="table.csv")
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--selector", default=HOLDER)
    ap.add_argument("--pause", type=float, default=1.0)
    ap.add_argument("--step", type=int, default=400,
                    help="шаг прокрутки, px — мельче шаг, надёжнее сбор")
    ap.add_argument("--max", type=int, default=500)
    args = ap.parse_args()

    d = attach(args.port)
    print(f"Страница: {d.title}")

    info = d.execute_script(JS_PREP, args.selector)
    if not info["found"]:
        raise SystemExit(f"Элемент {args.selector} не найден")

    headers = d.execute_script(JS_HEADERS)
    print(f"Колонок: {len(headers)}")
    total = int(info["scroll"])

    collected = {}      # key -> row
    order = []          # порядок появления
    pos = 0

    for i in range(args.max):
        st = d.execute_script(JS_SCROLL, args.selector, pos)
        time.sleep(args.pause)

        for row in d.execute_script(JS_ROWS, args.selector):
            k = row["key"]
            if k not in collected:
                collected[k] = row
                order.append(k)

        total = max(total, int(st["scroll"]))
        print(f"  позиция {int(st['top'])} / {total} — собрано {len(order)}")

        if st["top"] >= st["max"] - 1:
            # ещё раз на самом дне, чтобы добрать последние строки
            time.sleep(args.pause)
            for row in d.execute_script(JS_ROWS, args.selector):
                if row["key"] not in collected:
                    collected[row["key"]] = row
                    order.append(row["key"])
            break

        pos = st["top"] + args.step

    if not order:
        raise SystemExit("Строки не найдены — проверьте селектор")

    width = max(len(collected[k]["cells"]) for k in order)
    head = headers if len(headers) >= width else \
        headers + [f"col{i}" for i in range(len(headers), width)]

    with open(args.output, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(head[:width] + ["ссылка"])
        for k in order:
            r = collected[k]
            cells = r["cells"] + [""] * (width - len(r["cells"]))
            w.writerow(cells + [r["href"]])

    print(f"Готово: {args.output} — {len(order)} строк, {width} колонок")
    print("Открывать в Excel: Данные → Из текста/CSV, разделитель «;», UTF-8")


if __name__ == "__main__":
    main()
