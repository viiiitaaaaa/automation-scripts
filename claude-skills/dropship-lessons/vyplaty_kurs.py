# -*- coding: utf-8 -*-
"""Скрытая потеря на конвертации выплат (proecomdmitriy/1207, пост 914, 06.10.2026).

Комиссию сервиса видно в выписке, а потерю на КУРСЕ — нет. Скрипт сравнивает сервисы выплат
(Payoneer, Airwallex, Wise, банк) на одном и том же переводе и считает, сколько денег уходит
в месяц и в год из-за худшего курса.

Как пользоваться (ничего не отправляет наружу, всё считается на компьютере):
    python vyplaty_kurs.py --oborot 5000 --perevodov 4 \
        --servis "Payoneer:7.95:0" --servis "Airwallex:7.87:0" --servis "Wise:7.83:0.6"

--oborot      выплаты из Shopify в месяц, $
--perevodov   сколько переводов в месяц (для фиксированной платы)
--servis      "имя:курс:комиссия" — курс = сколько единиц валюты ПЛАТИТ сервис-источник за $1
              по выписке ИЛИ сколько $ уходит за 1 единицу валюты, главное — одинаково для всех;
              комиссия — % от суммы перевода (0, если её нет)
--napravlenie "prodaem" (по умолчанию: продаём $ и получаем валюту — чем БОЛЬШЕ курс, тем лучше)
              или "pokupaem" (платим $ за валюту, например HKD/CNY поставщику — чем МЕНЬШЕ курс, тем лучше)
--fiks        фиксированная плата за перевод, $ (общая для всех, если нужна)

В примере автора: $331 000 за полгода, Payoneer 7,95 HKD за $1 против 7,87 у Airwallex ≈ 1% ≈ $6 000 в год.
Проверка: --oborot 55000 --perevodov 5 --napravlenie pokupaem --servis "Payoneer:7.95:0" --servis "Airwallex:7.87:0"
→ Payoneer теряет 1,01% ≈ $553 в месяц, $6 642 в год (сходится с постом).
Курс брать из РЕАЛЬНЫХ выписок одного дня, а не с сайта сервиса.
"""
import argparse


def main():
    p = argparse.ArgumentParser(description="Сравнение курса конвертации сервисов выплат")
    p.add_argument("--oborot", type=float, required=True, help="выплаты в месяц, $")
    p.add_argument("--perevodov", type=int, default=4)
    p.add_argument("--servis", action="append", required=True, help='"имя:курс:комиссия%%"')
    p.add_argument("--napravlenie", choices=["prodaem", "pokupaem"], default="prodaem")
    p.add_argument("--fiks", type=float, default=0.0, help="фикс. плата за перевод, $")
    a = p.parse_args()

    rows = []
    for s in a.servis:
        name, rate, fee = (s.split(":") + ["0"])[:3]
        rate, fee = float(rate), float(fee)
        if a.napravlenie == "prodaem":
            # получаем валюту: сколько валюты дают за оборот после комиссии
            value = a.oborot * (1 - fee / 100) * rate - a.fiks * a.perevodov * rate
        else:
            # платим $ за валюту: сколько валюты купим на оборот
            value = (a.oborot * (1 - fee / 100) - a.fiks * a.perevodov) / rate
        rows.append((name, rate, fee, value))

    best = max(rows, key=lambda r: r[3])
    print(f"Оборот ${a.oborot:,.0f}/мес, переводов {a.perevodov}, направление: {a.napravlenie}")
    print(f"{'Сервис':<12}{'курс':>9}{'комис.%':>9}{'потеря %':>10}{'$ в мес':>10}{'$ в год':>10}")
    for name, rate, fee, value in sorted(rows, key=lambda r: -r[3]):
        loss_pct = (1 - value / best[3]) * 100
        loss_usd = a.oborot * loss_pct / 100
        print(f"{name:<12}{rate:>9.4f}{fee:>9.2f}{loss_pct:>10.2f}{loss_usd:>10.0f}{loss_usd*12:>10.0f}")
    print(f"\nЛучший: {best[0]}. Строку «конвертация, %» внести в юнит-экономику (sourcing-1688 → «Параметры»).")


if __name__ == "__main__":
    main()
