#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WB Ratings Updater — FIXED (пробует несколько эндпойнтов, устойчив к 404)

Запуск из CMD (Windows):
  1) Установите зависимости (один раз):
       pip install pandas requests openpyxl
  2) Запустите:
       python wb_ratings_fix.py --input "C:\WB\input.xlsx"

Скрипт создаст файл C:\WB\input_with_ratings.xlsx с колонками:
  wb_link, rating, feedbacks, updated_at
"""

import argparse
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd
import requests

BATCH_SIZE = 80
TIMEOUT = 20
RETRIES = 3
BACKOFF = 2.0
SLEEP_BETWEEN = 0.4
USER_AGENT = "Mozilla/5.0 (RatingsBot)"

CARD_ENDPOINTS = [
    "https://card.wb.ru/cards/detail",
    "https://card.wb.ru/cards/v2/detail",
    "https://card.wb.ru/cards/v1/detail",
]

DESTS = [
    "-1257786,-1069100,-1029256,-1255563",
    "-1257786",
]

def log(msg: str) -> None:
    print(msg, flush=True)

def is_numeric_like(s: str) -> bool:
    s = str(s).strip()
    if not s or s.lower() in ("nan", "none"):
        return False
    if s.isdigit():
        return 6 <= len(s) <= 12
    try:
        f = float(s.replace(",", "."))
        return f.is_integer() and 6 <= len(str(int(f))) <= 12
    except Exception:
        return False

def normalize_article(val) -> Optional[str]:
    if pd.isna(val):
        return None
    s = str(val).strip()
    if not s:
        return None
    if s.isdigit():
        return s
    try:
        f = float(s.replace(",", "."))
        if f.is_integer():
            return str(int(f))
    except Exception:
        pass
    digits = re.sub(r"\D+", "", s)
    return digits or None

def find_header_row(raw: pd.DataFrame) -> Optional[int]:
    for i in range(min(200, len(raw))):
        row = raw.iloc[i].astype(str).str.strip().str.lower()
        if row.eq("артикул").any() or row.eq("article").any():
            return i
    return None

def build_dataframe(src: Path) -> pd.DataFrame:
    if src.suffix.lower() in [".xlsx", ".xls"]:
        raw = pd.read_excel(src, header=None, dtype=object)
        hdr = find_header_row(raw)
        if hdr is not None:
            headers = raw.iloc[hdr].astype(str).tolist()
            # уникализируем имена
            seen = {}
            cols = []
            for h in headers:
                h = h.strip()
                if h not in seen:
                    seen[h] = 1
                    cols.append(h)
                else:
                    seen[h] += 1
                    cols.append(f"{h}__{seen[h]}")
            df = raw.iloc[hdr+1:].copy()
            df.columns = cols
            df = df.dropna(how="all")
            return df
        else:
            return pd.read_excel(src)
    else:
        return pd.read_csv(src)

def pick_article_column(df: pd.DataFrame) -> str:
    exact = [c for c in df.columns if str(c).strip().lower() in ("артикул", "article", "nmid", "nm", "sku", "id")]
    if exact:
        return max(exact, key=lambda c: sum(is_numeric_like(v) for v in df[c].values))
    best, best_score = None, -1
    for c in df.columns:
        score = sum(is_numeric_like(v) for v in df[c].values)
        if score > best_score:
            best, best_score = c, score
    if best is None:
        raise RuntimeError("Не нашёл колонку с артикулами")
    return best

def extract_rating_fields(p: dict):
    for k in ("rating", "feedbackRating", "reviewRating"):
        v = p.get(k)
        if v is not None:
            try:
                return float(v)
            except Exception:
                pass
    return None

def fetch_batch_any_endpoint(nm_list: List[str]) -> Dict[str, Dict[str, Optional[float]]]:
    headers = {"User-Agent": USER_AGENT}
    last_exc = None
    for base in CARD_ENDPOINTS:
        for dest in DESTS:
            params = {
                "appType": "1",
                "curr": "rub",
                "dest": dest,
                "spp": "0",
                "nm": ";".join(nm_list),
            }
            for attempt in range(1, RETRIES+1):
                try:
                    r = requests.get(base, params=params, headers=headers, timeout=TIMEOUT)
                    if r.status_code == 429:
                        time.sleep(BACKOFF ** attempt)
                        continue
                    r.raise_for_status()
                    data = r.json()
                    out = {}
                    for p in data.get("data", {}).get("products", []):
                        nm_id = str(p.get("id") or p.get("nmId") or "")
                        rating = extract_rating_fields(p)
                        feedbacks = p.get("feedbacks")
                        out[nm_id] = {
                            "rating": rating if rating is not None else None,
                            "feedbacks": int(feedbacks) if feedbacks is not None else None,
                        }
                    return out
                except Exception as e:
                    last_exc = e
                    if attempt == RETRIES:
                        break
                    time.sleep(BACKOFF ** attempt)
    if last_exc:
        print(f"     ! все эндпойнты дали ошибку: {last_exc}")
    return {}

def chunked(seq, n):
    return [seq[i:i+n] for i in range(0, len(seq), n)]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", "-i", required=True)
    ap.add_argument("--output", "-o")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.exists():
        print(f"ОШИБКА: файл не найден — {src}")
        raise SystemExit(1)

    print(f"[1/4] Читаю файл: {src}")
    df = build_dataframe(src)

    art_col = pick_article_column(df)
    print(f"[2/4] Нашёл колонку с артикулами: {art_col}")

    df["article_norm"] = [normalize_article(v) for v in df[art_col].values]
    df["wb_link"] = [f"https://www.wildberries.ru/catalog/{a}/detail.aspx" if a else None for a in df["article_norm"]]
    nmids = [a for a in df["article_norm"] if a]

    print(f"[3/4] Тяну рейтинги: всего {len(nmids)}")
    results: Dict[str, Dict[str, Optional[float]]] = {}
    unique_nm = list(dict.fromkeys(nmids))
    for idx, batch in enumerate(chunked(unique_nm, BATCH_SIZE), start=1):
        print(f"   - батч {idx}: {len(batch)} шт.")
        res = fetch_batch_any_endpoint(batch)
        if not res:
            for a in batch:
                res[a] = {"rating": None, "feedbacks": None}
        results.update(res)
        time.sleep(SLEEP_BETWEEN)

    print("[4/4] Заполняю таблицу и сохраняю")
    df["rating"] = [results.get(str(a), {}).get("rating") if a else None for a in df["article_norm"]]
    df["feedbacks"] = [results.get(str(a), {}).get("feedbacks") if a else None for a in df["article_norm"]]
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").round(2)
    df["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    out = Path(args.output) if args.output else src.with_name(src.stem + "_with_ratings.xlsx")
    df.to_excel(out, index=False)
    print(f"Готово: {out}")

if __name__ == "__main__":
    main()
