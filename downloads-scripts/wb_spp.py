#!/usr/bin/env python3
"""
Сбор колонки СПП из таблицы цен WB.
Читает текст из DOM — цифры точные, без распознавания картинок.

Chrome с --remote-debugging-port=9222 открыт на таблице цен.

    python wb_spp.py spp.csv
    python wb_spp.py spp.csv --pause 1.5 --step 300
    python wb_spp.py spp.csv --all-columns     # заодно сохранить все колонки
"""

import argparse
import csv
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

HOLDER = "div.ant-table-tbody-virtual-holder"

JS_PREP = """
const el = document.querySelector(arguments[0]);
if (!el) return {found: false};
el.scrollTop = 0;
window.scrollTo(0, 0);
return {found: true, scroll: el.scrollHeight,
        client: el.clientHeight};
"""

JS_SCROLL = """
const el = document.querySelector(arguments[0]);
el.scrollTop = arguments[1];
return {top: el.scrollTop, max: el.scrollHeight - el.clientHeight,
        scroll: el.scrollHeight};
"""

# Ищем индекс колонки СПП по тексту заголовка
JS_SPP_INDEX = """
const ths = document.querySelectorAll('.ant-table-header th, .ant-table-thead th');
let idx = -1;
Array.from(ths).forEach((th, i) => {
    const t = th.innerText.toUpperCase();
    if (idx === -1 && (t.includes('СПП') || t.includes('SPP'))) idx = i;
});
return {index: idx,
        headers: Array.from(ths).map(th =>
            th.innerText.trim().replace(/\\s+/g, ' '))};
"""

JS_ROWS = """
const holder = document.querySelector(arguments[0]);
const sppIdx = arguments[1];
const rows = holder.querySelectorAll('[data-row-key], .ant-table-row');
const out = [];
rows.forEach(tr => {
    const key = tr.getAttribute('data-row-key') || '';
    const cells = Array.from(tr.querySelectorAll('td, .ant-table-cell'))
        .map(td => td.innerText.replace(/\\u00a0/g, ' ')
                               .replace(/\\s*\\n\\s*/g, '\\n').trim());
    const link = tr.querySelector('a[href]');
    out.push({
        key: key,
        first: cells[0] || '',
        spp: (sppIdx >= 0 && cells[sppIdx] !== undefined) ? cells[sppIdx] : '',
        cells: cells,
        href: link ? link.href : ''
    });
});
return out;
"""


def parse_first_cell(text):
    """Из первой ячейки достаём название, бренд, артикул WB, артикул продавца."""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    name = lines[0] if lines else ""
    wb_id = ""
    seller_sku = ""
    brand = ""

    for line in lines[1:]:
        # строка вида "Smartwatch Straps · Zaomi · 148705541"
        m = re.search(r"\b(\d{6,12})\b", line)
        if m and not wb_id:
            wb_id = m.group(1)
            parts = [p.strip() for p in re.split(r"[·•|]", line) if p.strip()]
            parts = [p for p in parts if p != wb_id]
            if parts:
                brand = parts[-1]
        elif line.startswith("•") or "/" in line:
            if not seller_sku:
                seller_sku = line.lstrip("•").strip()
    return name, brand, wb_id, seller_sku


def parse_spp(text):
    """Из ячейки СПП достаём процент и цену."""
    pct = ""
    price = ""
    m = re.search(r"(\d+[.,]?\d*)\s*%", text)
    if m:
        pct = m.group(1).replace(".", ",")
    m = re.search(r"(\d[\d\s ]*)\s*₽", text)
    if m:
        price = m.group(1).replace(" ", "").replace("\u00a0", "").strip()
    return pct, price


def attach(port):
    o = Options()
    o.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    return webdriver.Chrome(options=o)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output", nargs="?", default="spp.csv")
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--selector", default=HOLDER)
    ap.add_argument("--pause", type=float, default=1.0)
    ap.add_argument("--step", type=int, default=400)
    ap.add_argument("--spp-col", type=int, default=None,
                    help="номер колонки СПП вручную, если не нашлась")
    ap.add_argument("--all-columns", action="store_true")
    ap.add_argument("--max", type=int, default=500)
    args = ap.parse_args()

    d = attach(args.port)
    print(f"Страница: {d.title}")

    info = d.execute_script(JS_PREP, args.selector)
    if not info["found"]:
        raise SystemExit(f"Элемент {args.selector} не найден")

    meta = d.execute_script(JS_SPP_INDEX)
    spp_idx = args.spp_col if args.spp_col is not None else meta["index"]

    print("Заголовки таблицы:")
    for i, h in enumerate(meta["headers"]):
        mark = "  <-- СПП" if i == spp_idx else ""
        print(f"  [{i}] {h[:60]}{mark}")

    if spp_idx < 0:
        print("\nКолонка СПП не опознана по заголовку.")
        print("Посмотрите список выше и укажите номер: --spp-col N")
        print("Собираю все колонки, чтобы вы могли выбрать.\n")

    total = int(info["scroll"])
    collected = {}
    order = []
    pos = 0

    for _ in range(args.max):
        st = d.execute_script(JS_SCROLL, args.selector, pos)
        time.sleep(args.pause)

        for row in d.execute_script(JS_ROWS, args.selector, spp_idx):
            k = row["key"] or row["first"][:60]
            if k and k not in collected:
                collected[k] = row
                order.append(k)

        total = max(total, int(st["scroll"]))
        print(f"  позиция {int(st['top'])} / {total} — собрано {len(order)}")

        if st["top"] >= st["max"] - 1:
            time.sleep(args.pause)
            for row in d.execute_script(JS_ROWS, args.selector, spp_idx):
                k = row["key"] or row["first"][:60]
                if k and k not in collected:
                    collected[k] = row
                    order.append(k)
            break
        pos = st["top"] + args.step

    if not order:
        raise SystemExit("Строки не найдены")

    with open(args.output, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        head = ["Артикул WB", "Артикул продавца", "Бренд", "Название",
                "СПП %", "Цена после СПП", "Ссылка"]
        if args.all_columns or spp_idx < 0:
            width = max(len(collected[k]["cells"]) for k in order)
            head += [f"col{i}" for i in range(width)]
        w.writerow(head)

        empty_spp = 0
        for k in order:
            r = collected[k]
            name, brand, wb_id, sku = parse_first_cell(r["first"])
            pct, price = parse_spp(r["spp"])
            if not pct:
                empty_spp += 1
            row = [wb_id, sku, brand, name, pct, price, r["href"]]
            if args.all_columns or spp_idx < 0:
                cells = r["cells"] + [""] * (width - len(r["cells"]))
                row += [c.replace("\n", " | ") for c in cells]
            w.writerow(row)

    print(f"\nГотово: {args.output} — {len(order)} строк")
    if empty_spp:
        print(f"Внимание: у {empty_spp} строк СПП пустая. "
              f"Проверьте номер колонки (--spp-col) или увеличьте --pause.")
    print("Excel: Данные → Из текста/CSV, разделитель «;», кодировка UTF-8")


if __name__ == "__main__":
    main()
