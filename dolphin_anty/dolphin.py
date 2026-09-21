"""
Dolphin{anty} -> открыть профиль и вкладку через автоматизацию (CDP).

Как это работает (по офиц. докам docs.dolphin-anty-cdn.com):
  1. Local API живёт на http://localhost:3001 (порт может съехать, если занят —
     смотри в приложении Settings -> Health). Доступен только с этой же машины,
     только пока запущено десктоп-приложение Dolphin{anty} и юзер залогинен.
  2. POST /v1.0/browser_profiles/{id}/start  с {"automation": true}
     -> {"success": true, "automation": {"port": 12345, "wsEndpoint": "/devtools/browser/..."}}
  3. Цепляемся к этому порту по CDP (Selenium / Playwright) и рулим браузером.
  4. GET /v1.0/browser_profiles/{id}/stop — гасим профиль и синкаем датадир.

Важно: automation=true недоступна на Free-плане (Local API вернёт 402).

Установка:
    pip install requests selenium
    # опционально, если хочешь --engine playwright:
    pip install playwright

Примеры:
    python dolphin.py --check
    python dolphin.py --token ВАШ_JWT --list
    python dolphin.py --profile 123456 --url https://whoer.net
    python dolphin.py --profile 123456 --url https://google.com --engine playwright --stop
"""

from __future__ import annotations

import argparse
import json
import sys
import time

import requests

REMOTE_API = "https://dolphin-anty-api.com"
DEFAULT_LOCAL_PORTS = (3001, 3002, 3003, 3004, 3005)


# --------------------------------------------------------------------------- #
# Local API
# --------------------------------------------------------------------------- #
class DolphinLocal:
    def __init__(self, port: int = 3001, token: str | None = None, timeout: int = 120):
        self.base = f"http://localhost:{port}"
        self.timeout = timeout
        self.s = requests.Session()
        if token:
            self.s.headers["Authorization"] = f"Bearer {token}"

    # --- служебное ---------------------------------------------------------
    @staticmethod
    def discover(ports=DEFAULT_LOCAL_PORTS) -> int | None:
        """Найти порт, на котором реально висит Local API."""
        for p in ports:
            try:
                r = requests.get(f"http://localhost:{p}/v1.0/browser_profiles/1/stop", timeout=2)
                # любой валидный HTTP-ответ = сервис живой
                if r.status_code < 600:
                    return p
            except requests.RequestException:
                continue
        return None

    def login_with_token(self, token: str) -> dict:
        """Сохранить JWT внутри Local API (нужно не всегда, но не мешает)."""
        r = self.s.post(
            f"{self.base}/v1.0/auth/login-with-token",
            json={"token": token},
            timeout=30,
        )
        return _json(r)

    # --- старт/стоп --------------------------------------------------------
    def start(self, profile_id: int, automation: bool = True, headless: bool = False,
              no_tabs: bool = False, password: str | None = None) -> dict:
        payload: dict = {"automation": automation}
        if headless:
            payload["headless"] = True
        if no_tabs:
            payload["noTabs"] = True
        if password:
            payload["browserProfilePassword"] = password

        r = self.s.post(
            f"{self.base}/v1.0/browser_profiles/{profile_id}/start",
            json=payload,
            timeout=self.timeout,
        )
        data = _json(r)

        if r.status_code == 402:
            raise RuntimeError("402: автоматизация недоступна на Free-плане Dolphin{anty}.")
        if r.status_code == 499:
            raise RuntimeError("499: на Free-плане уже запущено 3 профиля.")
        if r.status_code == 429:
            raise RuntimeError("429: слишком много одновременных запусков браузера.")
        if not data.get("success"):
            raise RuntimeError(f"Не удалось стартовать профиль: HTTP {r.status_code} {data}")
        return data

    def start_temporary(self, automation: bool = True, headless: bool = False) -> dict:
        """Временный профиль — не требует ID, создаётся на лету."""
        payload: dict = {"automation": automation}
        if headless:
            payload["headless"] = True
        r = self.s.post(
            f"{self.base}/v1.0/browser_profiles/start",
            json=payload,
            timeout=self.timeout,
        )
        data = _json(r)
        if not data.get("success"):
            raise RuntimeError(f"Не удалось стартовать временный профиль: HTTP {r.status_code} {data}")
        return data

    def stop(self, profile_id: int) -> dict:
        r = self.s.get(
            f"{self.base}/v1.0/browser_profiles/{profile_id}/stop",
            timeout=self.timeout,
        )
        return _json(r)


def start_with_retry(api: "DolphinLocal", profile_id: int, tries: int = 6, pause: int = 10,
                     no_tabs: bool = False) -> dict:
    """Стартовать профиль с automation, разруливая залипшее 'already running'.

    no_tabs=True — не восстанавливать сохранённые вкладки профиля: браузер
    поднимается пустым, вкладки не копятся и система не грузится.
    """
    import time as _t

    # Обе ошибки временные: пометка "running" снимается не сразу после stop,
    # а порт автоматизации Dolphin выдаёт не мгновенно после перезапуска.
    # Сюда же 502/503/504 — это таймауты на серверах самого Dolphin, они проходят.
    RETRYABLE = ("already running", "Failed to get port and socket",
                 "status code 502", "status code 503", "status code 504")

    def retryable(err: Exception) -> bool:
        return any(s in str(err) for s in RETRYABLE)

    try:
        return api.start(profile_id, automation=True, no_tabs=no_tabs)
    except RuntimeError as e:
        if not retryable(e):
            raise
        if "already running" in str(e):
            print("[..] профиль уже запущен, останавливаю …")
            api.stop(profile_id)

    for attempt in range(1, tries + 1):
        _t.sleep(pause)
        try:
            return api.start(profile_id, automation=True, no_tabs=no_tabs)
        except RuntimeError as e:
            if not retryable(e):
                raise
            print(f"[..] попытка {attempt}/{tries}: {str(e)[:60]} …")
    raise RuntimeError("Local API продолжает считать профиль запущенным — "
                       "закрой окно профиля вручную в приложении Dolphin{anty}.")


# --------------------------------------------------------------------------- #
# Remote API (список профилей) — нужен JWT с dolphin-anty.com/panel
# --------------------------------------------------------------------------- #
def list_profiles(token: str, limit: int = 50) -> list[dict]:
    r = requests.get(
        f"{REMOTE_API}/browser_profiles",
        headers={"Authorization": f"Bearer {token}"},
        params={"limit": limit},
        timeout=30,
    )
    data = _json(r)
    if r.status_code != 200:
        raise RuntimeError(f"Remote API HTTP {r.status_code}: {data}")
    return data.get("data", [])


# --------------------------------------------------------------------------- #
# Драйверы
# --------------------------------------------------------------------------- #
def open_tab_selenium(cdp_port: int, url: str, keep_open: bool):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    opts = Options()
    opts.add_experimental_option("debuggerAddress", f"127.0.0.1:{cdp_port}")
    driver = webdriver.Chrome(options=opts)   # нужен chromedriver под версию Anty-браузера

    driver.switch_to.new_window("tab")        # новая вкладка
    driver.get(url)
    time.sleep(2)
    print(f"[ok] вкладка открыта: {driver.title!r} — {driver.current_url}")

    if not keep_open:
        driver.quit()                          # только отцепляемся, браузер живёт


def open_tab_playwright(ws_endpoint: str, url: str, keep_open: bool):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_endpoint)
        ctx = browser.contexts[0] if browser.contexts else browser.new_context()
        page = ctx.new_page()
        page.goto(url, wait_until="domcontentloaded")
        print(f"[ok] вкладка открыта: {page.title()!r} — {page.url}")
        if keep_open:
            time.sleep(3)
        browser.close()   # рвёт только CDP-соединение


# --------------------------------------------------------------------------- #
def _json(r: requests.Response) -> dict:
    try:
        return r.json()
    except json.JSONDecodeError:
        return {"raw": r.text[:500], "status": r.status_code}


def main() -> int:
    ap = argparse.ArgumentParser(description="Открыть вкладку в профиле Dolphin{anty}")
    ap.add_argument("--profile", type=int, help="ID профиля Dolphin{anty}")
    ap.add_argument("--temp", action="store_true", help="временный профиль (без ID)")
    ap.add_argument("--url", default="https://whoer.net", help="какой URL открыть")
    ap.add_argument("--token", help="JWT с dolphin-anty.com/panel (нужен для --list)")
    ap.add_argument("--port", type=int, help="порт Local API (по умолчанию — автопоиск 3001+)")
    ap.add_argument("--engine", choices=("selenium", "playwright"), default="selenium")
    ap.add_argument("--headless", action="store_true")
    ap.add_argument("--stop", action="store_true", help="погасить профиль после работы")
    ap.add_argument("--keep-open", action="store_true", help="не отцепляться сразу")
    ap.add_argument("--no-automation", action="store_true",
                    help="просто запустить профиль без CDP (работает на Free-плане)")
    ap.add_argument("--check", action="store_true", help="только проверить, доступен ли Local API")
    ap.add_argument("--list", action="store_true", help="показать профили (нужен --token)")
    args = ap.parse_args()

    port = args.port or DolphinLocal.discover()
    if port is None:
        print("[x] Local API не отвечает на 3001-3005.\n"
              "    Проверь: приложение Dolphin{anty} запущено и ты в нём залогинен.\n"
              "    Фактический порт: в приложении Settings -> Health.")
        return 1
    print(f"[ok] Local API найден: http://localhost:{port}")

    if args.check:
        return 0

    api = DolphinLocal(port=port, token=args.token)
    if args.token:
        api.login_with_token(args.token)

    if args.list:
        if not args.token:
            print("[x] --list требует --token")
            return 1
        for p in list_profiles(args.token):
            print(f"  {p.get('id'):>10}  {p.get('name')}")
        return 0

    # --stop без --url/--engine = просто погасить профиль и выйти
    if args.stop and args.profile and args.no_automation:
        print(f"[ok] stop -> {api.stop(args.profile)}")
        return 0

    if not args.profile and not args.temp:
        print("[x] укажи --profile ID, --temp (временный профиль) или --list")
        return 1

    if args.temp:
        print("[..] стартую временный профиль c automation=true …")
        data = api.start_temporary(automation=True, headless=args.headless)
        args.profile = data.get("profileId")
        print(f"[ok] временный профиль id={args.profile}")
    else:
        auto_flag = not args.no_automation
        print(f"[..] стартую профиль {args.profile} (automation={auto_flag}) …")
        data = api.start(args.profile, automation=auto_flag, headless=args.headless)
        if args.no_automation:
            print("[ok] профиль запущен. CDP выключен — вкладками из Python рулить нельзя.")
            return 0
    auto = data.get("automation") or {}
    cdp_port, ws = auto.get("port"), auto.get("wsEndpoint")
    if not cdp_port:
        raise RuntimeError(f"В ответе нет automation.port: {data}")
    print(f"[ok] профиль поднят, CDP порт {cdp_port}, ws {ws}")

    try:
        if args.engine == "playwright":
            open_tab_playwright(f"ws://127.0.0.1:{cdp_port}{ws}", args.url, args.keep_open)
        else:
            open_tab_selenium(cdp_port, args.url, args.keep_open)
    finally:
        if args.stop:
            print("[..] гашу профиль …")
            print(f"[ok] stop -> {api.stop(args.profile)}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:  # noqa: BLE001
        print(f"[x] {e}")
        sys.exit(1)
