"""Собрать главную страницу магазина: секции и тексты.

Пишет templates/index.json и добавляет announcement bar в header-group.json.
Картинку hero хозяйка ставит сама — здесь только текст и кнопки.
"""
import io
import json

THEME = r"C:\Users\User\decor-store-theme"

# ---------------------------------------------------------------- announcement
hg_path = THEME + r"\sections\header-group.json"
hg = json.load(io.open(hg_path, encoding="utf-8-sig"))
hg["sections"]["announcement-bar"] = {
    "type": "announcement-bar",
    "blocks": {
        "shipping": {"type": "announcement", "settings": {
            "text": "Free shipping to the UK, Europe and the US",
            "link": "", "text_alignment": "center"}},
        "stone": {"type": "announcement", "settings": {
            "text": "Natural marble, travertine and onyx — no two pieces alike",
            "link": "", "text_alignment": "center"}},
    },
    "block_order": ["shipping", "stone"],
    "settings": {
        "color_scheme": "scheme-3",
        "show_line_separator": False,
        "auto_rotate": True,
        "change_slides_speed": 6,
        "show_social": False,
        "enable_country_selector": False,
        "enable_language_selector": False,
    },
}
hg["order"] = ["announcement-bar", "header"]
io.open(hg_path, "w", encoding="utf-8").write(json.dumps(hg, ensure_ascii=False, indent=2) + "\n")

# ---------------------------------------------------------------------- главная
FAQ = [
    ("How long does delivery take?",
     "<p>Orders are dispatched within two working days. Delivery takes 7–14 working days to "
     "the UK and Europe, 10–18 to the United States. You get a tracking number as soon as the "
     "parcel leaves the warehouse.</p>"),
    ("Is shipping really free?",
     "<p>Yes — to the United Kingdom, the European Union and the United States, with no minimum "
     "order. The price you see on the product page is the price at checkout.</p>"),
    ("Every piece looks slightly different in the photos. Why?",
     "<p>Because marble, travertine and onyx are cut from natural blocks. Veining, tone and the "
     "pattern of the pores change from piece to piece, and the one you receive will not be an "
     "exact copy of the photograph.</p>"),
    ("How do I look after natural stone?",
     "<p>Wipe with a damp cloth and dry it. Avoid acidic cleaners, limescale removers and "
     "bleach: they etch polished stone and leave dull marks that cannot be buffed out.</p>"),
    ("Can I return an order?",
     "<p>Yes, within 14 days of delivery, provided the piece is unused and in its original "
     "packaging. Write to us and we will send return instructions.</p>"),
]

index = {
    "sections": {
        "image_banner": {
            "type": "image-banner",
            "blocks": {
                "heading": {"type": "heading", "settings": {
                    "heading": "Stone, cut for the everyday",
                    "heading_size": "h0"}},
                "text": {"type": "text", "settings": {
                    "text": "Marble, travertine and onyx for the basin, the table and the shelf.",
                    "text_style": "body"}},
                "buttons": {"type": "buttons", "settings": {
                    "button_label_1": "Shop all", "button_link_1": "shopify://collections/all",
                    "button_style_secondary_1": False,
                    "button_label_2": "Shop by style", "button_link_2": "shopify://collections/neo-japandi",
                    "button_style_secondary_2": True}},
            },
            "block_order": ["heading", "text", "buttons"],
            "settings": {
                "image_overlay_opacity": 40, "image_height": "large",
                "desktop_content_position": "middle-center", "show_text_box": False,
                "image_behavior": "none", "desktop_content_alignment": "center",
                "color_scheme": "scheme-3", "mobile_content_alignment": "center",
                "stack_images_on_mobile": False, "show_text_below": False,
            },
        },
        "featured_neo": {
            "type": "featured-collection",
            "settings": {
                "title": "Neo-Japandi", "heading_size": "h2",
                "description": "", "show_description": False, "description_style": "body",
                "collection": "neo-japandi", "products_to_show": 4, "columns_desktop": 4,
                "color_scheme": "scheme-1", "full_width": False, "show_view_all": True,
                "view_all_style": "link", "enable_desktop_slider": False, "swipe_on_mobile": False,
                "image_ratio": "square", "image_shape": "default", "show_secondary_image": True,
                "show_vendor": False, "show_rating": False, "quick_add": "none",
                "columns_mobile": "2", "padding_top": 48, "padding_bottom": 16,
            },
        },
        "featured_sculptural": {
            "type": "featured-collection",
            "settings": {
                "title": "Sculptural Contemporary", "heading_size": "h2",
                "description": "", "show_description": False, "description_style": "body",
                "collection": "sculptural", "products_to_show": 4, "columns_desktop": 4,
                "color_scheme": "scheme-1", "full_width": False, "show_view_all": True,
                "view_all_style": "link", "enable_desktop_slider": False, "swipe_on_mobile": False,
                "image_ratio": "square", "image_shape": "default", "show_secondary_image": True,
                "show_vendor": False, "show_rating": False, "quick_add": "none",
                "columns_mobile": "2", "padding_top": 16, "padding_bottom": 16,
            },
        },
        "collection_list": {
            "type": "collection-list",
            "blocks": {
                f"col_{i}": {"type": "featured_collection", "settings": {"collection": h}}
                for i, h in enumerate([
                    "neo-japandi", "warm-minimalism", "organic-luxe", "quiet-luxury",
                    "sculptural", "dark-academia", "heritage-maximalism", "eclectic-collector"])
            },
            "block_order": [f"col_{i}" for i in range(8)],
            "settings": {
                "title": "Shop by style", "heading_size": "h2", "image_ratio": "square",
                "columns_desktop": 4, "color_scheme": "scheme-1", "show_view_all": False,
                "swipe_on_mobile": True, "columns_mobile": "2",
                "padding_top": 48, "padding_bottom": 48,
            },
        },
        "about": {
            "type": "image-with-text",
            "blocks": {
                "heading": {"type": "heading", "settings": {
                    "heading": "Cut, not moulded", "heading_size": "h2"}},
                "text": {"type": "text", "settings": {
                    "text": "<p>Every piece here is cut from a natural block — Volakos, Emperador, "
                            "Nero Marquina, travertine, onyx. The veining is not printed and not "
                            "repeated: the tray on your basin will not match the photograph exactly, "
                            "and that is the point of buying stone rather than a copy of it.</p>",
                    "text_style": "body"}},
                "button": {"type": "button", "settings": {
                    "button_label": "See the collections",
                    "button_link": "shopify://collections/neo-japandi"}},
            },
            "block_order": ["heading", "text", "button"],
            "settings": {
                "height": "adapt", "desktop_image_width": "medium", "layout": "image_first",
                "desktop_content_position": "middle", "desktop_content_alignment": "left",
                "content_layout": "no-overlap", "color_scheme": "scheme-2",
                "mobile_content_alignment": "left", "padding_top": 40, "padding_bottom": 40,
            },
        },
        "faq": {
            "type": "collapsible-content",
            "blocks": {
                f"q{i}": {"type": "collapsible_row", "settings": {"heading": q, "row_content": a}}
                for i, (q, a) in enumerate(FAQ)
            },
            "block_order": [f"q{i}" for i in range(len(FAQ))],
            "settings": {
                "caption": "", "heading": "Before you order", "heading_size": "h2",
                "heading_alignment": "left", "layout": "row", "color_scheme": "scheme-1",
                "container_color_scheme": "scheme-2", "open_first_collapsible_row": False,
                "image_ratio": "adapt", "desktop_layout": "image_second",
                "padding_top": 48, "padding_bottom": 48,
            },
        },
        "newsletter": {
            "type": "newsletter",
            "blocks": {
                "heading": {"type": "heading", "settings": {
                    "heading": "New stone, first", "heading_size": "h2"}},
                "paragraph": {"type": "paragraph", "settings": {
                    "text": "<p>One letter when a new cut arrives. No weekly mailing.</p>"}},
                "email_form": {"type": "email_form", "settings": {}},
            },
            "block_order": ["heading", "paragraph", "email_form"],
            "settings": {"color_scheme": "scheme-2", "full_width": True,
                         "padding_top": 48, "padding_bottom": 48},
        },
    },
    "order": ["image_banner", "featured_neo", "featured_sculptural", "collection_list",
              "about", "faq", "newsletter"],
}

io.open(THEME + r"\templates\index.json", "w", encoding="utf-8").write(
    json.dumps(index, ensure_ascii=False, indent=2) + "\n")
print("секции главной:", index["order"])
print("announcement:", hg["order"])
