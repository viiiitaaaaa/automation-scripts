"""Собрать чистые описания товаров вместо выгрузки спецификаций с AliExpress.

Из старого описания берём только факты (материал, отделка, размер), всё остальное —
бренды поставщика, «Origin: Mainland China», «High-concerned chemical» — выбрасываем.
"""
import html
import io
import json
import re

SRC = "p6.json"

# Пары абзацев на категорию: вариант выбирается по id, чтобы соседние карточки
# в сетке не читались одинаково.
COPY = {
    "cat:tray": (
        "A tray to gather the small things that otherwise drift across a surface — keys by the door, rings by the basin, a candle and a match.",
        "Cut from a single slab, this tray gives jewellery, perfume or a morning coffee a defined place to sit."),
    "cat:dispenser": (
        "A refillable dispenser that replaces supermarket plastic at the basin, so the everyday bottle stops interrupting the room.",
        "Decant hand wash or lotion once and the basin keeps a single material story instead of competing labels."),
    "cat:soap-dish": (
        "A soap dish with enough weight to stay put, keeping the bar dry between uses.",
        "Simple, heavy and easy to rinse — the bar sits above the water rather than in it."),
    "cat:toothbrush-holder": (
        "A holder that keeps brushes upright and off the counter, in the same material as the rest of the set.",
        "Upright storage for brushes and paste, sized to sit beside the basin without crowding it."),
    "cat:diffuser": (
        "A reed diffuser vessel that carries scent quietly, without a printed label on show.",
        "Fill with your own oil and reeds: the scent stays, the packaging disappears."),
    "cat:organizer": (
        "An organiser for cotton buds, pads and the small things a bathroom accumulates.",
        "Keeps daily clutter contained and closed, so the counter reads calm."),
    "cat:tissue-box": (
        "A cover that hides the printed carton and lets tissues become part of the room.",
        "Weighted enough to stay in place when a tissue is drawn — no chasing it across the table."),
    "cat:cup": (
        "A cup for brushes, combs or a rinse at the basin, in a material that ages well with water.",
        "Substantial in the hand and stable on a wet surface."),
    "cat:figurine": (
        "A sculptural piece for a shelf, console or cabinet — quiet enough to live with, distinct enough to notice.",
        "An object that gives a shelf its focal point without asking for the whole room."),
    "cat:stand": (
        "A raised stand that lifts fruit, pastries or objects clear of the table and gives them presence.",
        "Height turns everyday things into a small still life on the table."),
    "cat:bowl": (
        "A bowl for fruit, keys or nothing at all — the form carries the surface on its own.",
        "Deep enough to hold, sculptural enough to leave empty."),
    "cat:clock": (
        "A silent sweeping movement, so the piece marks time without ticking through a quiet room.",
        "A desk clock that reads as an object first and an instrument second."),
    "cat:rug": (
        "Soft underfoot and quick to dry, with a non-slip backing for the bathroom floor.",
        "Absorbent pile that takes the chill off tiles straight out of the shower."),
    "cat:box": (
        "A lidded box for jewellery and small valuables, weighty enough to feel considered.",
        "Closed storage that looks intentional left out on a dresser."),
    "cat:vase": (
        "A vessel for a single stem or a dried arrangement — the shape holds up empty, too.",
        "Narrow enough for one stem, sculptural enough to stand alone between seasons."),
    "cat:mirror": (
        "A mirror framed to sit as an object rather than disappear into the wall.",
        "Clear glass in a frame that carries the same materials as the rest of the room."),
    "cat:ashtray": (
        "A weighted ashtray that stays where it is put, indoors or on a terrace table.",
        "Deep enough to contain ash, heavy enough for open air."),
    "cat:shelf": (
        "Wall-mounted storage that keeps the floor clear and puts everyday things within reach.",
        "A shelf for towels, plants or books, fixed where the room needs the surface."),
    "cat:holder": (
        "A wall-mounted holder that keeps towels or paper off the counter.",
        "Fixed storage that frees the surface below it."),
    "cat:toilet-brush": (
        "A brush and holder that close away the least decorative object in the room.",
        "Concealed storage for a necessary thing, in the same material as the set."),
    "cat:candle-holder": (
        "A holder that gives a candle a base solid enough for open flame.",
        "Stone weight under a taper — stable on a mantel or a dining table."),
    "cat:shower": (
        "A complete shower set: overhead rainfall, handheld and mixer, in one finish.",
        "Rainfall above, handheld below, matched hardware throughout."),
    "cat:lamp": (
        "Warm, low light for a bedside or hallway, shaded by stone rather than fabric.",
        "A wall light that reads as a sculpture when it is switched off."),
    "cat:curtain": (
        "A shower curtain and rod that separate wet and dry without building a wall.",
        "Wall-mounted and foldable, for bathrooms where every centimetre counts."),
    "cat:faucet": (
        "A basin mixer with a tall spout, sized for vessel basins.",
        "Waterfall flow and a matched finish for the rest of the fittings."),
    "cat:hook": (
        "Adhesive wall hooks that hold without drilling and leave no trace when moved.",
        "Storage for a rented bathroom: no tools, no holes."),
    "cat:decor": (
        "A decorative object with enough presence to anchor a shelf on its own.",
        "Sculptural, quiet, and easy to place among books or ceramics."),
    "cat:mirror_default": ("", ""),
}

SET_INTRO = (
    "A full vanity set in one stone: dispenser, dish, holder and tray, so the basin stops looking like an accumulation of separate purchases.",
    "Everything the basin needs, cut from the same block — soap, brushes, cotton buds and scent, each with its own vessel.")

# Товары, которые категорией не описываются: тексты для них написаны отдельно.
SPECIAL = {
    "16088163516796": "A wireless speaker housed in a wooden cabinet — music in a kitchen, study or bedroom without a black plastic box on the shelf.",
    "16088090509692": "Preserved moss and fern under glass, framed to stand on a shelf or hang on a wall. No watering and no daylight required.",
    "16088090378620": "A seated Buddha lit from behind by an LED halo ring, dimmable through six levels — meditative light for a hallway console or a quiet corner.",
    "16085651980668": "A long-pile faux fur throw for the end of a bed, a bench or a reading chair.",
    "16085651915132": "Four unfinished wood slices for table settings, candle groupings and centrepieces.",
}

SET_COPY = ("Sold as a coordinated set, so the counter reads as one material rather than a collection of leftovers.",
            "Every piece is cut from the same stone, which keeps the vanity consistent from dispenser to tray.")

MATERIAL_NOTE = {
    "mat:marble": "Natural marble: every piece carries its own veining, so no two are identical.",
    "mat:travertine": "Natural travertine, with the open pores and warm tone typical of the stone.",
    "mat:onyx": "Natural onyx, translucent at the edges where the light catches it.",
    "mat:stone": "Natural stone, with variation in tone and pattern from piece to piece.",
    "mat:wood": "Solid wood, with grain that shifts from piece to piece.",
    "mat:metal": "Metal construction with a stable, wipe-clean finish.",
    "mat:ceramic": "Glazed ceramic, easy to rinse and slow to stain.",
    "mat:glass": "Clear glass, best cleaned with a soft cloth.",
    "mat:resin": "Cast resin, lighter than stone and warm to the touch.",
    "mat:textile": "Soft textile with a non-slip backing.",
    "mat:enamel": "Hand-finished enamel over metal.",
    "mat:fur": "Long-pile faux fur, soft underfoot.",
    "mat:alabaster": "Natural alabaster, pale and softly translucent.",
}

CARE = {
    "mat:marble": "Wipe with a damp cloth; avoid acidic cleaners, which etch stone.",
    "mat:travertine": "Wipe with a damp cloth; avoid acidic cleaners, which etch stone.",
    "mat:onyx": "Wipe with a damp cloth; avoid acidic cleaners, which etch stone.",
    "mat:stone": "Wipe with a damp cloth; avoid acidic cleaners.",
    "mat:wood": "Wipe dry after contact with water; do not soak.",
    "mat:textile": "Machine wash cool, dry flat.",
    "mat:fur": "Machine wash cool, dry flat.",
}

COLOUR_NAME = {
    "color:white": "white", "color:black": "black", "color:grey": "grey",
    "color:beige": "beige", "color:brown": "brown", "color:green": "green",
    "color:blue": "blue", "color:pink": "pink", "color:gold": "gold",
    "color:red": "red", "color:yellow": "yellow", "color:purple": "purple",
}

# Поля спецификации, которые имеет смысл сохранить
KEEP = {"material": "Material", "finish type": "Finish", "size": "Size",
        "type": "Type", "use": "Use", "material type": "Material"}
DROP_VALUES = re.compile(r"(?i)(mainland china|none|no\b|yes\b|other)")


def spec_pairs(body):
    text = html.unescape(re.sub(r"<[^>]+>", "|", body or ""))
    parts = [s.strip() for s in text.split("|") if s.strip()]
    out = {}
    for i, s in enumerate(parts[:80]):
        key = s.lower()
        if key in KEEP and i + 2 < len(parts) and parts[i + 1] == ":":
            val = parts[i + 2].strip()
            if val and not DROP_VALUES.fullmatch(val) and len(val) < 60:
                out.setdefault(KEEP[key], val)
    return out


def dimensions(text):
    m = re.search(r"\b\d{1,3}\s?[x×*]\s?\d{1,3}(\s?[x×*]\s?\d{1,3})?\s?(cm|mm)\b", text, re.I)
    if m:
        return m.group(0)
    m = re.search(r"\b\d{2,4}\s?ml\b", text, re.I)
    return m.group(0) if m else None


def build(p, new_title):
    tags = p["tags"]
    cats = [t for t in tags if t.startswith("cat:")]
    mats = [t for t in tags if t.startswith("mat:")]
    cols = [t for t in tags if t.startswith("color:")]
    pid = int(p["id"])

    is_set = len(cats) >= 3

    if str(pid) in SPECIAL:
        intro = SPECIAL[str(pid)]
    elif is_set:
        # у набора первая категория по алфавиту случайна — описываем набор целиком
        intro = SET_INTRO[pid % 2]
    else:
        pair = COPY.get(cats[0] if cats else "cat:decor") or COPY["cat:decor"]
        intro = pair[pid % 2]

    parts = [f"<p>{intro}</p>"]

    # второй «наборный» абзац нужен только там, где вводный был про один предмет
    if is_set and str(pid) in SPECIAL:
        parts.append(f"<p>{SET_COPY[pid % 2]}</p>")

    note = MATERIAL_NOTE.get(mats[0]) if mats else None
    if note:
        parts.append(f"<p>{note}</p>")

    details = []
    specs = spec_pairs(p.get("body_html"))
    if specs.get("Material"):
        details.append(f"Material: {specs['Material']}")
    elif mats:
        details.append("Material: " + mats[0].split(":")[1].replace("-", " ").title())
    if specs.get("Finish"):
        details.append(f"Finish: {specs['Finish']}")
    if cols:
        details.append("Colour: " + ", ".join(COLOUR_NAME.get(c, "") for c in cols).strip(", "))
    dim = specs.get("Size") or dimensions(p["title"] + " " + (p.get("body_html") or "")[:2000])
    if dim:
        details.append(f"Size: {dim}")
    if len(p["variants"]) > 1:
        details.append(f"Options: {len(p['variants'])} to choose from")

    if details:
        parts.append("<ul>" + "".join(f"<li>{d}</li>" for d in details) + "</ul>")

    care = CARE.get(mats[0]) if mats else None
    if care:
        parts.append(f"<p><strong>Care.</strong> {care}</p>")

    return "".join(parts)


products = json.load(io.open(SRC, encoding="utf-8"))["products"]
titles = json.load(io.open("titles_manual.json", encoding="utf-8"))
rows = [{"id": p["id"], "title": titles.get(str(i), p["title"]), "body": build(p, titles.get(str(i)))}
        for i, p in enumerate(products)]

json.dump(rows, io.open("bodies.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("описаний:", len(rows))
print("средняя длина:", sum(len(r["body"]) for r in rows) // len(rows), "символов")
print("\nпример 1 —", rows[9]["title"], "\n", rows[9]["body"][:600])
print("\nпример 2 —", rows[82]["title"], "\n", rows[82]["body"][:600])
print("\nпример 3 —", rows[0]["title"], "\n", rows[0]["body"][:600])
