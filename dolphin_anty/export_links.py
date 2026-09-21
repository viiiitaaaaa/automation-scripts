# -*- coding: utf-8 -*-
"""Ссылки из xlsx -> текстовый файл (по одной в строке)."""
import sys
from openpyxl import load_workbook

src = sys.argv[1]
dst = sys.argv[2]
only_good = "--all" not in sys.argv

ws = load_workbook(src).active
links, skipped = [], 0
for r in ws.iter_rows(min_row=2, values_only=True):
    url, conf = r[2], r[4]
    if not (isinstance(url, str) and url.startswith("http")):
        skipped += 1
        continue
    links.append(url)
# дубликаты уберём, порядок сохраним
seen, uniq = set(), []
for u in links:
    if u not in seen:
        seen.add(u)
        uniq.append(u)
open(dst, "w", encoding="utf-8").write("\n".join(uniq))
print("строк в файле: %d, ссылок: %d, уникальных: %d, пропущено: %d"
      % (ws.max_row - 1, len(links), len(uniq), skipped))
