#!/usr/bin/env python3
"""
Сбор СПП из таблицы цен WB — v2.

Исправлено:
  * СПП ищется регуляркой по содержимому ячеек (номер колонки не нужен)
  * прокрутка не сдаётся на первом экране: идёт, пока прибавляются строки
  * запасной способ прокрутки колесом мыши, если scrollTop не двигает
  * разбор бренда и артикулов приведён к фактическому виду ячейки

    python wb_spp2.py spp.csv
    python wb_spp2.py spp.csv --pause 1.5 --step 250
    python wb_spp2.py spp.csv --raw       # сохранить и все исходные колонки
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
if (!document.getElementById('__shot_style')) {
    const s = document.createElement('style');
    s.id = '__shot_style';
    s.textContent = `html{scroll-behavior:auto!important;}`;
    document.head.appendChild(s);
}
el.scrollTop = 0;
const r = el.getBoundingClientRect();
return {found: true, scroll: el.scrollHeight, client: el.clientHeight,
        cx: Math.round(r.left + r.width / 2),
        cy: Math.round(Math.max(r.top, 0) +
             (Math.min(r.bottom, window.innerHeight) - Math.max(r.top, 0)) / 2)};
"""

JS_SCROLL = """
const el = document.querySelector(arguments[0]);
const before = el.scrollTop;
el.scrollTop = arguments[1];
el.dispatchEvent(new Event('scroll', {bubbles: true}));
return {before: before, top: el.scrollTop,
        max: el.scrollHeight - el.clientHeight, scroll: el.scrollHeight};
"""

JS_STATE = """
const el = document.querySelector(arguments[0]);
return {top: el.scrollTop, max: el.scrollHeight - el.clientHeight,
        scroll: el.scrollHeight};
"""

JS_ROWS = """
const holder = document.querySelector(arguments[0]);
const rows = holder.querySelectorAll('[data-row-key], .ant-table-row');
const out = [];
rows.forEach(tr => {
    const cells = Array.from(tr.querySelectorAll('td, .ant-table-cell'))
        .map(td => td.innerText.replace(/\\u00a0/g, ' ')
                               .replace(/\\s*\\n\\s*/g, '\\n').trim());
    const link = tr.querySelector('a[href]');
    out.push({
        key: tr.getAttribute('data-row-key') || '',
        cells: cells,
        href: link ? link.href : ''
    });
});
return out;
"""

RE_SPP = re.compile(r"СПП\s*([\d]+[.,]?[\d]*)\s*%", re.I)
RE_MONEY = re.compile(r"([\d][\d\s\u00a0]*[.,]?\d*)\s*₽")
RE_WBID = re.compile(r"\b(\d{6,12})\b")


def money(s):
    return s.replace(" ", "").replace("\u00a0", "").replace(".", ",").strip()


def parse_row(cells):
    """Возвращает словарь с разобранными полями строки."""
    blob = "\n".join(cells)
    first = cells[0] if cells else ""
    lines = [l.strip() for l in first.split("\n") if l.strip()]

    name = lines[0] if lines else ""
    wb_id = ""
    brand = ""
    sku = ""

    for i, line in enumerate(lines[1:], 1):
        m = RE_WBID.fullmatch(line)
        if m and not wb_id:
            wb_id = m.group(1)
            # бренд — предыдущая непустая строка перед артикулом
            if i - 1 >= 1:
                brand = lines[i - 1]
            continue
        # артикул продавца обычно содержит слэш или дефис
        if not wb_id and RE_WBID.search(line):
            wb_id = RE_WBID.search(line).group(1)
            parts = [p.strip() for p in re.split(r"[·•|]", line)
                     if p.strip() and p.strip() != wb_id]
            if parts:
                brand = parts[-1]
            continue
        if ("/" in line or "-" in line) and not sku and line != name:
            sku = line.lstrip("•").strip()

    # СПП и цена после неё
    spp_pct = ""
    spp_price = ""
    spp_cell = ""
    for c in cells:
        m = RE_SPP.search(c)
        if m:
            spp_cell = c
            spp_pct = m.group(1).replace(".", ",")
            after = c[m.end():]
            mp = RE_MONEY.search(after)
            if mp:
                spp_price = money(mp.group(1))
            break

    # цена до скидок — первая денежная ячейка, состоящая только из суммы
    base_price = ""
    seller_disc = ""
    for c in cells[1:]:
        if not base_price and re.fullmatch(r"[\d\s\u00a0]+\s*₽", c):
            base_price = money(RE_MONEY.search(c).group(1))
        elif not seller_disc and re.fullmatch(r"\d+\s*%", c):
            seller_disc = c.replace("%", "").strip()

    # цена после скидки продавца — первое число в ячейке с СПП
    price_after_disc = ""
    if spp_cell:
        mp = RE_MONEY.search(spp_cell)
        if mp:
            price_after_disc = money(mp.group(1))

    return {
        "wb_id": wb_id, "sku": sku, "brand": brand, "name": name,
        "base_price": base_price, "seller_disc": seller_disc,
        "price_after_disc": price_after_disc,
        "spp_pct": spp_pct, "spp_price": spp_price,
    }


def attach(port):
    o = Options()
    o.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    return webdriver.Chrome(options=o)


def wheel(driver, x, y, delta):
    driver.execute_cdp_cmd("Input.dispatchMouseEvent", {
        "type": "mouseWheel", "x": x, "y": y,
        "deltaX": 0, "deltaY": delta, "pointerType": "mouse"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output", nargs="?", default="spp.csv")
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--selector", default=HOLDER)
    ap.add_argument("--pause", type=float, default=1.0)
    ap.add_argument("--step", type=int, default=350)
    ap.add_argument("--raw", action="store_true",
                    help="дописать исходные колонки как есть")
    ap.add_argument("--max", type=int, default=1000)
    args = ap.parse_args()

    d = attach(args.port)
    print(f"Страница: {d.title}")

    info = d.execute_script(JS_PREP, args.selector)
    if not info["found"]:
        raise SystemExit(f"Элемент {args.selector} не найден")

    print(f"Контейнер: содержимое {info['scroll']} px, "
          f"видно {info['client']} px")

    collected = {}
    order = []
    pos = 0
    idle = 0           # сколько шагов подряд без новых строк
    use_wheel = False

    for step_i in range(args.max):
        if use_wheel:
            wheel(d, info["cx"], info["cy"], args.step)
            time.sleep(args.pause)
            st = d.execute_script(JS_STATE, args.selector)
        else:
            st = d.execute_script(JS_SCROLL, args.selector, pos)
            time.sleep(args.pause)
            # scrollTop не сдвинулся, хотя просили — переходим на колесо
            if step_i > 0 and st["top"] == st["before"] and pos > st["before"]:
                if not use_wheel:
                    print("  scrollTop не двигает — переключаюсь на колесо мыши")
                    use_wheel = True
                    continue

        before_count = len(order)
        for row in d.execute_script(JS_ROWS, args.selector):
            k = row["key"] or (row["cells"][0][:80] if row["cells"] else "")
            if k and k not in collected:
                collected[k] = row
                order.append(k)
        added = len(order) - before_count

        print(f"  позиция {int(st['top'])}/{int(st['max'])} — "
              f"всего {len(order)} (+{added})")

        at_bottom = st["top"] >= st["max"] - 1
        if added == 0:
            idle += 1
        else:
            idle = 0

        # Останавливаемся, только если и внизу, и новых строк не появляется
        if at_bottom and idle >= 2:
            print("  конец списка")
            break
        if idle >= 6:
            print("  новых строк нет 6 шагов подряд — останавливаюсь")
            break

        pos = st["top"] + args.step

    if not order:
        raise SystemExit("Строки не найдены")

    head = ["Артикул WB", "Артикул продавца", "Бренд", "Название",
            "Цена до скидки", "Скидка продавца %", "Цена после скидки",
            "СПП %", "Цена после СПП", "Ссылка"]
    width = max(len(collected[k]["cells"]) for k in order)
    if args.raw:
        head += [f"col{i}" for i in range(width)]

    no_spp = 0
    with open(args.output, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(head)
        for k in order:
            r = collected[k]
            p = parse_row(r["cells"])
            if not p["spp_pct"]:
                no_spp += 1
            row = [p["wb_id"], p["sku"], p["brand"], p["name"],
                   p["base_price"], p["seller_disc"], p["price_after_disc"],
                   p["spp_pct"], p["spp_price"], r["href"]]
            if args.raw:
                cells = r["cells"] + [""] * (width - len(r["cells"]))
                row += [c.replace("\n", " | ") for c in cells]
            w.writerow(row)

    print(f"\nГотово: {args.output} — {len(order)} строк")
    if no_spp:
        print(f"Без СПП: {no_spp} строк "
              f"(возможно, у товара её просто нет)")


if __name__ == "__main__":
    main()
