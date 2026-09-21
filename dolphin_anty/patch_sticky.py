"""Подключить липкую кнопку покупки в секцию карточки товара (файл с CRLF)."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(__file__).parent / "theme_work" / "sections__main-product.liquid"
src = p.read_text(encoding="utf-8")

if "sticky-atc" in src:
    print("уже подключено")
    raise SystemExit

anchor = "</product-info>"
if src.count(anchor) != 1:
    print("якорь встречается раз:", src.count(anchor), "- правка отменена")
    raise SystemExit(1)

block = (
    anchor + "\r\n"
    "\r\n"
    "{%- comment -%} Липкая кнопка покупки на мобильном {%- endcomment -%}\r\n"
    "{%- render 'sticky-atc', product: product, product_form_id: product_form_id -%}"
)

p.write_text(src.replace(anchor, block), encoding="utf-8")
print("липкая кнопка подключена в", p.name)
