"""Цвета товаров по спецификации/вариантам/названию. Поиск по границам слов,
чтобы Bluetooth не давал blue, а Reed diffuser — red."""
import html
import io
import json
import re
from collections import Counter

SRC = "p4.json"
MAX_COLORS = 3

PALETTE = [
    ("white",  ["white", "volakos", "crema", "ivory", "cream", "milky?", "snow",
                "arabescato", "calacatta", "carrara", "statuario", "alabaster"]),
    ("black",  ["black", "nero", "marquina", "charcoal", "graphite", "obsidian", "ink"]),
    ("grey",   ["grey", "gray", "silver", "smoke", "smoky", "ash", "pewter", "concrete", "chrome"]),
    ("beige",  ["beige", "travertine", "sand", "sandstone", "taupe", "nude", "oat", "linen",
                "champagne", "wheat", "apricot"]),
    ("brown",  ["brown", "walnut", "wood", "wooden", "oak", "coffee", "emperador", "bronze",
                "chocolate", "amber", "teak", "bamboo", "rosewood", "caramel"]),
    ("gold",   ["gold", "golden", "brass", "copper"]),
    ("green",  ["green", "emerald", "jade", "olive", "sage", "malachite", "cyan"]),
    ("blue",   ["blue", "navy", "azure", "teal", "indigo", "sapphire"]),
    ("pink",   ["pink", "rose", "blush", "peach", "coral", "cherry blossom"]),
    ("purple", ["purple", "violet", "lilac", "lavender"]),
    ("red",    ["red", "terracotta", "burgundy", "wine", "rust", "maroon", "scarlet"]),
    ("yellow", ["yellow", "mustard", "ochre", "lemon"]),
]

# Слова, внутри которых цвет — ложный: Bluetooth, Reed, Greenhouse не в счёт.
STOP = re.compile(r"(?i)\b(bluetooth|reed|redu\w+|goldfish)\b")

PATTERNS = [(name, re.compile(r"(?i)\b(?:" + "|".join(ws) + r")\b")) for name, ws in PALETTE]


def all_colors(text):
    t = STOP.sub(" ", (text or ""))
    found = []
    for name, rx in PATTERNS:
        m = rx.search(t)
        if m:
            found.append((m.start(), name))
    return [n for _, n in sorted(found)]


def spec_color(body):
    text = html.unescape(re.sub(r"<[^>]+>", "|", body or ""))
    parts = [s.strip() for s in text.split("|") if s.strip()]
    for i, s in enumerate(parts[:120]):
        if re.fullmatch(r"(?i)(colou?r|colou?r classification|pure color|main colou?r)", s):
            if i + 2 < len(parts) and parts[i + 1] == ":":
                return parts[i + 2]
    return None


products = json.load(io.open(SRC, encoding="utf-8"))["products"]
rows, stats, src_stats = [], Counter(), Counter()

for p in products:
    colors, source = [], None

    spec = spec_color(p.get("body_html"))
    if spec:
        colors, source = all_colors(spec), "спецификация"

    if not colors:
        seen = []
        for o in p["options"]:
            if "olor" not in o["name"].lower():
                continue
            for v in o["values"]:
                for c in all_colors(v):
                    if c not in seen:
                        seen.append(c)
        if seen:
            colors, source = seen, "варианты"

    if not colors:
        colors = all_colors(p["title"])
        source = "название" if colors else None

    if not colors:
        tags = " ".join(p["tags"])
        for tag, c, label in [("mat:marble", "white", "мрамор"),
                              ("mat:travertine", "beige", "травертин"),
                              ("mat:wood", "brown", "дерево"),
                              ("mat:onyx", "white", "оникс"),
                              ("mat:metal", "grey", "металл")]:
            if tag in tags:
                colors, source = [c], f"материал ({label})"
                break

    colors = colors[:MAX_COLORS]
    for c in colors:
        stats[c] += 1
    src_stats[source or "не определён"] += 1
    rows.append({"id": p["id"], "handle": p["handle"], "title": p["title"],
                 "colors": colors, "source": source})

json.dump(rows, io.open("colors.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print("товаров:", len(rows), "| без цвета:", sum(1 for r in rows if not r["colors"]))
print("\nцвета:", {k: v for k, v in stats.most_common()})
print("источник:", dict(src_stats))
print("\nбез цвета:")
for r in rows:
    if not r["colors"]:
        print("  -", r["title"][:66])
