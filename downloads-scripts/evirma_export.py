#!/usr/bin/env python3
"""
Открывает карточку товара WB и выгружает отчёт расширения Evirma.

ВАЖНО: расширение Evirma должно быть установлено в том профиле Chrome,
который запущен с --remote-debugging-port. Профиль C:\\chrome-debug —
чистый, расширений в нём нет. Проверьте: chrome://extensions

Разведка (посмотреть, что вообще есть на странице):
    python evirma_export.py 213873739 --discover

Выгрузка:
    python evirma_export.py 213873739
    python evirma_export.py 213873739 --text "Export"
    python evirma_export.py 213873739 --downloads "C:\\Users\\User\\Downloads"
"""

import argparse
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

PRODUCT_URL = "https://www.wildberries.ru/catalog/{}/detail.aspx"

# Обходим и обычный DOM, и Shadow DOM — расширения часто прячут UI туда
JS_WALK = """
function walk(root, out, depth) {
    if (depth > 12) return;
    let nodes;
    try { nodes = root.querySelectorAll('*'); } catch (e) { return; }
    nodes.forEach(el => {
        out.push(el);
        if (el.shadowRoot) walk(el.shadowRoot, out, depth + 1);
    });
}
const all = [];
walk(document, all, 0);
return all.length;
"""

JS_FIND_EVIRMA = """
function walk(root, out, depth) {
    if (depth > 12) return;
    let nodes;
    try { nodes = root.querySelectorAll('*'); } catch (e) { return; }
    for (const el of nodes) {
        out.push(el);
        if (el.shadowRoot) walk(el.shadowRoot, out, depth + 1);
    }
}
const all = [];
walk(document, all, 0);

const res = {blocks: [], clickables: [], total: all.length};

// 1. Блоки, в которых упоминается Evirma
all.forEach(el => {
    const id = (el.id || '');
    const cls = (typeof el.className === 'string' ? el.className : '');
    if (/evirma/i.test(id) || /evirma/i.test(cls)) {
        const r = el.getBoundingClientRect();
        if (r.width < 10 || r.height < 10) return;
        res.blocks.push({
            tag: el.tagName.toLowerCase(), id: id.slice(0, 50),
            cls: cls.slice(0, 70),
            x: Math.round(r.left), y: Math.round(r.top + window.pageYOffset),
            w: Math.round(r.width), h: Math.round(r.height)
        });
    }
});

// 2. Всё кликабельное с подходящим текстом
const want = /export|excel|xlsx|выгруз|скачат|экспорт|отчёт|отчет/i;
all.forEach(el => {
    const tag = el.tagName.toLowerCase();
    const clickable = tag === 'button' || tag === 'a' ||
        el.getAttribute('role') === 'button' ||
        (el.onclick !== null && el.onclick !== undefined) ||
        /btn|button/i.test(typeof el.className === 'string' ? el.className : '');
    if (!clickable) return;
    const txt = (el.innerText || el.textContent || '').trim();
    const title = el.getAttribute('title') || el.getAttribute('aria-label') || '';
    if (!want.test(txt) && !want.test(title)) return;
    if (txt.length > 60) return;
    const r = el.getBoundingClientRect();
    if (r.width < 5 || r.height < 5) return;
    res.clickables.push({
        tag: tag, text: txt.slice(0, 60), title: title.slice(0, 50),
        cls: (typeof el.className === 'string' ? el.className : '').slice(0, 70),
        href: el.getAttribute('href') || '',
        x: Math.round(r.left), y: Math.round(r.top + window.pageYOffset),
        w: Math.round(r.width), h: Math.round(r.height),
        inShadow: !el.ownerDocument.contains(el)
    });
});
return res;
"""

JS_CLICK_BY_TEXT = """
function walk(root, out, depth) {
    if (depth > 12) return;
    let nodes;
    try { nodes = root.querySelectorAll('*'); } catch (e) { return; }
    for (const el of nodes) {
        out.push(el);
        if (el.shadowRoot) walk(el.shadowRoot, out, depth + 1);
    }
}
const all = [];
walk(document, all, 0);

const want = new RegExp(arguments[0], 'i');
for (const el of all) {
    const tag = el.tagName.toLowerCase();
    if (!(tag === 'button' || tag === 'a' ||
          el.getAttribute('role') === 'button' ||
          /btn|button/i.test(typeof el.className === 'string' ? el.className : '')))
        continue;
    const txt = (el.innerText || el.textContent || '').trim();
    const title = el.getAttribute('title') || el.getAttribute('aria-label') || '';
    if (txt.length > 60 && !want.test(title)) continue;
    if (!want.test(txt) && !want.test(title)) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 5 || r.height < 5) continue;
    el.scrollIntoView({block: 'center'});
    el.click();
    return {ok: true, text: txt.slice(0, 60), tag: tag};
}
return {ok: false};
"""


def attach(port):
    o = Options()
    o.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    return webdriver.Chrome(options=o)


def slow_scroll(driver, steps=14, pause=0.7):
    """Прокручиваем страницу до низа — расширение рисует блок лениво."""
    for _ in range(steps):
        driver.execute_script("window.scrollBy(0, window.innerHeight * 0.8);")
        time.sleep(pause)
    time.sleep(1.5)


def snapshot(folder):
    try:
        return {f: os.path.getmtime(os.path.join(folder, f))
                for f in os.listdir(folder)}
    except Exception:
        return {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("article", help="артикул WB")
    ap.add_argument("--port", type=int, default=9222)
    ap.add_argument("--discover", action="store_true",
                    help="только показать, что найдено на странице")
    ap.add_argument("--text", default="export|excel|xlsx|выгруз|скачат|экспорт",
                    help="регулярка для текста кнопки выгрузки")
    ap.add_argument("--downloads",
                    default=os.path.join(os.path.expanduser("~"), "Downloads"),
                    help="папка загрузок Chrome")
    ap.add_argument("--wait", type=float, default=25,
                    help="сколько ждать появления файла, сек")
    ap.add_argument("--scroll-steps", type=int, default=14)
    args = ap.parse_args()

    d = attach(args.port)
    url = PRODUCT_URL.format(args.article)
    print(f"Открываю {url}")
    d.get(url)
    time.sleep(3)
    print(f"Заголовок: {d.title}")

    print("Прокручиваю страницу, чтобы Evirma отрисовалась...")
    slow_scroll(d, args.scroll_steps)

    res = d.execute_script(JS_FIND_EVIRMA)
    print(f"\nЭлементов на странице (включая Shadow DOM): {res['total']}")

    print(f"\n=== БЛОКИ EVIRMA ({len(res['blocks'])}) ===")
    for i, b in enumerate(res["blocks"]):
        print(f"[{i}] <{b['tag']}> id={b['id']} class={b['cls']}")
        print(f"    y={b['y']} размер {b['w']}x{b['h']}")

    print(f"\n=== КНОПКИ ВЫГРУЗКИ ({len(res['clickables'])}) ===")
    for i, c in enumerate(res["clickables"]):
        print(f"[{i}] <{c['tag']}> «{c['text']}»")
        if c["title"]:
            print(f"    title/aria: {c['title']}")
        print(f"    class: {c['cls']}")
        if c["href"]:
            print(f"    href: {c['href'][:80]}")
        print(f"    y={c['y']} размер {c['w']}x{c['h']} "
              f"{'[Shadow DOM]' if c['inShadow'] else ''}")

    if args.discover:
        print("\nРежим разведки — ничего не нажимаю.")
        if not res["blocks"]:
            print("Блоков Evirma не найдено. Проверьте:")
            print("  1. расширение установлено в ЭТОМ профиле Chrome?")
            print("     откройте chrome://extensions в отладочном окне")
            print("  2. оно включено для сайта wildberries.ru?")
            print("  3. видно ли панель Evirma на странице глазами?")
        return

    if not res["clickables"]:
        print("\nКнопка выгрузки не найдена. Запустите с --discover "
              "и пришлите вывод.")
        return

    before = snapshot(args.downloads)
    print(f"\nВ папке загрузок сейчас {len(before)} файлов")

    clicked = d.execute_script(JS_CLICK_BY_TEXT, args.text)
    if not clicked["ok"]:
        print("Не удалось нажать кнопку. Попробуйте --text с другим словом.")
        return
    print(f"Нажал: <{clicked['tag']}> «{clicked['text']}»")

    print(f"Жду файл до {args.wait} сек...")
    deadline = time.time() + args.wait
    found = None
    while time.time() < deadline:
        time.sleep(1)
        now = snapshot(args.downloads)
        new = [f for f in now
               if f not in before and not f.endswith((".crdownload", ".tmp"))]
        if new:
            found = max(new, key=lambda f: now[f])
            break

    if found:
        path = os.path.join(args.downloads, found)
        size = os.path.getsize(path)
        print(f"\nГотово: {path} ({size} байт)")
    else:
        print("\nНовый файл не появился. Возможные причины:")
        print("  - Chrome спросил, куда сохранять (снимите галку "
              "«Всегда спрашивать» в настройках загрузок)")
        print("  - выгрузка идёт дольше, поднимите --wait")
        print("  - папка загрузок другая, укажите --downloads")


if __name__ == "__main__":
    main()
