# -*- coding: utf-8 -*-
"""Список товаров дороже 75$ по стартовой цене. Только список, ничего не удаляет."""
import json
rows = json.load(open("catalog.json", encoding="utf-8"))
USD = 3.606
LIM = 75 * USD
kill = sorted([r for r in rows if r["min"] > LIM], key=lambda x: -x["min"])
keep = [r for r in rows if r["min"] <= LIM]
json.dump(kill, open("to_delete.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"порог: 75$ = {LIM:.2f} PLN")
print(f"ОСТАЁТСЯ: {len(keep)}")
print(f"УДАЛЯЕТСЯ: {len(kill)}\n")
print("Самые дорогие 10 из удаляемых:")
for r in kill[:10]:
    print(f"   {r['min']/USD:7.2f}$  {r['title'][:60]}")
print("\nБлижайшие к порогу (только-только не прошли):")
for r in kill[-8:]:
    print(f"   {r['min']/USD:7.2f}$  {r['title'][:60]}")
print("\nСамые дорогие из ОСТАЮЩИХСЯ (стартовая цена, но верхняя может быть выше):")
for r in sorted(keep, key=lambda x:-x["max"])[:5]:
    print(f"   от {r['min']/USD:6.2f}$ до {r['max']/USD:7.2f}$  {r['title'][:50]}")
