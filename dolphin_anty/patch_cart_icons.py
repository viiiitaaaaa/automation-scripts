"""Вставить значки платёжных систем в подвал корзины (файл с CRLF)."""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(__file__).parent / "theme_work" / "sections__main-cart-footer.liquid"
src = p.read_text(encoding="utf-8")

anchor = '<div id="cart-errors"></div>'
if "cart__payment-icons" in src:
    print("уже вставлено")
    raise SystemExit

block = (
    "{%- comment -%}\r\n"
    "          Значки платёжных систем: берутся из подключённых к магазину\r\n"
    "          способов оплаты. Свои картинки не грузим - это чужие знаки.\r\n"
    "        {%- endcomment -%}\r\n"
    "        {%- if shop.enabled_payment_types.size > 0 -%}\r\n"
    '          <div class="cart__payment-icons">\r\n'
    '            <ul class="list-unstyled list-payment" role="list">\r\n'
    "              {%- for type in shop.enabled_payment_types -%}\r\n"
    '                <li class="list-payment__item">\r\n'
    "                  {{ type | payment_type_svg_tag: class: 'icon icon--full-color' }}\r\n"
    "                </li>\r\n"
    "              {%- endfor -%}\r\n"
    "            </ul>\r\n"
    "          </div>\r\n"
    "        {%- endif -%}\r\n"
    "\r\n"
    "        " + anchor
)

if src.count(anchor) != 1:
    print("якорь встречается раз:", src.count(anchor), "- правка отменена")
    raise SystemExit(1)

p.write_text(src.replace(anchor, block), encoding="utf-8")
print("значки карт вставлены в", p.name)
