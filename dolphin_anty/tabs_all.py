"""
Снять ВСЕ страницы магазинов AliExpress через профиль Dolphin{anty}.

  * работает по уже открытым вкладкам либо по заданным ссылкам;
  * снимает не первые N страниц, а ВСЕ до конца пагинации;
  * прогресс пишется после каждой страницы — обрыв не теряет работу;
  * вкладки не плодятся: одна ссылка = одна вкладка, закрывается после съёмки.

    python tabs_all.py                      # все открытые вкладки
    python tabs_all.py --tab 2              # только вторая вкладка
    python tabs_all.py --url ССЫЛКА         # по ссылке (можно повторять)
    python tabs_all.py --url ССЫЛКА --fresh # снять заново, игнорируя прогресс
    python tabs_all.py --max-pages 30       # предохранитель (по умолчанию 60)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests

from shots import autoscroll, first_cards, store_name
from open_links import to_desktop

OUT_DIR = Path.home() / "Desktop" / "скрины магазинов"
STATE = Path(__file__).with_name("state_tabs.json")
BAD_CHARS = r'[<>:"/\\|?*]'


def find_cdp() -> tuple[int, str]:
    """Найти живой CDP уже запущенного браузера."""
    import subprocess
    out = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True).stdout
    ports = sorted({int(m.group(1)) for m in
                    (re.search(r"127\.0\.0\.1:(\d+)\s+.*LISTENING", ln) for ln in out.splitlines())
                    if m})
    for p in ports:
        try:
            r = requests.get(f"http://127.0.0.1:{p}/json/version", timeout=1)
            if r.status_code == 200 and "webSocketDebuggerUrl" in r.text:
                return p, r.json()["webSocketDebuggerUrl"]
        except Exception:  # noqa: BLE001
            pass
    raise RuntimeError("CDP не найден — профиль запущен без automation?")


def go_next(page, target: int) -> bool:
    """Перейти на страницу `target`: сначала по номеру, иначе стрелкой «вперёд».

    У магазина клиентская пагинация: URL не меняется, поэтому факт перехода
    проверяем по смене карточек товаров.
    """
    before = first_cards(page)

    # AliExpress выкатывает панель `cosmos-drawer-wrap` и прочие оверлеи; они
    # перехватывают указатель, и обычный клик Playwright висит до таймаута.
    page.evaluate("""() => {
        const sel = '.cosmos-drawer-wrap, .cosmos-drawer, .next-overlay-wrapper,'
                  + '[class*="overlay-mask"], [class*="drawer-mask"], [class*="popup-mask"]';
        document.querySelectorAll(sel).forEach(e => e.remove());
    }""")

    # Клик делаем из JS: он не проверяет перекрытие элемента и не ждёт стабильности.
    clicked = page.evaluate("""(t) => {
        const a = [...document.querySelectorAll('a')]
            .filter(x => (x.innerText || '').trim() === String(t) && x.offsetParent !== null)
            .pop();
        if (!a) return false;
        a.scrollIntoView({block: 'center'});
        a.click();
        return true;
    }""", target)

    if not clicked:
        # номера кончились (окно пагинатора уехало) — жмём стрелку «следующая»
        clicked = page.evaluate("""() => {
            const nums = [...document.querySelectorAll('a')]
                .filter(a => /^\\d{1,3}$/.test((a.innerText || '').trim()));
            if (!nums.length) return false;
            const box = nums[nums.length - 1].parentElement?.parentElement;
            if (!box) return false;
            const kids = [...box.querySelectorAll('a, button, [role="button"]')];
            const lastNum = kids.lastIndexOf(nums[nums.length - 1]);
            const nxt = kids.slice(lastNum + 1).find(e => e.offsetParent !== null);
            if (!nxt) return false;
            nxt.click();
            return true;
        }""")

    if not clicked:
        return False

    deadline = time.time() + 45
    while time.time() < deadline:
        time.sleep(1)
        now = first_cards(page)
        if now and now != before:
            return True
    return False


def shoot_tab(page, out_root: Path, max_pages: int, state: dict, fresh: bool = False,
              shot_timeout: int = 180_000) -> bool:
    """Снять все страницы магазина. True — дошли до конца, False — прервались."""
    page.bring_to_front()

    # мобильная версия не годится: другая вёрстка и нет пагинации
    desktop = to_desktop(page.url)
    if desktop != page.url:
        print("    [i] мобильная версия — перехожу на браузерную")
        page.goto(desktop, wait_until="domcontentloaded", timeout=90_000)

    page.wait_for_selector('a[href*="/item/"]', timeout=60_000)
    time.sleep(1.5)

    name = re.sub(BAD_CHARS, "", store_name(page, page.url)).strip() or "магазин"
    out_dir = out_root / name
    out_dir.mkdir(parents=True, exist_ok=True)
    done = set() if fresh else set(state.get(name, {}).get("pages", []))
    print(f"\n=== {name}")
    if done:
        print(f"    уже снято страниц: {sorted(done)}")

    n = 1
    while n <= max_pages:
        if n in done:
            print(f"    страница {n} — уже есть, пропускаю")
        else:
            autoscroll(page)
            out = out_dir / f"{name} — страница {n}.png"
            try:
                page.screenshot(path=str(out), full_page=True, timeout=shot_timeout)
            except Exception as e:  # noqa: BLE001
                # После трёх десятков полностраничных скринов рендерер выдыхается.
                # Сообщаем наверх: там откроют свежую вкладку и продолжат с этой страницы.
                print(f"    [x] страница {n}: {str(e)[:60]} — нужна свежая вкладка")
                out.unlink(missing_ok=True)
                return False
            done.add(n)
            state[name] = {"pages": sorted(done), "url": page.url,
                           "ts": time.strftime("%Y-%m-%d %H:%M:%S")}
            STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), "utf-8")
            print(f"    [ok] страница {n}  ({first_cards(page)[:38]}…)")

        if not go_next(page, n + 1):
            print(f"    [i] страницы кончились на {n}")
            return True
        n += 1
    else:
        print(f"    [!] упёрся в предохранитель {max_pages} страниц")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Все страницы магазинов AliExpress")
    ap.add_argument("--tab", type=int, action="append", help="номер вкладки (можно повторять)")
    ap.add_argument("--profile", type=int, default=828976678, help="ID профиля, если браузер закрыт")
    ap.add_argument("--url", action="append", default=[],
                    help="ссылка на магазин (можно повторять); вкладка закроется после съёмки")
    ap.add_argument("--fresh", action="store_true",
                    help="снимать все страницы заново, не пропуская по сохранённому прогрессу")
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    ap.add_argument("--max-pages", type=int, default=60)
    ap.add_argument("--retries", type=int, default=10,
                    help="сколько раз открывать свежую вкладку, если рендерер устал")
    ap.add_argument("--shot-timeout", type=int, default=180,
                    help="секунд на один скрин (длинные страницы требуют больше)")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    def connect(p):
        """Прицепиться к живому браузеру, иначе поднять профиль самим.

        Браузер живёт, только пока с ним работает запустивший процесс, поэтому
        старт и вся работа должны быть в ОДНОМ процессе. Порт в netstat может
        ещё числиться, когда браузер уже погас — поэтому ошибку connect ловим.
        """
        # Прицепляемся только когда работаем по уже открытым вкладкам.
        # Если ссылки заданы явно — надёжнее поднять профиль самим.
        if not args.url:
            try:
                _, ws = find_cdp()
                b = p.chromium.connect_over_cdp(ws)
                if b.contexts and b.contexts[0].pages:
                    print("[ok] прицепился к уже открытому браузеру")
                    return b
                b.close()
            except Exception as e:  # noqa: BLE001
                print(f"[i] живого браузера нет ({type(e).__name__})")

        print(f"[..] поднимаю профиль {args.profile} …")
        from dolphin import DolphinLocal, start_with_retry
        api = DolphinLocal(port=DolphinLocal.discover() or 3001)
        auto = start_with_retry(api, args.profile)["automation"]
        print(f"[ok] профиль поднят, CDP {auto['port']}")
        return p.chromium.connect_over_cdp(f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}")

    state = json.loads(STATE.read_text("utf-8")) if STATE.exists() else {}
    args.out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = connect(p)
        ctx = browser.contexts[0]
        pages = [pg for pg in ctx.pages if pg.url.startswith("http")]
        print(f"[i] вкладок: {len(pages)} (новых не открываю)")

        if args.url:
            # Ссылки заданы явно: открываем по одной вкладке и закрываем после съёмки,
            # чтобы вкладки не плодились.
            for u in args.url:
                # Крупные магазины не снимаются за один заход: рендерер устаёт.
                # Тогда открываем свежую вкладку — уже снятые страницы пропускаются.
                for attempt in range(1, args.retries + 1):
                    pg = ctx.new_page()
                    done = False
                    try:
                        pg.goto(u, wait_until="domcontentloaded", timeout=90_000)
                        done = shoot_tab(pg, args.out, args.max_pages, state,
                                         args.fresh and attempt == 1, args.shot_timeout * 1000)
                    except Exception as e:  # noqa: BLE001
                        print(f"    [x] {e}")
                    finally:
                        pg.close()
                        print(f"    [i] вкладка закрыта (открыто: {len(ctx.pages)})")
                    if done:
                        break
                    if attempt < args.retries:
                        print(f"    [..] заход {attempt + 1}/{args.retries}: свежая вкладка")
        else:
            chosen = ([pages[i - 1] for i in args.tab if 0 < i <= len(pages)]
                      if args.tab else pages)
            for pg in chosen:
                try:
                    shoot_tab(pg, args.out, args.max_pages, state, args.fresh, args.shot_timeout * 1000)
                except Exception as e:  # noqa: BLE001 — одна вкладка не роняет остальные
                    print(f"    [x] {e}")

        browser.close()   # рвёт только CDP-соединение, вкладки остаются открытыми

    print(f"\n[готово] прогресс: {STATE.name}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n[i] остановлено, прогресс сохранён")
        sys.exit(130)
    except Exception as e:  # noqa: BLE001
        print(f"[x] {e}")
        sys.exit(1)
