"""Скачать много страниц параллельно — с лимитом одновременных запросов, таймаутом и повторами.

Рабочая версия шаблона из references/python/asyncio.md (раздел 5) по документации asyncio.ru/3.15
(python_tg/3996, пост 554). Для сборщиков: tg_monitor (страницы каналов), радар (подсказки, бренды),
1688/treg (карточки по списку ID), lead-engine (сайты компаний для досье).

Запуск:
    python async_fetch.py https://example.com https://example.org          # адреса в строке
    python async_fetch.py --file urls.txt --limit 5 --out result.json        # адреса из файла, по одному в строке
    python async_fetch.py --test                                             # самопроверка на локальном сервере

Из своего скрипта:
    import asyncio, sys; sys.path.insert(0, r"C:\\Users\\User\\.claude\\skills\\knowledge-library\\scripts")
    from async_fetch import fetch_all
    res = asyncio.run(fetch_all(urls, limit=5))   # [{"url","status","text","error","tries"}]

Правила (почему так):
- limit = Semaphore: не больше N запросов сразу — сайт не банит, Happ/VPN не захлёбывается.
- Повторы только на сетевых ошибках и 429/5xx, с паузой 1, 2, 4 с; 404 не повторяем.
- Одна сессия aiohttp на все запросы (через `async with`) — соединения закрываются сами.
- Одна упавшая страница не роняет остальные: ошибка пишется в её строку.
Для Taobao/1688 под её аккаунтом автосборы запрещены — этот скрипт только для разрешённых источников.
"""
import argparse
import asyncio
import json
import sys
import time

import aiohttp

RETRY_STATUS = {429, 500, 502, 503, 504}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140 Safari/537.36"


async def fetch_one(session, sem, url, retries=3, timeout=20):
    row = {"url": url, "status": None, "text": None, "error": None, "tries": 0}
    for attempt in range(retries + 1):
        row["tries"] = attempt + 1
        try:
            async with sem:  # не больше limit запросов одновременно
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as r:
                    row["status"] = r.status
                    if r.status in RETRY_STATUS and attempt < retries:
                        raise aiohttp.ClientResponseError(r.request_info, (), status=r.status)
                    row["text"] = await r.text(errors="replace")
                    row["error"] = None
                    return row
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            row["error"] = f"{type(e).__name__}: {e}"[:200]
            if attempt < retries:
                await asyncio.sleep(2 ** attempt)  # 1, 2, 4 с
    return row


async def fetch_all(urls, limit=5, retries=3, timeout=20, progress=True):
    sem = asyncio.Semaphore(limit)
    done = 0
    t0 = time.time()
    async with aiohttp.ClientSession(headers={"User-Agent": UA}) as session:
        async def wrapped(u):
            nonlocal done
            r = await fetch_one(session, sem, u, retries, timeout)
            done += 1
            if progress:
                print(f"  {done} из {len(urls)}  [{r['status'] or 'ошибка'}] {u}", file=sys.stderr)
            return r
        rows = await asyncio.gather(*(wrapped(u) for u in urls))
    if progress:
        print(f"Готово за {time.time() - t0:.1f} с", file=sys.stderr)
    return rows


def _selftest():
    """Локальный сервер: /ok — 200, /flaky — сначала 503, потом 200, /slow — 1 с, /404 — 404."""
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    hits = {"flaky": 0}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            if self.path == "/flaky":
                hits["flaky"] += 1
                code = 503 if hits["flaky"] == 1 else 200
            elif self.path == "/404":
                code = 404
            else:
                code = 200
            if self.path.startswith("/slow"):
                time.sleep(1)
            self.send_response(code)
            self.end_headers()
            self.wfile.write(f"page {self.path}".encode())

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_port}"
    urls = [f"{base}/ok"] + [f"{base}/slow{i}" for i in range(6)] + [f"{base}/flaky", f"{base}/404"]
    t0 = time.time()
    rows = asyncio.run(fetch_all(urls, limit=3, retries=2, timeout=5, progress=False))
    dt = time.time() - t0
    srv.shutdown()
    by = {r["url"].rsplit("/", 1)[1]: r for r in rows}
    checks = [
        ("все 9 адресов обработаны", len(rows) == 9),
        ("/ok = 200", by["ok"]["status"] == 200),
        ("/flaky: 503 → повтор → 200", by["flaky"]["status"] == 200 and by["flaky"]["tries"] == 2),
        ("/404 не повторяется", by["404"]["status"] == 404 and by["404"]["tries"] == 1),
        ("лимит 3: шесть медленных по 1 с ≈ 2 с, а не 6", 1.5 < dt < 4.5),
    ]
    ok = True
    for name, good in checks:
        print(("ОК   " if good else "СБОЙ ") + name)
        ok &= good
    print(f"время {dt:.1f} с — {'всё верно' if ok else 'есть сбои'}")
    return 0 if ok else 1


def main():
    p = argparse.ArgumentParser(description="Параллельное скачивание страниц с лимитом и повторами")
    p.add_argument("urls", nargs="*")
    p.add_argument("--file")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--timeout", type=int, default=20)
    p.add_argument("--out", help="сохранить JSON (url, status, text, error, tries)")
    p.add_argument("--test", action="store_true")
    a = p.parse_args()
    if a.test:
        return _selftest()
    urls = list(a.urls)
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            urls += [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
    if not urls:
        p.error("нет адресов")
    rows = asyncio.run(fetch_all(urls, a.limit, a.retries, a.timeout))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        print(f"Сохранено: {a.out}")
    else:
        for r in rows:
            print(r["status"], len(r["text"] or ""), "символов", r["url"], r["error"] or "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
