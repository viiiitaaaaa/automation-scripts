#!/usr/bin/env python3
"""
Сбор СПП из таблицы цен WB — v3.

Прокрутка идёт «к последней отрисованной строке»: виртуальный список
сам дорисовывает следующую порцию. Зависающий CDP-вызов колеса убран.

    python wb_spp3.py spp.csv
    python wb_spp3.py spp.csv --pause 1.5
    python wb_spp3.py spp.csv --raw
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
const s = document.getElementById('__shot_style') || document.createElement('style');
s.id = '__shot_style';
s.textContent = 'html{scroll-behavior:auto!important;}';
if (!s.parentNode) document.head.appendChild(s);
el.scrollTop = 0;
return {found: true, scroll: el.scrollHeight, client: el.clientHeight};
"""

# Три способа сдвинуться, по очереди — что сработает, то и используется
JS_ADVANCE = """
const holder = document.querySelector(arguments[0]);
const step = arguments[1];
const before = holder.scrollTop;

// 1. подвести последнюю отрисованную строку к низу видимой области
const rows = holder.querySelectorAll('[data-row-key], .ant-table-row');
if (rows.length) {
    rows[rows.length - 1].scrollIntoView({block: 'end', behavior: 'auto'});
}
let after = holder.scrollTop;

// 2. если не помогло — обычный scrollTop
if (after <= before) {
    holder.scrollTop = before + step;
    after = holder.scrollTop;
}

// 3. если и это не помогло — scrollBy
if (after <= before) {
    holder.scrollBy(0, step);
    after = holder.scrollTop;
}

holder.dispatchEvent(new Event('scroll', {bubbles: true}));
return {before: before, after: after, rendered: rows.length,
        max: holder.scrollHeight - holder.clientHeight,
        scroll: holder.scrollHeight};
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
    out.push({key: tr.getAttribute('data-row-key') || '',
              cells: cells, href: link ? link.href : ''});
});
return out;
"""

RE_SPP = re.compile(r"СПП\s*([\d]+[.,]?[\d]*)\s*%", re.I)
RE_MONEY = re.compile(r"([\d][\d\s\u00a0]*[.,]?\d*)\s*₽")
RE_WBID = re.compile(r"^\d{6,12}$")


def money(s):
    return s.replace(" ", "").replace("\u00a0", "").replace(".", ",").strip()


def parse_row(cells):
    first = cells[0] if cells else ""
    lines = [l.strip() for l in first.split("\n") if l.strip()]

    name = lines[0] if lines else ""
    wb_id = brand = sku = ""

    for i, line in enumerate(lines):
        if RE_WBID.match(line) and not wb_id:
            wb_id = line
            if i >= 1:
                brand = lines[i - 1]
        elif i > 0 and ("/" in line) and not sku:
            sku = line.lstrip("•").strip()

    spp_pct = spp_price = price_after_disc = ""
    for c in cells:
        m = RE_SPP.search(c)
        if m:
            spp_pct = m.group(1).replace(".", ",")
            mp = RE_MONEY.search(c[m.end():])
            if mp:
                spp_price = money(mp.group(1))
            mf = RE_MONEY.search(c)
            if mf and mf.start() < m.start():
                price_after_disc = money(mf.group(1))
            break

    base_price = seller_disc = ""
    for c in cells[1:]:
        t = c.strip()
        if not base_price and re.fullmatch(r"[\d\s\u00a0]+₽", t):
            base_price = money(RE_MONEY.search(t).group(1))
        elif not seller_disc and re.fullmatch(r"\d+\s*%", t):
            seller_disc = t.replace("%", "").strip()

    return dict(wb_id=wb_id, sku=sku, brand=brand, name=name,
                base_price=base_price, seller_disc=seller_disc,
                price_after_disc=price_after_disc,
                spp_pct=spp_pct, spp_price=spp_price)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output", nargs="?", default="spp.csv")
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--selector", default=HOLDER)
    ap.add_argument("--pause", type=float, default=1.0)
    ap.add_argument("--step", type=int, default=350)
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--max", type=int, default=1000)
    args = ap.parse_args()

    o = Options()
    o.add_experimental_option("debuggerAddress", f"127.0.0.1:{args.port}")
    d = webdriver.Chrome(options=o)
    d.set_script_timeout(30)

    print(f"Страница: {d.title}")
    info = d.execute_script(JS_PREP, args.selector)
    if not info["found"]:
        raise SystemExit(f"Элемент {args.selector} не найден")
    print(f"Контейнер: содержимое {info['scroll']} px, видно {info['client']} px")

    collected, order = {}, []
    idle = 0

    def harvest():
        added = 0
        for row in d.execute_script(JS_ROWS, args.selector):
            k = row["key"] or (row["cells"][0][:80] if row["cells"] else "")
            if k and k not in collected:
                collected[k] = row
                order.append(k)
                added += 1
        return added

    harvest()
    print(f"  стартовая порция: {len(order)} строк")

    for i in range(args.max):
        st = d.execute_script(JS_ADVANCE, args.selector, args.step)
        time.sleep(args.pause)
        added = harvest()

        moved = st["after"] - st["before"]
        print(f"  шаг {i + 1}: сдвиг {int(moved)} px, "
              f"позиция {int(st['after'])}/{int(st['max'])}, "
              f"в DOM {st['rendered']}, всего {len(order)} (+{added})")

        idle = idle + 1 if added == 0 else 0

        if moved <= 0 and added == 0:
            print("  прокрутка не двигается и новых строк нет — конец")
            break
        if idle >= 5:
            print("  5 шагов без новых строк — конец списка")
            break

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
        print(f"Без СПП: {no_spp}")


if __name__ == "__main__":
    main()
