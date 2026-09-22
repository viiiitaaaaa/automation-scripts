"""
One-off 730-day bootstrap via the async collector (Semaphore(1), one
request in flight). Writes to the partitioned dataset and prints a short
summary. Usage:
    .venv/Scripts/python.exe run_trends_bootstrap.py "plaid skirt" ["chunky sweater" ...]
    .venv/Scripts/python.exe run_trends_bootstrap.py --youtube "plaid skirt" ...   # YouTube search
"""

import asyncio
import sys
from pathlib import Path

from src.collectors.google_trends_async import collect_keywords
from src.storage.google_trends_dataset import DATASET_ROOT, write_partitioned_dataset

YOUTUBE_ROOT = Path("data/normalized/google_trends_youtube")


def main():
    args = sys.argv[1:]
    youtube = "--youtube" in args
    keywords = [a for a in args if a != "--youtube"] or ["plaid skirt"]
    gprop, root = ("youtube", YOUTUBE_ROOT) if youtube else ("", DATASET_ROOT)

    df = asyncio.run(collect_keywords(keywords=keywords, geo="US", days=730, gprop=gprop))

    if df.empty:
        print("Нет данных — все keywords пропущены (см. ошибки выше).")
        return

    write_partitioned_dataset(df, root=root)

    for kw, g in df.groupby("keyword"):
        full = g[~g["is_partial"].astype(bool)]
        print(
            f"{kw}: {len(g)} точек ({len(full)} полных), "
            f"{g['date'].min().date()} .. {g['date'].max().date()}, "
            f"последнее значение {g['interest'].iloc[-1]}"
        )

    print(f"Записано в {root}/")


if __name__ == "__main__":
    main()
