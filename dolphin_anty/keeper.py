"""Поднять профиль Dolphin и держать браузер живым.

Браузер гаснет вскоре после завершения запустившего его процесса, поэтому этот
скрипт остаётся работать в фоне. Адрес CDP пишется в cdp.json — другие скрипты
подключаются к нему, пока keeper жив.

    python keeper.py --profile 836461485 --hours 2
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from dolphin import DolphinLocal, start_with_retry

CDP_FILE = Path(__file__).with_name("cdp.json")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", type=int, default=836461485)
    ap.add_argument("--hours", type=float, default=2)
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8")
    api = DolphinLocal(port=DolphinLocal.discover() or 3001)
    print(f"[..] поднимаю профиль {args.profile}")
    auto = start_with_retry(api, args.profile)["automation"]

    CDP_FILE.write_text(json.dumps({
        "profile": args.profile,
        "port": auto["port"],
        "wsEndpoint": auto["wsEndpoint"],
        "url": f"ws://127.0.0.1:{auto['port']}{auto['wsEndpoint']}",
        "started": time.time(),
    }), encoding="utf-8")

    print(f"[ok] CDP на порту {auto['port']}, адрес записан в {CDP_FILE.name}")
    print(f"[i] держу браузер {args.hours} ч")
    try:
        time.sleep(args.hours * 3600)
    except KeyboardInterrupt:
        pass
    finally:
        CDP_FILE.unlink(missing_ok=True)
        api.stop(args.profile)
        print("[i] профиль погашен")
    return 0


if __name__ == "__main__":
    sys.exit(main())
