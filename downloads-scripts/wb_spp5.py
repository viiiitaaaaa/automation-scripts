#!/usr/bin/env python3
"""
Сбор СПП из таблицы цен WB — v5.

Новое: перед сбором скрипт сам включает тумблер «С остатками»
и ждёт, пока таблица перестроится под фильтр.

    python wb_spp5.py spp.csv
    python wb_spp5.py spp.csv --expect 120
    python wb_spp5.py spp.csv --no-stock      # не трогать тумблер
    python wb_spp5.py spp.csv --toggle "Без цены"   # другой тумблер
    python wb_spp5.py spp.csv --raw
"""

import argparse
import csv
import re
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

HOLDER = "div.ant-table-tbody-virtual-holder"

# ---------------------------------------------------------------- тумблер

JS_FIND_TOGGLE = """
const want = arguments[0];
const switches = document.querySelectorAll(
    'button.ant-switch, .ant-switch, [role="switch"], input[type="checkbox"]');
for (const s of switches) {
    // ищем подпись рядом: поднимаемся на несколько уровней вверх
    let p = s.parentElement, txt = '';
    for (let i = 0; i < 4 && p; i++) {
        const t = (p.innerText || '').trim();
        if (t.includes(want)) { txt = t; break; }
        p = p.parentElement;
    }
    if (!txt) continue;
    // подпись не должна тащить за собой пол-страницы
    if (txt.length > 120) continue;

    const checked = s.classList.contains('ant-switch-checked')
        || s.getAttribute('aria-checked') === 'true'
        || s.checked === true;
    s.setAttribute('data-wb-toggle', '1');
    return {found: true, checked: checked, label: txt.slice(0, 60)};
}
return {found: false};
"""

JS_CLICK_TOGGLE = """
const s = document.querySelector('[data-wb-toggle]');
if (!s) return {ok: false};
s.click();
return {ok: true};
"""

JS_TOGGLE_STATE = """
const s = document.querySelector('[data-wb-toggle]');
if (!s) return null;
return s.classList.contains('ant-switch-checked')
    || s.getAttribute('aria-checked') === 'true'
    || s.checked === true;
"""

JS_TABLE_STATE = """
const el = document.querySelector(arguments[0]);
if (!el) return {ready: false};
const rows = el.querySelectorAll('[data-row-key], .ant-table-row');
const first = rows.length ? (rows[0].getAttribute('data-row-key') || '') : '';
return {ready: true, scroll: el.scrollHeight, rendered: rows.length,
        first: first};
"""

# ------------------------------------------------------------- прокрутка

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
    out.push({key: tr.getAttribute('data-row-key') || '', cells: cells});
});
return out;
"""

# ---------------------------------------------------------------- разбор

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


# ------------------------------------------------------------------ main

def wait_table_settled(d, selector, pause=0.6, tries=25):
    """Ждём, пока таблица перестанет меняться после переключения фильтра."""
    prev = None
    stable = 0
    for _ in range(tries):
        time.sleep(pause)
        st = d.execute_script(JS_TABLE_STATE, selector)
        if not st or not st.get("ready"):
            continue
        sig = (st["scroll"], st["rendered"], st["first"])
        if sig == prev and st["rendered"] > 0:
            stable += 1
            if stable >= 2:
                return st
        else:
            stable = 0
        prev = sig
    return d.execute_script(JS_TABLE_STATE, selector)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output", nargs="?", default="spp.csv")
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--selector", default=HOLDER)
    ap.add_argument("--toggle", default="С остатками",
                    help="подпись тумблера, который надо включить")
    ap.add_argument("--no-stock", action="store_true",
                    help="не трогать тумблер вообще")
    ap.add_argument("--pause", type=float, default=1.0)
    ap.add_argument("--expect", type=int, default=None)
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--max", type=int, default=2000)
    args = ap.parse_args()

    o = Options()
    o.add_experimental_option("debuggerAddress", f"127.0.0.1:{args.port}")
    d = webdriver.Chrome(options=o)
    d.set_script_timeout(30)
    print(f"Страница: {d.title}")

    # --- тумблер «С остатками»
    if not args.no_stock:
        t = d.execute_script(JS_FIND_TOGGLE, args.toggle)
        if not t["found"]:
            print(f"! Тумблер «{args.toggle}» не найден. "
                  f"Включите его вручную и запустите с --no-stock")
        elif t["checked"]:
            print(f"Тумблер «{args.toggle}» уже включён")
        else:
            print(f"Включаю тумблер «{args.toggle}»...")
            before = d.execute_script(JS_TABLE_STATE, args.selector)
            d.execute_script(JS_CLICK_TOGGLE)
            time.sleep(0.5)
            state = d.execute_script(JS_TOGGLE_STATE)
            if state is not True:
                # клик через JS не прошёл — пробуем как настоящий пользователь
                try:
                    el = d.find_element("css selector", "[data-wb-toggle]")
                    el.click()
                    time.sleep(0.5)
                    state = d.execute_script(JS_TOGGLE_STATE)
                except Exception as e:
                    print(f"  клик не удался: {e}")
            print(f"  состояние тумблера: "
                  f"{'включён' if state else 'НЕ включился'}")
            after = wait_table_settled(d, args.selector, args.pause)
            if before and after and before.get("ready") and after.get("ready"):
                print(f"  таблица перестроилась: было {before['scroll']} px, "
                      f"стало {after['scroll']} px")

    # --- сбор
    info = d.execute_script(JS_PREP, args.selector)
    if not info["found"]:
        raise SystemExit(f"Элемент {args.selector} не найден")

    row_h = info["rowH"] or 100
    rendered = info["rendered"] or 10
    estimate = round(info["scroll"] / row_h) if row_h else 0
    step = max(row_h, int(rendered * row_h * 0.5))
    print(f"\nВысота строки ~{row_h} px, в DOM {rendered} строк")
    print(f"Ожидаю примерно {estimate} товаров, шаг {step} px\n")

    collected, order = {}, []

    def harvest():
        keys, added = [], 0
        for row in d.execute_script(JS_ROWS, args.selector):
            k = row["key"] or (row["cells"][0][:80] if row["cells"] else "")
            if not k:
                continue
            keys.append(k)
            if k not in collected:
                collected[k] = row
                order.append(k)
                added += 1
        return keys, added

    def sweep(direction):
        nonlocal step
        st = d.execute_script(JS_SET_TOP, args.selector,
                              0 if direction == "down" else 10 ** 7)
        time.sleep(args.pause)
        pos, max_top = st["top"], st["max"]
        prev_keys, _ = harvest()
        idle = 0
        for i in range(args.max):
            nxt = pos + step if direction == "down" else pos - step
            nxt = max(0, min(nxt, max_top))
            st = d.execute_script(JS_SET_TOP, args.selector, nxt)
            time.sleep(args.pause)
            pos, max_top = st["top"], st["max"]
            keys, added = harvest()

            overlap = len(set(keys) & set(prev_keys))
            if overlap == 0 and keys and prev_keys:
                step = max(row_h, int(step * 0.6))
                print(f"    ! перекрытия нет — шаг {step} px, откат")
                back = pos - step if direction == "down" else pos + step
                st = d.execute_script(JS_SET_TOP, args.selector,
                                      max(0, min(back, max_top)))
                time.sleep(args.pause)
                pos = st["top"]
                keys, added = harvest()

            prev_keys = keys
            print(f"    {int(pos)}/{int(max_top)} — DOM {len(keys)}, "
                  f"перекрытие {overlap}, всего {len(order)} (+{added})")

            idle = idle + 1 if added == 0 else 0
            at_end = (pos >= max_top - 1) if direction == "down" else (pos <= 1)
            if (at_end and idle >= 2) or idle >= 8:
                break

    print("Проход вниз:")
    sweep("down")
    print("\nПроход вверх:")
    before_n = len(order)
    sweep("up")
    if len(order) - before_n:
        print(f"  обратный проход добрал {len(order) - before_n} строк")

    if not order:
        raise SystemExit("Строки не найдены")

    head = ["Артикул WB", "Артикул продавца", "Бренд", "Название",
            "Цена до скидки", "Скидка продавца %", "Цена после скидки",
            "СПП %", "Цена после СПП"]
    width = max(len(collected[k]["cells"]) for k in order)
    if args.raw:
        head += [f"col{i}" for i in range(width)]

    no_spp = 0
    ids = set()
    with open(args.output, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(head)
        for k in order:
            r = collected[k]
            p = parse_row(r["cells"])
            if not p["spp_pct"]:
                no_spp += 1
            if p["wb_id"]:
                ids.add(p["wb_id"])
            row = [p["wb_id"], p["sku"], p["brand"], p["name"],
                   p["base_price"], p["seller_disc"], p["price_after_disc"],
                   p["spp_pct"], p["spp_price"]]
            if args.raw:
                cells = r["cells"] + [""] * (width - len(r["cells"]))
                row += [c.replace("\n", " | ") for c in cells]
            w.writerow(row)

    print(f"\n{'=' * 50}")
    print(f"Готово: {args.output}")
    print(f"  строк:              {len(order)}")
    print(f"  уникальных артикулов: {len(ids)}")
    print(f"  оценка по высоте:   {estimate}")
    if args.expect:
        diff = args.expect - len(ids)
        print(f"  {'не хватает ' + str(diff) if diff > 0 else 'всё на месте'}")
    if no_spp:
        print(f"  строк без СПП:      {no_spp}")


if __name__ == "__main__":
    main()
