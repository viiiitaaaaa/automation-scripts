r"""Безубыточный ROAS (BER), маржа до/после рекламы и реальный ROAS по дням.

Уроки из новостей (akuliabuhta/1065, 1063, 1048, 1047, 1042, 1043 — отмечены 07.10):
  * BER = цена ÷ (цена − товар − доставка − комиссии) — при таком ROAS заказ в ноль. У опытных 1,4–1,7.
  * Маржа ДО рекламы ≥ 65%, иначе поднимать цену.
  * ДРР (реклама ÷ выручка) ≤ 30% = ROAS ≥ 3,3; ДРР 70% — работа в ноль.
  * ROAS кабинета Google/Meta врёт (трекер ловит не всё) — считать реальный: выручка Shopify ÷ расход.

Режимы:
  python roas_calc.py ber --price 65 --cost 9 --ship 7.5 [--duty 0.3] [--fee-pct 2.9 --fee-fix 0.30
                          --returns 5 --chargebacks 1 --tax 6 --apps 1]
      Одна вещь: маржа до рекламы, BER, потолок цены покупателя (CAC) и вердикт по правилу 65%.

  python roas_calc.py real [--csv real_roas.csv] [--shopify]
      Реальный ROAS по дням. CSV (UTF-8): date,revenue,google,meta  (revenue можно оставить пустым —
      с флагом --shopify выручка дня берётся из Admin API нового магазина 2e0bv7-jn, только чтение).
      Расход вносится вручную из кабинетов. Выводит ROAS, ДРР и сравнение с BER (--ber, по умолч. 1,6).

Данные: 🟡 только на ПК (выручка и расходы магазина) — CSV никуда не отправлять.
"""
import argparse
import csv
import sys
from pathlib import Path

HERE = Path(__file__).parent
DEFAULT_CSV = Path(r"C:\Users\User\store3\real_roas.csv")


def ber(a):
    goods = a.cost * (1 + a.duty)          # закупка + пошлина США
    fees = a.price * (a.fee_pct + a.returns + a.chargebacks + a.tax) / 100 + a.fee_fix + a.apps
    left = a.price - goods - a.ship - fees  # остаётся до рекламы = потолок CAC
    margin = left / a.price * 100
    print(f"Цена ${a.price:.2f} | товар+пошлина ${goods:.2f} | доставка ${a.ship:.2f} | комиссии ${fees:.2f}")
    print(f"До рекламы остаётся ${left:.2f}  (маржа до рекламы {margin:.0f}%)")
    if left <= 0:
        print("❌ Убыток ещё до рекламы — цену поднимать или товар не брать.")
        return
    b = a.price / left
    print(f"Безубыточный ROAS (BER) = {b:.2f}   (у опытных 1,4–1,7)")
    print(f"Потолок цены покупателя (CAC) = ${left:.2f}; при ROAS 3,3 (ДРР 30%) реклама ${a.price/3.3:.2f}, "
          f"чистыми ${left - a.price/3.3:.2f}")
    if margin < 65:
        need = (goods + a.ship + a.fee_fix + a.apps) / (1 - 0.65 - (a.fee_pct + a.returns + a.chargebacks + a.tax) / 100)
        print(f"⚠ Маржа до рекламы < 65% — правило: поднять цену. Для 65% нужна цена ≈ ${need:.2f}")
    else:
        print("✅ Маржа до рекламы ≥ 65% — норма.")


def shopify_revenue(day):
    sys.path.insert(0, r"C:\Users\User\store3")
    from shop3_api import gql  # noqa: E402
    q = """query($q:String!,$after:String){orders(first:100,after:$after,query:$q){
      pageInfo{hasNextPage endCursor} nodes{currentTotalPriceSet{shopMoney{amount}}}}}"""
    total, after = 0.0, None
    while True:
        d = gql(q, {"q": f"created_at:>={day}T00:00:00 created_at:<={day}T23:59:59 -status:cancelled",
                    "after": after})["orders"]
        total += sum(float(n["currentTotalPriceSet"]["shopMoney"]["amount"]) for n in d["nodes"])
        if not d["pageInfo"]["hasNextPage"]:
            return total
        after = d["pageInfo"]["endCursor"]


def real(a):
    p = Path(a.csv)
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("date,revenue,google,meta\n", encoding="utf-8")
        print(f"Создан пустой {p} — вносить по строке в день: дата, выручка (или пусто + --shopify), расход Google, Meta.")
        return
    rows = list(csv.DictReader(p.open(encoding="utf-8-sig")))
    tot_r = tot_s = 0.0
    print(f"{'дата':<11}{'выручка':>10}{'реклама':>10}{'ROAS':>7}{'ДРР':>6}  вердикт")
    for r in rows:
        rev = r.get("revenue", "").strip()
        rev = float(rev) if rev else (shopify_revenue(r["date"]) if a.shopify else 0.0)
        spend = sum(float(r.get(k) or 0) for k in ("google", "meta"))
        tot_r, tot_s = tot_r + rev, tot_s + spend
        roas = rev / spend if spend else 0
        drr = spend / rev * 100 if rev else 0
        v = "нет расхода" if not spend else ("✅ прибыль" if roas >= 3.3 else ("в плюс" if roas > a.ber else "❌ ниже BER"))
        print(f"{r['date']:<11}{rev:>10.2f}{spend:>10.2f}{roas:>7.2f}{drr:>5.0f}%  {v}")
    if tot_s:
        print(f"Итого: ROAS {tot_r/tot_s:.2f}, ДРР {tot_s/tot_r*100 if tot_r else 0:.0f}% (цель ≤30%), BER {a.ber}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    b = sub.add_parser("ber")
    b.add_argument("--price", type=float, required=True)
    b.add_argument("--cost", type=float, required=True, help="закупка в $ (с комиссией посредника)")
    b.add_argument("--ship", type=float, required=True, help="доставка до двери в США, $")
    b.add_argument("--duty", type=float, default=0.30, help="пошлина США доля от закупки (0.30)")
    b.add_argument("--fee-pct", type=float, default=2.9)
    b.add_argument("--fee-fix", type=float, default=0.30)
    b.add_argument("--returns", type=float, default=5)
    b.add_argument("--chargebacks", type=float, default=1)
    b.add_argument("--tax", type=float, default=6, help="налог с выручки, %%")
    b.add_argument("--apps", type=float, default=1)
    r = sub.add_parser("real")
    r.add_argument("--csv", default=str(DEFAULT_CSV))
    r.add_argument("--shopify", action="store_true")
    r.add_argument("--ber", type=float, default=1.6)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    ber(a) if a.mode == "ber" else real(a)


if __name__ == "__main__":
    main()
