---
name: trend-radar
description: Парсинг трендов Google Trends/Pinterest/TikTok по ключевым словам (одежда/стили) через Bright Data, плюс поиск и отбор товаров AliExpress (Dolphin с пагинацией или Apify-акторы) для нового магазина, включая сверку с вручную отобранными ссылками и сборку HTML-галереи с фото. Используй, когда просят "проверь тренды", "спарси тренды", "запусти trend radar", "найди товары на алиэкспресс по запросу", "спарси N страниц по запросу", "сравни с моей ручной подборкой", "собери галерею с фото товаров". Триггеры: "тренды", "trend radar", "google trends", "парсинг трендов", "bright data", "aliexpress apify", "пагинация алиэкспресс", "галерея товаров", "сверка с ручным отбором".
---

# Fashion Trend Radar

Проект `C:\Users\User\fashion-trend-radar\fashion-trend-radar` — сбор данных Google Trends
(интерес по неделям за 12 месяцев) по ключевым словам одежды для нового магазина
(Dolphin-профиль 859648353, домен 2e0bv7-jn.myshopify.com). Считает score (рост +
импульс + стабильность интереса) и складывает результат в `data/exports/`.

## Запуск

```powershell
cd C:\Users\User\fashion-trend-radar\fashion-trend-radar
.\.venv\Scripts\python.exe run.py
```

Занимает ~1-2 минуты на ключевое слово (плюс пауза 45с между словами против блокировок) —
на 6 слов из `config/keywords.csv` уходит 8-10 минут. Не прерывать раньше времени.

Ключевые слова редактируются в `config/keywords.csv` (колонки `keyword,category,style,priority`).
Токен Bright Data — в `.env` (`BRIGHTDATA_API_TOKEN`), уже настроен.

## Результат

- `data/exports/trends_summary_*.csv` — главный файл: keyword, category, style, priority,
  score, latest_value, avg_value, отсортировано по score убыванию.
- `data/exports/trends_timeseries_*.csv` — сырой ряд по неделям на каждое слово.
- `data/exports/trends_geo_*.csv` — интерес по регионам США.

## Как это устроено

Не через SERP API-зону Bright Data (она только под обычный google-поиск, без произвольных
URL) — а через **кастомный Web Scraper IDE краулер** Bright Data,
`collector=c_mtyj2z3e14ur8nhivi`, собранный через их AI-ассистента под конкретно
`trends.google.com/trends/explore`. Вызов асинхронный:

1. `POST https://api.brightdata.com/dca/trigger?collector=c_mtyj2z3e14ur8nhivi&queue_next=1`
   с телом `[{"url": "<трендовая ссылка>"}]` → возвращает `collection_id`.
2. Поллинг `GET https://api.brightdata.com/dca/dataset?id=<collection_id>` каждые ~10с:
   `collecting` → `building` → готовый JSON, либо пустое тело 200 = 0% успеха (сбор
   провалился, надо перезапускать это слово).
3. Успешный прогон — от ~45с до нескольких минут, это нормально, не зависание.

Реализовано в `src/clients/brightdata_client.py` (`trigger`/`fetch_result`/`fetch_url`,
`max_wait=300`с). Формат ответа краулера — плоский JSON с `interest_over_time` (список
`{date, interest_value}` по неделям) и `regional_interest` (три списка подряд без явного
разделителя: регионы с `interest_score`, топики и похожие запросы без него).
`src/processors/normalize.py` разбирает это в DataFrame, `scoring.py` считает score.

## Pinterest (добавлено 12.09.2026)

Отдельный сигнал, не через официальный Pinterest API (Trial access отклонили, да и Trends API
у Pinterest всё равно закрытый продукт для агентств/enterprise — в списке scopes на
developers.pinterest.com раздела Trends вообще нет). Вместо этого — тоже через Bright Data,
готовый датасет-скрапер `dataset_id=gd_lk0sjs4d21kdr7cnlv` (сайт pinterest.com), в режиме
поиска по ключевому слову.

Запуск:
```powershell
cd C:\Users\User\fashion-trend-radar\fashion-trend-radar
.\.venv\Scripts\python.exe run_pinterest.py
```

Это **синхронный** вызов (`POST /datasets/v3/scrape`, не `/dca/trigger`+poll), ответ приходит
одним блокирующим запросом в формате NDJSON (по объекту JSON на строку, не единый массив) —
`src/clients/pinterest_client.py` разбирает построчно. Проходит по всем словам за пару минут,
пауза между словами всего 15с (не 45с как у Google Trends).

Вызов:
```
POST https://api.brightdata.com/datasets/v3/scrape
  ?dataset_id=gd_lk0sjs4d21kdr7cnlv&notify=false&include_errors=true&type=discover_new&discover_by=keyword
Body: {"input":[{"keyword":"<слово>"}],"limit_per_input":20}
```

Результат — файлы `data/exports/pinterest_summary_*.csv` (score по слову) и
`pinterest_pins_*.csv` (сырые пины). Score считает `src/processors/pinterest_scoring.py`:
`post_count*0.6 + recency_ratio(180 дней)*100*0.4` — **не** по лайкам, потому что:

- **Поле `likes` в этом датасете всегда 0** — скрапер не отдаёт реальные лайки/сохранения.
  Не пытаться чинить это в коде — это ограничение самого источника данных.
- **Неоднозначные ключевые слова путают выдачу**: «baby tee» (модный укороченный топ) Pinterest
  в основном находит как «Infant Tees» (одежда для младенцев) — для двусмысленных слов
  результат ненадёжен, проверять `top_related_hashtags` в сводке на смысл, а не слепо доверять
  score.
- Часть input-строк в ответе — не пины, а ошибки `{"error":"Bad input. Page does not exist.",
  "error_code":"dead_page"}` вперемешку с валидными записями (обычно первые 1-2 на keyword) —
  `pinterest_normalize.py` их отфильтровывает по наличию ключа `error`.

## Правка краулера в Bright Data IDE (важно, 12.09.2026)

Кнопка **«Save to development»** в редакторе краулера сохраняет только черновик —
обычные запросы через API (`/dca/trigger`) продолжают идти на **production**-версию
кода и падают с `422 Unprocessable Entity`, если вживую поменяли Interaction/Parser
code и не задеплоили. Нужно **обязательно** нажать стрелку рядом с кнопкой →
**«Save to production»** (это гоняет ещё один тестовый прогон и просит короткий
комментарий «What was changed?»). Признак сломанного продакшена — иконка
**SCHEMA** с красным «!» на странице обзора коллектора
(`brightdata.com/cp/data_collector?...`), тултип «The schema structure doesn't
match the data that the collector is producing» — кликнуть по ссылке «here» в
тултипе, чтобы попасть прямо в редактор кода.

Если правка сломала прод и непонятно почему — самый быстрый путь: откатить
Interaction/Parser code на последнюю рабочую версию (см. блоки кода выше в этом
файле), прогнать Preview, затем **Save to production**, и только после этого
проверять реальным Python-запросом (`GoogleTrendsCollector().fetch_keyword_data(...)`),
а не доверять статусу в UI — он может показывать устаревшее «Last modified».

## TikTok (добавлено 13.09.2026)

Третий сигнал, тоже через Bright Data, готовый датасет-скрапер
`dataset_id=gd_lu702nij2f790tmv9h` (сайт tiktok.com), поиск по ключевому слову.
В отличие от Pinterest, здесь **реальные лайки и просмотры отдаются** — не нули.

Запуск:
```powershell
cd C:\Users\User\fashion-trend-radar\fashion-trend-radar
.\.venv\Scripts\python.exe run_tiktok.py
```

Асинхронный вызов, как у Google Trends (не синхронный, как у Pinterest):
`POST https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_lu702nij2f790tmv9h&notify=false&include_errors=true&type=discover_new&discover_by=keyword`,
тело `{"input":[{"search_keyword":"<слово>","country":""}],"limit_per_input":20}` →
`snapshot_id`, затем поллинг `GET /datasets/v3/snapshot/<id>?format=json` каждые 15с
(таймаут 600с) до непустого ответа. Реализовано в `src/clients/tiktok_client.py`
(`TikTokClient.search_keyword`) и `src/collectors/tiktok_collector.py`. Пауза между
словами — 15с, как у Pinterest.

Результат — `data/exports/tiktok_summary_*.csv` (score по слову) и
`tiktok_videos_*.csv` (сырые видео: author, likes, plays, create_time, hashtags,
description, url). Score считает `src/processors/tiktok_scoring.py`:

```
unique_authors*3 + recency_ratio(90 дней)*100*0.15 + log1p(median_plays)*3 + median_engagement_rate*1000*0.4
```

Логика (см. докстринг в коде) — весит **независимых авторов и engagement RATE**, а не
сырые просмотры: одно вирусное видео с низкой вовлечённостью — медиа-случайность, а не
повторяемый паттерн спроса. Окно recency — 90 дней (короче, чем 180 у Pinterest, потому
что тренды TikTok выгорают быстрее).

Пример сырых данных по "plaid skirt" (файл `trend_radar_dashboard_retry.html`,
дашборд собран 13.09.2026): 9 видео, лайки от 1 213 до 46 400, просмотры от 12 400 до
863 300 — разброс большой, поэтому скоринг и берёт медианы и engagement rate, а не сумму.

## AliExpress: два источника (Dolphin + Apify)

**Важно (15.09.2026): весь AliExpress-парсинг для этого проекта — только через
профиль Dolphin{anty} 859648353** (профиль нового магазина, см.
[[novyy-magazin-shopify-profil3]] в памяти). Профиль 828976678 («Ремешки») —
чужой магазин, использовать здесь нельзя. `PROFILE` в
`src/clients/aliexpress_dolphin_client.py` исправлен на 859648353.

### Источник 1 — Dolphin (антидетект-браузер), с пагинацией

`src/clients/aliexpress_dolphin_client.py::search_keyword(..., page=N)` —
параметр `page` открывает конкретную страницу выдачи AliExpress
(`&page=N` в URL). `src/collectors/aliexpress_collector.py::AliExpressCollector
.fetch_keyword_data(..., pages=N)` оборачивает это циклом `page=1..N`,
дедуплицирует по `url`, останавливается раньше, если очередная страница не
дала новых товаров. Пауза между страницами (`page_pause`, по умолчанию 3с).

Фильтр «Quality & trust» (4★ и выше) на самом AliExpress **выключен по
умолчанию** (`apply_rating_filter=False`) — раньше жёстко прибивал выдачу к
4★+, что мешало сравнивать с ручным отбором. Цена (`minPrice`/`maxPrice`)
по-прежнему фильтруется прямо в URL. Включить рейтинг-фильтр сайта:
`apply_rating_filter=True`.

Требует playwright в venv проекта (`pip install playwright` — раньше он был
только в системном Python 3.13, из-за чего пагинация падала с
`ModuleNotFoundError`; добавлен в `requirements.txt`).

Пример (30 страниц, только цена $10-60 на сайте, фильтр по рейтингу/продажам
после):
```python
from src.collectors.aliexpress_collector import AliExpressCollector
from src.processors.aliexpress_filter import filter_products

rows = AliExpressCollector().fetch_keyword_data(
    keyword="plaid skirt", limit=60, search_text="women's plaid skirt",
    min_price=10, max_price=60, pages=30,
)
kept = filter_products(rows, min_rating=4.5, min_price=10, max_price=60, min_orders=30)
```
`aliexpress_filter.passes_quality_gate`/`filter_products` теперь принимают
`min_orders` (было: только `orders>0`).

### Источник 2 — Apify, ДВА разных актора (не путать)

**`devcake/aliexpress-products-scraper`** (старый, `aliexpress_apify_client.py`,
`run_aliexpress_apify.py`) — **НЕ умеет пагинировать несмотря на схему**:
`maxProducts` официально 50-1000, но реально всегда возвращает одну страницу
выдачи (~50-60 товаров), что при `maxProducts=1000` тоже. Проверено прямым
вызовом API 15.09.2026: 50→50, 1000→59. Не пытаться увеличивать `maxProducts`
у этого актора — бессмысленно, только оставлять 50.

**`axlymxp/aliexpress-search-scraper`** (найден и подключён 15.09.2026,
`src/clients/aliexpress_search_scraper_client.py`, актор-id
`uNGAIgYARPCnogDTx`) — **реально пагинирует**: `maxItemsPerQuery` до 3600,
60 товаров = 1 страница AliExpress, честно ходит по страницам. Отдаёт готовые
числовые `rating`, `orders`, `price` (не текст) — парсить не нужно. Пример на
запросе 20×60=1200 сработал: вернул 744 товара в цене $10-60, из них 117 с
рейтингом>4.5 и продажами>30.

Цена — **pay-per-event**: $0.003 за каждый возвращённый товар + $0.01 за
запуск актора (~$3/1000 товаров). Не путать со старым актором ($2/1000, но
там всё равно нельзя получить больше одной страницы).

Актор иногда падает с `transient network error`/`curl: (28) timeout` на
самом первом запросе и возвращает 0 товаров при статусе `SUCCEEDED` — это
не баг вызова, а разовый сетевой сбой самого актора; **просто повторить
запуск**, деньги за 0 товаров почти не списываются (только $0.01 за старт).

```python
from src.clients.aliexpress_search_scraper_client import search_keyword
rows = search_keyword("plaid skirt", max_items=1200, search_text="women's plaid skirt",
                       sort="default", min_price=10, max_price=60)
kept = [r for r in rows if (r["rating"] or 0) > 4.5 and (r["orders"] or 0) > 30]
```
Пример готового раннера: `run_plaid_skirt_apify.py`.

Токен обоих акторов — `.env` → `APIFY_API_TOKEN` (аккаунт Apify пользователя,
логин через антидетект-профиль 859648353).

### Сверка с товарами, отобранными вручную

Когда пользователь сам отбирает товары на сайте (открывает вкладки, экспортирует
ссылки в txt через `links_from_tabs*.txt` на рабочем столе) и просит сравнить с
автоматической подборкой:

1. Вытащить ID товара из каждой ссылки регэкспом `item/(\d+)`, сравнить
   множества ID (**не** через `comm` — путь `/tmp` в Git Bash на этой машине
   нестабилен между вызовами Bash-тула и `comm` тихо даёт неверный результат
   без ошибки; сравнивать через Python `set() & set()`).
2. Для отсутствующих ID — зайти на `https://www.aliexpress.us/item/<id>.html`
   через Dolphin (см. выше) и прочитать текущие цену/рейтинг/продажи живьём:
   `[class*="price-default--wrap"]` (цена, `\$([\d.]+)`),
   `[class*="reviewer--rating"]` (рейтинг, число), `[class*="sold"]`
   (текст вида "306 sold"). Так выясняется, что часть пропусков — заслуженный
   отсев по фильтру (продажи ≤30, рейтинг ≤4.5, цена вне диапазона), а часть —
   товары, которые реально проходят все условия, но актор их не увидел
   (выдача AliExpress персонализируется по аккаунту/куки — актор идёт с
   чистого прокси без привязки к пользователю, поэтому набор и ранжирование
   отличаются от того, что видно вручную в браузере).
3. Для найденных «упущенных, но подходящих» — забрать `og:title`/`og:image`
   с той же страницы товара (`fetch_extra_picks.py` — пример) и добавить в
   общую подборку с пометкой `source: "manual"`.

### Галерея с фото (HTML-артефакт)

Табличный CSV со ссылками на картинки **не читается** — превращать финальную
подборку в HTML-галерею (Artifact), не в голый CSV:

- Картинки с `aliexpress-media.com` **не грузятся** в артефакте — CSP рендерера
  разрешает внешние `<img>` только с горстки доменов (не включает AliExpress
  CDN). Нужно скачать все картинки локально (`requests.get` с
  `User-Agent` браузера, иначе может не отдать) и опубликовать их как
  файлы артефакта (`files: [{"path": "imgs/000.jpg"}, ...]`,
  `root: "<папка со scratch-файлами>"`), а в JSON-данных страницы ссылаться
  на `imgs/NNN.jpg`, не на внешний URL.
- Карточка: фото, цена, рейтинг, orders_text, кнопка "Open on AliExpress" на
  реальный `url`. Сортировка (по продажам/рейтингу/цене) и фильтр по
  `is_choice`/`source==manual` — на чистом JS, без библиотек.

## Грабли (проверено 11-12.09.2026)

- **Параметр `cat` в URL Google Trends обязан быть числовым кодом категории** (например
  185 = Apparel), а НЕ текстовым словом. `config/keywords.csv` использует `category`/`style`
  как свои лейблы для группировки — их **нельзя** подставлять в `cat` URL: страница Trends
  тогда не рендерит график, и краулер падает по таймауту
  (`waiting for selector ".fe-line-chart-directive table tbody tr" failed`). Это была причина
  всех сбоев при первой настройке — `google_trends_collector.py` теперь `cat` в URL не
  добавляет вообще. Если понадобится фильтр по категории Google — искать числовой код
  в их документации, не использовать своё текстовое значение.
- Даты в ответе краулера содержат невидимые unicode-символы направления текста
  (U+200E/U+202A-E) вокруг текста — `normalize.py` вырезает их регэкспом.
- Bright Data SERP-зона (`serp_api1`, доступна из `.env`/`config/settings.py` как
  `BRIGHTDATA_ZONE`) в принципе не поддерживает открытие произвольных URL вроде
  `trends.google.com/...` — только структурированный google-поиск (domain, gl/hl, tbm).
  Не пытаться чинить парсинг Trends через неё, только через кастомный краулер выше.
- Между запросами разных ключевых слов нужна пауза (сейчас 45с в `run.py`) — без неё
  Google Trends начинает возвращать 0% успеха подряд (похоже на временную блокировку
  после нескольких быстрых обращений).
