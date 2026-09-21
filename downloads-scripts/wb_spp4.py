#!/usr/bin/env python3
"""
Сбор СПП из таблицы цен WB — v4. Без потери строк.

Что добавлено против v3:
  * контроль перекрытия: если среди видимых строк нет ни одной знакомой,
    значит шаг перепрыгнул кусок списка — скрипт откатывается и уменьшает шаг
  * шаг считается от высоты строки и размера отрисованного буфера
  * оценка ожидаемого числа строк по scrollHeight / высоту строки
  * контрольный второй проход снизу вверх

    python wb_spp4.py spp.csv
    python wb_spp4.py spp.csv --pause 1.5
    python wb_spp4.py spp.csv --expect 120      # знаете точное число товаров
    python wb_spp4.py spp.csv --raw
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
const rows = el.querySelectorAll('[data-row-key], .ant-table-row');
let rowH = 0;
if (rows.length >= 2) {
    const a = rows[0].getBoundingClientRect();
    const b = rows[1].getBoundingClientRect();
    rowH = Math.round(Math.abs(b.top - a.top)) || Math.round(a.height);
} else if (rows.length === 1) {
    rowH = Math.round(rows[0].getBoundingClientRect().height);
}
return {found: true, scroll: el.scrollHeight, client: el.clientHeight,
        rendered: rows.length, rowH: rowH};
"""

JS_SET_TOP = """
const el = document.querySelector(arguments[0]);
el.scrollTop = arguments[1];
el.dispatchEvent(new Event('scroll', {bubbles: true}));
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
        elif i > 0 and "/" in line and not sku:
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
    ap.add_argument("--expect", type=int, default=None,
                    help="ожидаемое число товаров для проверки")
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--max", type=int, default=2000)
    args = ap.parse_args()

    o = Options()
    o.add_experimental_option("debuggerAddress", f"127.0.0.1:{args.port}")
    d = webdriver.Chrome(options=o)
    d.set_script_timeout(30)

    print(f"Страница: {d.title}")
    info = d.execute_script(JS_PREP, args.selector)
    if not info["found"]:
        raise SystemExit(f"Элемент {args.selector} не найден")

    row_h = info["rowH"] or 100
    rendered = info["rendered"] or 10
    total_px = info["scroll"]
    estimate = round(total_px / row_h) if row_h else 0

    print(f"Высота строки ~{row_h} px, в DOM одновременно {rendered} строк")
    print(f"Содержимое {total_px} px → ожидаю примерно {estimate} товаров")

    # Шаг = половина отрисованного буфера. Гарантирует перекрытие
    # даже если список перерисовывается с запозданием.
    step = max(row_h, int(rendered * row_h * 0.5))
    print(f"Шаг прокрутки: {step} px\n")

    collected, order = {}, []

    def harvest():
        rows = d.execute_script(JS_ROWS, args.selector)
        keys = []
        added = 0
        for row in rows:
            k = row["key"] or (row["cells"][0][:80] if row["cells"] else "")
            if not k:
                continue
            keys.append(k)
            if k not in collected:
                collected[k] = row
                order.append(k)
                added += 1
        return keys, added

    def sweep(direction="down"):
        nonlocal step
        pos = 0 if direction == "down" else None
        st = d.execute_script(JS_SET_TOP, args.selector, 0 if pos == 0 else 10 ** 7)
        time.sleep(args.pause)
        pos = st["top"]
        max_top = st["max"]
        prev_keys, added = harvest()
        print(f"  старт {direction}: позиция {int(pos)}, собрано {len(order)}")

        idle = 0
        for i in range(args.max):
            nxt = pos + step if direction == "down" else pos - step
            nxt = max(0, min(nxt, max_top))
            st = d.execute_script(JS_SET_TOP, args.selector, nxt)
            time.sleep(args.pause)
            pos = st["top"]
            max_top = st["max"]

            keys, added = harvest()

            # Проверка перекрытия: хоть одна строка должна быть знакомой
            overlap = len(set(keys) & set(prev_keys))
            if overlap == 0 and keys and prev_keys:
                step = max(row_h, int(step * 0.6))
                print(f"    ! перекрытия нет — шаг уменьшен до {step} px, "
                      f"откат назад")
                back = pos - step if direction == "down" else pos + step
                st = d.execute_script(JS_SET_TOP, args.selector,
                                      max(0, min(back, max_top)))
                time.sleep(args.pause)
                pos = st["top"]
                keys, added = harvest()

            prev_keys = keys
            print(f"    {int(pos)}/{int(max_top)} — в DOM {len(keys)}, "
                  f"перекрытие {overlap}, всего {len(order)} (+{added})")

            idle = idle + 1 if added == 0 else 0
            at_end = (pos >= max_top - 1) if direction == "down" else (pos <= 1)
            if at_end and idle >= 2:
                break
            if idle >= 8:
                break

    print("Проход сверху вниз:")
    sweep("down")

    print(f"\nПроход снизу вверх (контрольный):")
    before = len(order)
    sweep("up")
    found_extra = len(order) - before
    if found_extra:
        print(f"  обратный проход нашёл ещё {found_extra} строк")

    if not order:
        raise SystemExit("Строки не найдены")

    # Сортируем в порядке появления сверху вниз по data-row-key нельзя,
    # поэтому оставляем порядок первого обнаружения при проходе вниз.
    head = ["Артикул WB", "Артикул продавца", "Бренд", "Название",
            "Цена до скидки", "Скидка продавца %", "Цена после скидки",
            "СПП %", "Цена после СПП", "Ссылка"]
    width = max(len(collected[k]["cells"]) for k in order)
    if args.raw:
        head += [f"col{i}" for i in range(width)]

    no_spp = 0
    seen_ids = set()
    dupes = 0
    with open(args.output, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(head)
        for k in order:
            r = collected[k]
            p = parse_row(r["cells"])
            if not p["spp_pct"]:
                no_spp += 1
            if p["wb_id"]:
                if p["wb_id"] in seen_ids:
                    dupes += 1
                seen_ids.add(p["wb_id"])
            row = [p["wb_id"], p["sku"], p["brand"], p["name"],
                   p["base_price"], p["seller_disc"], p["price_after_disc"],
                   p["spp_pct"], p["spp_price"], r["href"]]
            if args.raw:
                cells = r["cells"] + [""] * (width - len(r["cells"]))
                row += [c.replace("\n", " | ") for c in cells]
            w.writerow(row)

    print(f"\n{'=' * 50}")
    print(f"Готово: {args.output}")
    print(f"  строк собрано:      {len(order)}")
    print(f"  уникальных артикулов: {len(seen_ids)}")
    print(f"  оценка по высоте:   {estimate}")
    if args.expect:
        diff = args.expect - len(seen_ids)
        if diff > 0:
            print(f"  НЕ ХВАТАЕТ {diff} товаров — запустите ещё раз "
                  f"с --pause {args.pause + 1}")
        elif diff == 0:
            print(f"  все {args.expect} товаров на месте")
    elif estimate and abs(estimate - len(order)) > max(3, estimate * 0.05):
        print(f"  ! расхождение с оценкой — возможны пропуски, "
              f"поднимите --pause")
    if dupes:
        print(f"  повторов артикула:  {dupes}")
    if no_spp:
        print(f"  строк без СПП:      {no_spp}")


if __name__ == "__main__":
    main()
