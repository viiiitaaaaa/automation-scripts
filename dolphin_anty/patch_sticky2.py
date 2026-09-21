"""Подставить явный assign product_form_id перед липкой кнопкой."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(__file__).parent / "theme_work" / "sections__main-product.liquid"
src = p.read_text(encoding="utf-8")

old = "{%- render 'sticky-atc', product: product, product_form_id: product_form_id -%}"
new = (
    "{%- assign sticky_form_id = 'product-form-' | append: section.id -%}\r\n"
    "{%- render 'sticky-atc', product: product, product_form_id: sticky_form_id -%}"
)

if "sticky_form_id" in src:
    print("уже поправлено")
    raise SystemExit
if src.count(old) != 1:
    print("строка не найдена, правка отменена")
    raise SystemExit(1)

p.write_text(src.replace(old, new), encoding="utf-8")
print("id формы вычисляется явно")
