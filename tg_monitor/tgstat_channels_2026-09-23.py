"""Channels the user opened on TGStat 23.09.2026 (Chrome tabs): join link + description from Telegram's own page.
Output: tgstat_channels_2026-09-23.csv / .md next to this file."""
import csv
import html
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# (title from the TGStat tab, @username or private invite code)
TABS = [
    ("ГуголЪ | IT и Тренды", "@google_trends2"), ("Креативщик • Тренды", "@creativsh"), ("Стилево | Тренды 🦄", "@stilevotrend"),
    ("Skin boss / Тренды и новинки косметологии", "@skin_bossy"), ("в тренде у девочек", "@females"),
    ("По моде | Тренды 2026", "@odezhda_stil_moda"), ("Прокачай Мозг: Айти, Тренды, Технологии", "@iPumpBrain"),
    ("SHOP SECRET - канал о красивых покупках, трендах и стиле звезд", "@shop_sekret"),
    ("SHE BUYS FIRST - Первая в находках и трендах", "@she_buys"), ("Маркетолог в тренде", "@marketvtrende"),
    ("Кликай - тренды, маркетинг", "@clickaytrend"), ("Нажми Enter | Тренды, ІТ и бизнес", "@PushEnter"),
    ("Коммерcтайп — бизнес и тренды", "@commerstype"), ("БизнесХаб — бизнес и тренды", "@bsn_hub"),
    ("Bt — бизнес и тренды", "@bi_trends"), ("Стартапная | Тренды и бизнес", "@startapnaya"),
    ("РИЛС | REELS ТРЕНДЫ | ШАБЛОНЫ CAPCUT | МЕМЫ", "@reelstutor"), ("ТРЕНДЫ", "@thetrends_journal"),
    ("Мария Штерн • Астрология в тренде", "@MariaSternAstrology"), ("Тренды на WB|OZON", "daHXWCx-QTliNmFi"),
    ("ПО ТРЕНДАМ | Находки", "GatdumB86kRlZjc6"), ("Мода в капсуле | Образы | Стиль | Тренды", "@shoppingfyou"),
    ("Топоева Олеся. Стиль. Мода. Тренды. Вдохновение.", "@topoeva_olesya"), ("MurCating | Тренды и Реклама", "@murcating_telegram"),
    ("В тренде сегодня", "VpvhlZTP0wVjN2Ey"), ("ДЕНЬГИ И ТРЕНДЫ", "@biznes_prof"), ("Бренды и тренды", "@brandstr"),
    ("Abramovrich | Тренды WB — находки, обзоры, распаковки на Wildberries", "@abramovrich_wb"),
    ("Бегущая за трендами", "@runtobuy"), ("Будь в тренде | Мода и стиль", "aHXPxTR2B0I5Yjcy"),
    ("бренды в тренды", "@natashaishere"), ("theGirl | тренды, поп-культура", "@thegirlrussia"),
    ("SMMочная | Тренды и маркетинг", "@rustrendy"), ("Женские Тренды✨", "@Womens_Trends"), ("WB ТРЕНДЫ", "@WBTreends"),
    ("Светлана Нечего Надеть | Стилист, Тренд-аналитик, стиль, мода, тренды", "@svetlana_nechego_nadet"),
    ("XL Женская одежда в Тренде", "@xlvtrende"), ("Красота в тренде🌸", "@krasota_v_trende"),
    ("ПРО́МТИ: тренды и промты ИИ", "@promty_by_irri"), ("Заигрываю с трендами", "@stilisteczortist"),
    ("Маркетинг: Тренды и кейсы", "@marketing_trends_all"), ("Brand Analytics – цифры и тренды", "@BrandAnalytics"),
    ("Old school | антитренды", "@oldshool_3"), ("Женская мода | Стиль | Тренды в Телеграм 🌸", "@moda_vtelege"),
    ("Мировые маркетплейсы: новости и тренды", "@world_ecom"), ("Диана-Мама в тренде🤍", "@DianaMamavTrende"),
    ("Технобум: новости, тренды, IT", "@braingearsit"), ("Тренды с Инной Питеровой | свадебные торты | декор", "@trendipiterova"),
    ("ТРЕНД АНАЛИТИКА ОДЕЖДЫ", "@cloter_trend_poshiv"), ("ТРЕНДЫ КОНТЕНТА", "@valeri_bloc"),
    ("Pro_reelss: тренды & эстетика", "@pro_reelss"), ("Тренды-бренды| маркетинг", "@androidmasterapps"),
    ("Пингвин ИИ | Тренды и идеи", "@photopingvin_ai"), ("ТРЕНДЫ 2026 / Мода и Стиль", "@my_image_and_style"),
]
HERE = Path(__file__).parent
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128.0 Safari/537.36"}


def info(link):
    s = BeautifulSoup(requests.get(link, headers=UA, timeout=20).text, "html.parser")
    desc = s.select_one(".tgme_page_description")
    extra = s.select_one(".tgme_page_extra")
    return (desc.get_text("\n", strip=True) if desc else ""), (extra.get_text(" ", strip=True) if extra else "")


rows = []
for title, h in TABS:
    link = f"https://t.me/{h[1:]}" if h.startswith("@") else f"https://t.me/joinchat/{h}"
    try:
        desc, subs = info(link)
    except Exception as e:
        desc, subs = f"(не загрузилось: {e})", ""
    rows.append({"title": title, "nick": h if h.startswith("@") else "закрытый канал", "link": link,
                 "subscribers": subs, "description": re.sub(r"\n{2,}", "\n", desc)})
    time.sleep(0.7)

with open(HERE / "tgstat_channels_2026-09-23.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)
md = ["# Каналы из TGStat (открыты пользователем 23.09.2026)\n"]
for r in rows:
    md.append(f"- **{r['title']}** — {r['nick']} — {r['link']} — {r['subscribers']}\n  {r['description'].replace(chr(10), ' ')[:400]}")
(HERE / "tgstat_channels_2026-09-23.md").write_text("\n".join(md), encoding="utf-8")
print(len(rows), "каналов; без описания:", sum(not r["description"] for r in rows))
