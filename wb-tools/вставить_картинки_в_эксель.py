
import pandas as pd
import os
import sys
import requests
from io import BytesIO
from PIL import Image as PILImage

import xlsxwriter

def main(input_xlsx, output_xlsx, image_col_candidates=("主图链接", "Ссылка на изображение"), link_col_candidates=("商品链接","Ссылка на товар")):
    # Читаем таблицу "как есть"
    df = pd.read_excel(input_xlsx, dtype=object)
    # Определяем колонку с картинками
    img_col = None
    for c in image_col_candidates:
        if c in df.columns:
            img_col = c
            break
    if img_col is None:
        raise SystemExit(f"Не найдена колонка с изображениями среди: {image_col_candidates}")
    # Определяем колонку со ссылкой на товар (необязательно)
    link_col = None
    for c in link_col_candidates:
        if c in df.columns:
            link_col = c
            break

    # Создаём выходной файл
    with pd.ExcelWriter(output_xlsx, engine="xlsxwriter") as writer:
        # Подготовим рабочий лист: добавим колонку "Картинка" в самое начало
        export_df = df.copy()
        export_df.insert(0, "Картинка", "")
        export_df.to_excel(writer, index=False, sheet_name="Данные с картинками")
        ws = writer.sheets["Данные с картинками"]

        # Настройки колонок
        ws.set_column("A:A", 18)
        # Подберём ширину для первых колонок, чтобы было удобнее
        width_map = {
            1: 40,  # Следующая после картинки колонка
            2: 40,
            3: 12,
            4: 16,
        }
        for col_idx, w in width_map.items():
            try:
                ws.set_column(col_idx, col_idx, w)
            except Exception:
                pass

        # Вставляем картинки построчно
        total = len(export_df)
        for i in range(total):
            row_idx = i + 1  # строки Excel после заголовка
            img_url = df.iloc[i].get(img_col, None)
            # Поднимем высоту строки под мини-превью
            ws.set_row(row_idx, 105)

            # Ссылка на товар (если есть)
            if link_col is not None:
                link = df.iloc[i].get(link_col, "")
                if isinstance(link, str) and link.startswith("http"):
                    ws.write_url(row_idx,  df.columns.get_loc(link_col) + 1, link, string="Открыть 1688")

            # Если URL корректный — пробуем скачать
            if isinstance(img_url, str) and img_url.startswith("http"):
                try:
                    r = requests.get(img_url, timeout=15)
                    r.raise_for_status()
                    img_bytes = BytesIO(r.content)
                    with PILImage.open(img_bytes) as im:
                        # Превью для Excel (~140px по большей стороне)
                        im.thumbnail((140, 140))
                        tmp_path = f"_tmp_img_{i}.png"
                        im.save(tmp_path, format="PNG")
                    # Вставляем в колонку A
                    ws.insert_image(row_idx, 0, tmp_path, {'x_offset': 2, 'y_offset': 2})
                    # Очистим временный файл
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                except Exception as e:
                    ws.write(row_idx, 0, "нет изображения")
            else:
                ws.write(row_idx, 0, "нет изображения")

    print(f"Готово: {output_xlsx}")

if __name__ == "__main__":
    # Использование:
    # python вставить_картинки_в_эксель.py "Исходник_для_встраивания.xlsx" "Результат_с_картинками.xlsx"
    inp = sys.argv[1] if len(sys.argv) > 1 else "Исходник_для_встраивания.xlsx"
    out = sys.argv[2] if len(sys.argv) > 2 else "Результат_с_картинками.xlsx"
    main(inp, out)
