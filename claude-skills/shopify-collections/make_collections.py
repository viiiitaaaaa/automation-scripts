"""Завести коллекции магазина: восемь стилей плюс капсула по сценарию.

Коллекции автоматические — состав держится на тегах товара, поэтому новый товар
попадает в свою подборку сам. Handle обязан содержать слаг стиля: по нему тема
подхватывает цвет коллекции из decor-shell.css.
"""
from shop_api import gql

# handle, заголовок, тег-условие, шаблон, описание
COLLECTIONS = [
    ("neo-japandi", "Neo-Japandi", "style:neo-japandi", "category",
     "Stone, pale wood and unglazed ceramic in a muted grey-green register. Objects are "
     "left plain so the material and the light on it carry the room."),
    ("warm-minimalism", "Warm Minimalism", "style:warm-minimalism", "category",
     "Oat, cream and sand, with corners rounded rather than cut. Nothing here competes for "
     "attention — the pieces settle into a room and warm it."),
    ("organic-luxe", "Organic Luxe", "style:organic-luxe", "category",
     "Raw travertine, unfinished wood and clay, kept close to the state they came in. "
     "Surfaces are uneven on purpose, so light breaks across them instead of sliding off."),
    ("quiet-luxury", "Quiet Luxury", "style:quiet-luxury", "category",
     "Plain forms in single tones of grey and bone, without a logo or a flourish. The value "
     "sits in the stone and the weight of it in the hand."),
    ("sculptural", "Sculptural Contemporary", "style:sculptural", "category",
     "Pieces bought for their silhouette: asymmetric, carved, deliberately off-balance. Each "
     "one holds a shelf on its own and needs nothing beside it."),
    ("dark-academia", "Dark Academia", "style:dark-academia", "category",
     "Dark marble, bronze and deep wood tones, the palette of a study rather than a bathroom. "
     "Best in lamplight, against books and leather."),
    ("heritage-maximalism", "Heritage Maximalism", "style:heritage-maximalism", "category",
     "Brass, gilding and worked detail, where the ornament is the point. These pieces are "
     "made to be noticed and to sit among other things that are."),
    ("eclectic-collector", "Eclectic Collector", "style:eclectic-collector", "category",
     "Onyx, enamel and coloured stone gathered without a single rule. The collection reads "
     "as things picked up one at a time rather than bought as a set."),
    ("aroma-ritual-neo-japandi", "Aroma Ritual", "set:aroma-ritual", "capsule",
     "A small group for scent: diffuser, vessel and tray, meant to stand together on a shelf "
     "or the corner of a basin. Stone keeps the reeds upright and the oil out of the light."),
]

CREATE = """
mutation($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection { id handle title productsCount { count } }
    userErrors { field message }
  }
}
"""

EXISTING = {c["handle"] for c in
            gql("{ collections(first:100){ nodes{ handle } } }")["collections"]["nodes"]}

for handle, title, tag, tpl, body in COLLECTIONS:
    if handle in EXISTING:
        print(f"уже есть: {handle}")
        continue
    res = gql(CREATE, {"input": {
        "handle": handle,
        "title": title,
        "descriptionHtml": f"<p>{body}</p>",
        "templateSuffix": tpl,
        "ruleSet": {
            "appliedDisjunctively": False,   # все условия сразу, не «любое из»
            "rules": [{"column": "TAG", "relation": "EQUALS", "condition": tag}],
        },
    }})["collectionCreate"]
    if res["userErrors"]:
        print("ошибка:", handle, res["userErrors"])
    else:
        c = res["collection"]
        print(f"создана: {c['handle']:28} {c['title']:26} товаров {c['productsCount']['count']}")
