# Trend Radar — API и подписки (состояние на 24.09.2026)

## Что уже работает бесплатно (через входы пользователя, без API)

| Источник | Как | Скрипт |
|---|---|---|
| Pinterest Trends (кривые 2 года, растущие вещи, возраст/пол) | бизнес-вход в Dolphin-профиле 3 | `run_pinterest_extra.py`, `run_pinterest_discovery.py` |
| Temu США (товары, продажи, цены) | вход пользователя в Temu, Dolphin-профиль 3 | `run_temu.py` |
| Реклама конкурентов США (Meta Ad Library, сайт) | Dolphin-профиль 3 | `run_meta_adlib_web.py` |
| Насыщение Amazon (товары, бренды, отзывы, «куплено за месяц») | Dolphin-профиль 3 | `run_saturation.py` |
| Бренды: новинки сейчас + история 2 года (Wayback Machine) | Dolphin-профиль 3 / веб-архив | `run_retailers.py`, `run_brand_history.py` |
| Telegram (новости, закрытые каналы, чат shopify_chat) | вход в Telegram Web | `tg_monitor/tg_web_reader.js` |
| Google Trends, YouTube-поиск | pytrends (бесплатно, но Google часто отвечает 429) | `run_trends_bootstrap.py` |
| YouTube Data API | ключ в `.env` | `run_youtube_api.py` |

## Чего не хватает — по важности

| # | Что | Что даст | Цена | Статус |
|---|---|---|---|---|
| 1 | **Пополнить treg.to** | TikTok США, Instagram, TikTok Shop, объёмы/варианты/возраст Google (правило 28+) | $5–10 | баланс в нуле (HTTP 402) |
| 2 | **Официальный Google Trends API** | без отказов 429; кривые YouTube по новым вещам | бесплатно, заявка от аккаунта Google пользователя | не подано |
| 3 | **Trends MCP Pro** | поиск Amazon и TikTok за 2 года вместо 90 дней, без устаревших данных | ~$20–30/мес | бесплатно 100 запросов/мес (73 использовано) |
| 4 | **Apify (Temu)** | Temu по нескольким страницам и с сортировкой по продажам | ~$3 / 1000 товаров, $5/мес бесплатно | нужен `APIFY_TOKEN` в `.env` |
| 5 | **Keepa** | история продаж и цен Amazon за 2 года | от €49/мес | когда будем выбирать товар для закупки |
| 6 | **Google Merchant Center** | отчёт «лучшие товары» Google | бесплатно, при регистрации карта | не зарегистрирован |

Лучшие по пользе: 1–3. Остальное уже закрыто бесплатными способами.

## Temu — варианты API
- Apify: [zentrafoundry/temu-product-price-tracker](https://apify.com/zentrafoundry/temu-product-price-tracker/api) (~$3/1000), [apivault_labs/temu-product-scraper](https://apify.com/apivault_labs/temu-product-scraper)
- Oxylabs: [Temu Scraper API](https://oxylabs.io/products/scraper-api/ecommerce/temu) — платный, пробный период
- В каталоге treg.to Temu нет.

## Отклонено (не предлагать повторно)
- **Etsy** — ключ забанен 22.09, новых заявок не подавать.
- **Reddit** — коммерческое использование только с письменного одобрения Reddit; сторонние сборщики Reddit (в т.ч. через treg) нарушают его правила.
- **Meta Ad Library API** — аккаунту нужен доступ через подтверждение личности (ошибка 10 / 2332002); пользователь это делать не будет. Реклама США собирается через сайт.
- **Google Shopping** — убран 24.09: по нашим вещам почти одни нули.
- Неофициальные библиотеки (instagram_private_api, TikTok-Api и т.п.) — риск бана.

## Где ключи
Все ключи — только в `.env` проекта fashion-trend-radar (в `.gitignore`, на GitHub не попадает):
`TREG_TOKEN`, `TREG_ORG`, `TRENDSMCP_*`, `YOUTUBE_API_KEY`, `META_ACCESS_TOKEN` (не рабочий без доступа), при подключении — `APIFY_TOKEN`.
