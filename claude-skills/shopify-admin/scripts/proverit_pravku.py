"""Проверка массовой правки товаров: что РЕАЛЬНО лежит в Shopify, а не что сказал скрипт/ИИ.

Зачем: ИИ или скрипт отвечает «готово, изменил 250 товаров», а в магазине не поменялось ничего
(proecomdmitriy/1141, пост 182, 19.08.2026). После любой массовой правки — этот скрипт.

Вход — JSON «что должно получиться»:
  {"gid://shopify/Product/123": {"title": "...", "status": "ACTIVE", "tags_has": ["cat:skirt"],
                                 "productType": "...", "vendor": "...", "inventoryPolicy": "CONTINUE"}}
  (id можно писать и просто числом "123"). Поля — любые из списка FIELDS + tags_has / tags_not.
  inventoryPolicy проверяется у ВСЕХ вариантов товара.

Запуск:
  python proverit_pravku.py ozhidanie.json
  python proverit_pravku.py ozhidanie.json --out raskhozhdeniya.json

Итог: «совпало N из M», список расхождений; код выхода 0 — всё совпало, 1 — есть расхождения.
Писать «готово» пользователю — только после «совпало M из M».
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from shop_api import gql  # noqa: E402

FIELDS = ["title", "status", "productType", "vendor", "handle", "descriptionHtml"]

Q = """
query($ids: [ID!]!) {
  nodes(ids: $ids) {
    ... on Product {
      id title status productType vendor handle descriptionHtml tags
      variants(first: 100) { nodes { inventoryPolicy } }
    }
  }
}"""


def gid(x):
    x = str(x)
    return x if x.startswith("gid://") else f"gid://shopify/Product/{x}"


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    want = {gid(k): v for k, v in json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig")).items()}
    ids = list(want)
    got = {}
    for i in range(0, len(ids), 100):
        for n in gql(Q, {"ids": ids[i:i + 100]})["nodes"]:
            if n:
                got[n["id"]] = n

    bad = {}
    for pid, exp in want.items():
        cur = got.get(pid)
        if cur is None:
            bad[pid] = ["товара нет в магазине"]
            continue
        errs = []
        for f in FIELDS:
            if f in exp and cur.get(f) != exp[f]:
                errs.append(f"{f}: ждали {exp[f]!r}, в магазине {cur.get(f)!r}")
        for t in exp.get("tags_has", []):
            if t not in cur["tags"]:
                errs.append(f"нет тега {t!r}")
        for t in exp.get("tags_not", []):
            if t in cur["tags"]:
                errs.append(f"остался тег {t!r}")
        if "inventoryPolicy" in exp:
            pol = {v["inventoryPolicy"] for v in cur["variants"]["nodes"]}
            if pol != {exp["inventoryPolicy"]}:
                errs.append(f"inventoryPolicy вариантов: {sorted(pol)}")
        if errs:
            bad[pid] = errs

    ok = len(want) - len(bad)
    print(f"Совпало {ok} из {len(want)}")
    for pid, errs in list(bad.items())[:50]:
        print(f"  {pid}: " + "; ".join(errs))
    if len(bad) > 50:
        print(f"  … и ещё {len(bad) - 50}")
    if "--out" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--out") + 1])
        out.write_text(json.dumps(bad, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Расхождения: {out}")
    sys.exit(0 if not bad else 1)


if __name__ == "__main__":
    main()
