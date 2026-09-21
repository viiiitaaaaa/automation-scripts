
import pandas as pd
import sys
import requests
from io import BytesIO
from PIL import Image as PILImage
import xlsxwriter

def main(input_xlsx, output_xlsx, image_col_candidates=("主图链接", "Ссылка на изображение"), link_col_candidates=("商品链接","Ссылка на товар")):
    df = pd.read_excel(input_xlsx, dtype=object)

    # Определяем колонки
    img_col = next((c for c in image_col_candidates if c in df.columns), None)
    if img_col is None:
        raise SystemExit(f"Не найдена колонка с изображениями среди: {image_col_candidates}")
    link_col = next((c for c in link_col_candidates if c in df.columns), None)

    with pd.ExcelWriter(output_xlsx, engine="xlsxwriter") as writer:
        export_df = df.copy()
        export_df.insert(0, "Картинка", "")
        export_df.to_excel(writer, index=False, sheet_name="Данные с картинками")

        ws = writer.sheets["Данные с картинками"]
        ws.set_column("A:A", 18)

        # немножко удобной ширины для первых столбцов
        for col_idx, w in {1:40, 2:40, 3:12, 4:16}.items():
            try:
                ws.set_column(col_idx, col_idx, w)
            except Exception:
                pass

        total = len(export_df)
        print(f"Всего строк: {total}")
        for i in range(total):
            row_idx = i + 1
            ws.set_row(row_idx, 105)

            # Кликабельная ссылка (если есть)
            if link_col is not None:
                link = df.iloc[i].get(link_col, "")
                if isinstance(link, str) and link.startswith("http"):
                    # cмещение на 1 столбец из-за добавленной колонки "Картинка"
                    ws.write_url(row_idx, df.columns.get_loc(link_col) + 1, link, string="Открыть 1688")

            img_url = df.iloc[i].get(img_col, None)
            if isinstance(img_url, str) and img_url.startswith("http"):
                try:
                    r = requests.get(img_url, timeout=15)
                    r.raise_for_status()
                    img_bytes = BytesIO(r.content)
                    # Уменьшаем превью для Excel
                    with PILImage.open(img_bytes) as im:
                        im.thumbnail((140, 140))
                        out_buf = BytesIO()
                        im.save(out_buf, format="PNG")
                        out_buf.seek(0)
                    # ВСТРАИВАЕМ из памяти: никаких временных файлов на диске
                    ws.insert_image(row_idx, 0, "preview.png", {'x_offset': 2, 'y_offset': 2, 'image_data': out_buf})
                except Exception as e:
                    ws.write(row_idx, 0, "нет изображения")
            else:
                ws.write(row_idx, 0, "нет изображения")

            if (i+1) % 10 == 0 or i == total - 1:
                print(f"Готово строк: {i+1}/{total}")

    print(f"Готово: {output_xlsx}")

if __name__ == "__main__":
    # Пример запуска:
    # py -3 вставить_картинки_в_эксель_FIX.py "Исходник_для_встраивания.xlsx" "Результат_с_картинками.xlsx"
    inp = sys.argv[1] if len(sys.argv) > 1 else "Исходник_для_встраивания.xlsx"
    out = sys.argv[2] if len(sys.argv) > 2 else "Результат_с_картинками.xlsx"
    main(inp, out)
