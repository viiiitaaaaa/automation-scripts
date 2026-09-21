#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wildberries Ratings Updater (Windows CMD friendly)

Как запустить (в командной строке / CMD):
  1) Установите зависимости (один раз):
       pip install pandas requests openpyxl
  2) Запустите скрипт, указав входной файл:
       python wb_ratings.py --input "C:\Путь\к\файлу.xlsx"
     (необязательно) Укажите выходной файл:
       python wb_ratings.py --input "in.xlsx" --output "out.xlsx"

Если файл — CSV:
       python wb_ratings.py --input "файл.csv"

Результат: Excel с колонками
  - wb_link    — ссылка на карточку WB
  - rating     — текущий рейтинг (0–5)
  - feedbacks  — количество отзывов
  - updated_at — дата/время обновления
"""

import argparse
import math
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import requests


# -------- Настройки по умолчанию --------
BATCH_SIZE = 80           # сколько артикулов запрашивать за раз
TIMEOUT = 20              # таймаут HTTP, сек
RETRIES = 3               # число повторов при ошибках/429
BACKOFF = 2.0             # множитель экспоненциальной паузы между ретраями
SLEEP_BETWEEN = 0.4       # пауза между батчами, сек
USER_AGENT = "Mozilla/5.0 (RatingsBot)"


def log(msg: str) -> None:
    print(msg, flush=True)


def find_header_row(raw: pd.DataFrame) -> Optional[int]:
    """
    Ищем строку, где встречается ячейка с 'Артикул' (без учёта регистра).
    Возвращаем индекс строки-«шапки» или None.
    """
    for i in range(min(200, len(raw))):
        row = raw.iloc[i].astype(str).str.strip().str.lower()
        if row.eq("артикул").any() or row.eq("article").any():
            return i
    return None


def make_unique(headers: List[str]) -> List[str]:
    """
    Делает имена столбцов уникальными: если встречаются дубли — добавляет суффиксы __2, __3, ...
    """
    seen = {}
    out = []
    for h in headers:
        base = h or "Unnamed"
        if base not in seen:
            seen[base] = 1
            out.append(base)
        else:
            seen[base] += 1
            out.append(f"{base}__{seen[base]}")
    return out


def is_numeric_like(s: str) -> bool:
    s = str(s).strip()
    if not s or s.lower() in ("nan", "none"):
        return False
    if s.isdigit():
        return 6 <= len(s) <= 12
    # float-like "25990554.0"
    try:
        f = float(s.replace(",", "."))
        return f.is_integer() and 6 <= len(str(int(f))) <= 12
    except Exception:
        return False


def pick_article_column(df: pd.DataFrame) -> str:
    """
    Выбираем колонку с артикулами (nmId). Сначала ищем 'Артикул' (включая дубликаты),
    далее — любую колонку, где больше всего похожих на nmId значений.
    """
    # точные названия
    exact = [c for c in df.columns if str(c).strip().lower() in ("артикул", "article", "nmid", "nm", "sku", "id")]
    if exact:
        # среди кандидатов выберем ту, где больше всех чисел нужного формата
        best = max(exact, key=lambda c: sum(is_numeric_like(x) for x in df[c].values))
        return best

    # иначе — просканируем все колонки
    best_col = None
    best_score = -1
    for c in df.columns:
        score = sum(is_numeric_like(x) for x in df[c].values)
        if score > best_score:
            best_score = score
            best_col = c
    if best_col is None:
        raise RuntimeError("Не удалось определить колонку с артикулами")
    return best_col


def normalize_article(val) -> Optional[str]:
    if pd.isna(val):
        return None
    s = str(val).strip()
    if not s:
        return None
    if s.isdigit():
        return s
    # float-like
    try:
        f = float(s.replace(",", "."))
        if f.is_integer():
            return str(int(f))
    except Exception:
        pass
    # оставить только цифры
    digits = re.sub(r"\D+", "", s)
    return digits or None


def chunked(seq: List[str], size: int) -> List[List[str]]:
    return [seq[i:i + size] for i in range(0, len(seq), size)]


def fetch_wb_batch(batch: List[str]) -> Dict[str, Dict[str, Optional[float]]]:
    """
    Запрашиваем карточки WB для пачки nmId и возвращаем:
      { nmId: {"rating": float|None, "feedbacks": int|None } }
    """
    url = "https://card.wb.ru/cards/v1/detail"
    params = {
        "appType": "1",
        "curr": "rub",
        # несколько направлений, чтобы увеличить шанс нахождения товара
        "dest": "-1257786,-1069100,-1029256,-1255563",
        "spp": "0",
        "nm": ";".join(batch),
    }
    headers = {"User-Agent": USER_AGENT}

    last_err = None
    for attempt in range(1, RETRIES + 1):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
            if r.status_code == 429:
                time.sleep(BACKOFF ** attempt)
                continue
            r.raise_for_status()
            data = r.json()
            out = {}
            for p in data.get("data", {}).get("products", []):
                nm_id = str(p.get("id") or p.get("nmId") or "")
                rating = p.get("rating")
                if rating is None:
                    rating = p.get("feedbackRating")
                feedbacks = p.get("feedbacks")
                out[nm_id] = {
                    "rating": float(rating) if rating is not None else None,
                    "feedbacks": int(feedbacks) if feedbacks is not None else None,
                }
            return out
        except Exception as e:
            last_err = e
            if attempt == RETRIES:
                raise
            time.sleep(BACKOFF ** attempt)
    if last_err:
        raise last_err
    return {}


def build_dataframe(src: Path) -> pd.DataFrame:
    """
    Читает исходный файл (XLSX/CSV), приводит его к чистой таблице и возвращает DataFrame.
    Пытается найти строку заголовков с 'Артикул'.
    """
    log(f"[1/5] Чтение файла: {src}")
    if not src.exists():
        raise FileNotFoundError(f"Файл не найден: {src}")

    if src.suffix.lower() in [".xlsx", ".xls"]:
        raw = pd.read_excel(src, header=None, dtype=object)
    else:
        # CSV читаем обычным способом (ожидаем нормальные заголовки)
        return pd.read_csv(src)

    # Найдём строку-«шапку»
    hdr_idx = find_header_row(raw)
    if hdr_idx is not None:
        headers = raw.iloc[hdr_idx].astype(str).tolist()
        headers = [h.strip() for h in headers]
        headers = make_unique(headers)
        df = raw.iloc[hdr_idx + 1:].copy()
        df.columns = headers
        # удалить полностью пустые строки
        df = df.dropna(how="all")
    else:
        # fallback: пусть первая строка — это заголовок
        df = pd.read_excel(src)

    return df


def run(input_path: Path, output_path: Optional[Path]) -> Path:
    df = build_dataframe(input_path)

    # выбираем корректную колонку с nmId
    art_col = pick_article_column(df)
    log(f"[2/5] Колонка с артикулами: '{art_col}'")

    # нормализуем артикулы
    df["article_norm"] = [normalize_article(v) for v in df[art_col].values]
    articles = [a for a in df["article_norm"] if a]

    if not articles:
        raise RuntimeError("Не найдено ни одного артикула (nmId) после нормализации.")

    # формируем ссылку
    df["wb_link"] = [f"https://www.wildberries.ru/catalog/{a}/detail.aspx" if a else None for a in df["article_norm"]]

    # собираем рейтинги
    log(f"[3/5] Запрос рейтингов: всего артикулов {len(articles)}")
    results: Dict[str, Dict[str, Optional[float]]] = {}

    for idx, batch in enumerate(chunked(list(dict.fromkeys(articles)), BATCH_SIZE), start=1):
        log(f"   - батч {idx}: {len(batch)} шт.")
        try:
            res = fetch_wb_batch(batch)
            results.update(res)
        except Exception as e:
            log(f"     ! ошибка на батче: {e}")
            for a in batch:
                results.setdefault(a, {"rating": None, "feedbacks": None})
        time.sleep(SLEEP_BETWEEN)

    # маппинг результатов обратно в таблицу
    log("[4/5] Заполнение таблицы")
    df["rating"] = [results.get(str(a), {}).get("rating") if a else None for a in df["article_norm"]]
    df["feedbacks"] = [results.get(str(a), {}).get("feedbacks") if a else None for a in df["article_norm"]]
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").round(2)
    df["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # сохраняем
    if output_path is None:
        # имя на основе входного
        stem = input_path.stem
        if not stem.endswith("_with_ratings"):
            stem = stem + "_with_ratings"
        output_path = input_path.with_name(stem + ".xlsx")

    log(f"[5/5] Сохранение результата: {output_path}")
    df.to_excel(output_path, index=False)
    log("Готово.")

    return output_path


def main():
    parser = argparse.ArgumentParser(description="Подтянуть рейтинг/отзывы Wildberries к артикулам из Excel/CSV.")
    parser.add_argument("--input", "-i", required=True, help="Путь к входному файлу (.xlsx/.xls/.csv)")
    parser.add_argument("--output", "-o", required=False, help="Путь к выходному .xlsx (необязательно)")

    args = parser.parse_args()
    input_path = Path(args.input).expanduser()
    output_path = Path(args.output).expanduser() if args.output else None

    try:
        run(input_path, output_path)
    except Exception as e:
        log(f"ОШИБКА: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
