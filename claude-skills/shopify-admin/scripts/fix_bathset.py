"""Разложить товары с тегом cat:bath-set по предметным категориям.

Варианты таких товаров — это и есть отдельные предметы («Soap dispenser A»,
«Tray C», «Cotton swab jar-B»), поэтому категории берём из значений вариантов
и из названия, а общий cat:bath-set убираем: с ним товар не попадал ни в одну
вкладку каталога.
"""
import io
import json
import re
import time
from collections import Counter

from shop_api import gql

# порядок важен: более узкие формулировки должны проверяться раньше общих
RULES = [
    ("cat:dispenser",    [r"soap dispenser", r"lotion bottle", r"dispenser", r"shower gel",
                          r"shampoo", r"pump bottle", r"sub-?pack"]),
    ("cat:soap-dish",    [r"soap dish", r"soap holder", r"soap tray"]),
    ("cat:diffuser",     [r"reed diffuser", r"aromatherapy", r"diffuser"]),
    ("cat:toothbrush-holder", [r"toothbrush holder", r"toothbrush"]),
    ("cat:tissue-box",   [r"tissue box", r"tissue can", r"napkin box"]),
    ("cat:organizer",    [r"cotton swab", r"cotton swabs", r"swab jar", r"swab can",
                          r"storage jar", r"organizer", r"jar"]),
    ("cat:tray",         [r"tray", r"plate"]),
    ("cat:cup",          [r"\bcup\b", r"goblet", r"tumbler", r"mouthwash"]),
    ("cat:toilet-brush", [r"toilet brush", r"toilet cleaning"]),
    ("cat:box",          [r"\bbox\b", r"container"]),
    ("cat:holder",       [r"holder", r"stand"]),
]

Q = """
query($cursor: String) {
  products(first: 50, after: $cursor, query: "tag:'cat:bath-set'") {
    pageInfo { hasNextPage endCursor }
    nodes {
      id title tags
      options { name optionValues { name } }
    }
  }
}
"""

M_ADD = "mutation($id: ID!, $tags: [String!]!) { tagsAdd(id: $id, tags: $tags) { userErrors { message } } }"
M_DEL = "mutation($id: ID!, $tags: [String!]!) { tagsRemove(id: $id, tags: $tags) { userErrors { message } } }"


def categories(text):
    t = text.lower()
    found = []
    for cat, pats in RULES:
        if any(re.search(p, t) for p in pats):
            found.append(cat)
    return found


items, cursor = [], None
while True:
    d = gql(Q, {"cursor": cursor})["products"]
    items += d["nodes"]
    if not d["pageInfo"]["hasNextPage"]:
        break
    cursor = d["pageInfo"]["endCursor"]

print("товаров с cat:bath-set:", len(items))

stats, report = Counter(), []
for i, p in enumerate(items, 1):
    variants = " ; ".join(v["name"] for o in p["options"] for v in o["optionValues"])
    cats = categories(variants) or categories(p["title"])
    # если предмет так и не опознан — пусть остаётся organizer, а не пустота
    if not cats:
        cats = ["cat:organizer"]
    cats = cats[:4]
    existing = [t for t in p["tags"] if t.startswith("cat:") and t != "cat:bath-set"]
    to_add = [c for c in cats if c not in existing]

    if to_add:
        gql(M_ADD, {"id": p["id"], "tags": to_add})
    gql(M_DEL, {"id": p["id"], "tags": ["cat:bath-set"]})

    for c in cats:
        stats[c] += 1
    report.append({"title": p["title"][:60], "added": to_add, "had": existing})
    if i % 10 == 0:
        print(f"  {i}/{len(items)}")
    time.sleep(0.25)

json.dump(report, io.open("bathset_report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\nпроставлено категорий:")
for k, v in stats.most_common():
    print(f"  {k:26} {v}")
