#!/usr/bin/env python3
"""
Диагностика прокрутки. Показывает все скроллящиеся элементы страницы
и проверяет, реагируют ли они на scrollTop.

Запуск (Chrome с --remote-debugging-port=9222 уже открыт на нужной странице):
    python diagnose_scroll.py
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

JS = """
const out = [];

// окно
out.push({
    what: 'WINDOW',
    sel: '(window)',
    client: window.innerHeight,
    scroll: document.documentElement.scrollHeight,
    x: 0, y: 0, w: window.innerWidth, h: window.innerHeight
});

document.querySelectorAll('*').forEach(el => {
    if (el.scrollHeight <= el.clientHeight + 20) return;
    if (el.clientHeight < 100) return;
    const st = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    let sel = el.tagName.toLowerCase();
    if (el.id) sel += '#' + el.id;
    if (el.className && typeof el.className === 'string') {
        sel += '.' + el.className.trim().split(/\\s+/).slice(0, 3).join('.');
    }
    out.push({
        what: 'ELEMENT',
        sel: sel,
        overflowY: st.overflowY,
        client: el.clientHeight,
        scroll: el.scrollHeight,
        x: Math.round(r.x), y: Math.round(r.y),
        w: Math.round(r.width), h: Math.round(r.height)
    });
});
return out;
"""

JS_TEST = """
const el = document.querySelectorAll('*')[arguments[0]];
return null;
"""

JS_TRY = """
// пробуем реально прокрутить элемент по CSS-селектору
const el = arguments[0] === '(window)' ? null : document.querySelector(arguments[0]);
if (arguments[0] === '(window)') {
    const before = window.pageYOffset;
    window.scrollTo(0, before + 300);
    const after = window.pageYOffset;
    window.scrollTo(0, before);
    return {before: before, after: after, moved: after - before};
}
if (!el) return {error: 'не найден'};
const before = el.scrollTop;
el.scrollTop = before + 300;
const after = el.scrollTop;
el.scrollTop = before;
return {before: before, after: after, moved: after - before};
"""

opts = Options()
opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
d = webdriver.Chrome(options=opts)

print(f"Страница: {d.title}")
print(f"URL: {d.current_url}\n")

items = d.execute_script(JS)
print(f"Найдено кандидатов: {len(items)}\n")

for i, it in enumerate(items):
    print(f"[{i}] {it['what']}  {it['sel']}")
    print(f"    видно {it['client']} px, всего {it['scroll']} px "
          f"(запас {it['scroll'] - it['client']} px)")
    print(f"    позиция x={it['x']} y={it['y']} размер {it['w']}x{it['h']}")
    if it.get('overflowY'):
        print(f"    overflow-y: {it['overflowY']}")

    try:
        res = d.execute_script(JS_TRY, it['sel'])
        if res.get('error'):
            print(f"    ПРОВЕРКА: селектор не сработал")
        elif res['moved'] > 0:
            print(f"    ПРОВЕРКА: ПРОКРУЧИВАЕТСЯ (сдвинулся на {res['moved']} px)")
        else:
            print(f"    ПРОВЕРКА: не двигается (scrollTop заблокирован)")
    except Exception as e:
        print(f"    ПРОВЕРКА: ошибка — {e}")
    print()
