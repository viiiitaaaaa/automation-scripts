"""Найти живой CDP-порт уже запущенного профиля и показать открытые вкладки."""
import re
import subprocess

import requests

out = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True).stdout
ports = sorted({int(m.group(1)) for m in
                (re.search(r"127\.0\.0\.1:(\d+)\s+.*LISTENING", ln) for ln in out.splitlines())
                if m})

found = None
for p in ports:
    try:
        r = requests.get(f"http://127.0.0.1:{p}/json/version", timeout=1)
        if r.status_code == 200 and "webSocketDebuggerUrl" in r.text:
            found = (p, r.json())
            break
    except Exception:
        pass

if not found:
    print(f"[x] CDP не найден (проверено портов: {len(ports)})")
    raise SystemExit(1)

port, ver = found
print(f"[ok] CDP порт {port} — {ver.get('Browser')}")
print(f"     ws: {ver.get('webSocketDebuggerUrl')}")

tabs = requests.get(f"http://127.0.0.1:{port}/json/list", timeout=5).json()
pages = [t for t in tabs if t.get("type") == "page"]
print(f"\nоткрыто вкладок: {len(pages)}")
for i, t in enumerate(pages, 1):
    print(f"{i:>3}. {t.get('title', '')[:60]}")
    print(f"     {t.get('url', '')[:120]}")
