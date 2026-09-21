# -*- coding: utf-8 -*-
import json
rows = json.load(open("catalog.json", encoding="utf-8"))
USD = 3.606  # 1 USD = 3.606 PLN
lim = 75 * USD
print("Всего товаров:", len(rows), " лимит 75$ =", round(lim,2), "PLN")
st = {}
for r in rows: st[r["status"]] = st.get(r["status"],0)+1
print("статусы:", st)
le = [r for r in rows if r["max"] <= lim]
gt = [r for r in rows if r["max"] > lim]
print("до 75$ включительно (по макс. цене варианта):", len(le))
print("дороже 75$:", len(gt))
print("\nсамые дорогие 15:")
for r in sorted(rows, key=lambda x:-x["max"])[:15]:
    print(f"   {r['max']:8.2f} PLN = {r['max']/USD:6.2f}$  {r['title'][:55]}")
print("\nсамые дешёвые 5:")
for r in sorted(rows, key=lambda x:x["min"])[:5]:
    print(f"   {r['min']:8.2f} PLN = {r['min']/USD:6.2f}$  {r['title'][:55]}")
