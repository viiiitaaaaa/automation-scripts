---
name: trend-radar
description: Мультиканальный тренд-радар женской одежды (США) — проект fashion-trend-radar. Проверяет кандидатов-вещи шестью независимыми «свидетелями» (Google, Pinterest, YouTube, TikTok, Amazon, бренды) на двухлетней истории, решает «тестировать / наблюдать / отказ», метит сезонность и собирает дашборд с кривыми за 2 года. Используй, когда просят «запусти тренд радар», «пересчитай радар», «обнови дашборд тренд радар», «проверь кандидата», «добавь канал в радар», «собери YouTube/подсказки/Amazon/бренды», «какие данные ещё не подключены», «какие API нужны». Триггеры: "тренд радар", "trend radar", "кандидаты", "дашборд трендов", "google trends", "pinterest trends", "сезонность", "youtube api", "подсказки поиска".
---

# Fashion Trend Radar (v2, 22.09.2026)

Проект: `C:\Users\User\fashion-trend-radar\fashion-trend-radar`, Python — `.\.venv\Scripts\python.exe`.
Бэкап кода: GitHub `viiiitaaaaa/automation-scripts`, папка `fashion-trend-radar/` (копия, не живой репозиторий).
ТЗ и история решений: `TZ_trend_scoring.md` в проекте — читать при любом изменении логики.

Идея: один сигнал = шум. Вещь-кандидат идёт в тест, только если рост видят несколько
независимых каналов, и рост — не повтор прошлогоднего сезона.

## Правила пользователя (не нарушать)

- **Никаких автозапусков и расписаний.** Логику тестируем; каждый сбор — только по команде
  пользователя. `run_scheduled.py daily|weekly` — ручной оркестратор, в Планировщик не ставить.
- **Dolphin — только профиль 859648353** (не 828976678). Хелперы:
  `sys.path.insert(0, r"C:\Users\User\dolphin_anty"); from dolphin import DolphinLocal, start_with_retry`;
  `start_with_retry(api, 859648353, no_tabs=True)["automation"]` → `connect_over_cdp`.
  Всё в ОДНОМ запуске скрипта — `start_with_retry` перезапускает профиль и сбрасывает вкладки.
- **TikTok — окно минимум 90 дней.**
- **Не обходить защиту сайтов:** никаких прокси-ротаций, подмены личности, стелс-библиотек,
  долбёжки после 429/таймаутов. Человеческий темп, паузы. После 2-3 неудач — стоп и отчёт.
- **Неофициальные библиотеки отвергнуты (22.09):** instagram_private_api (ping, dilame),
  igbot, TikTok-Api (davidteather), Douyin_TikTok_Download_API, TikTokAPI-Python, TikTokBot,
  php-pinterest-bot, pinterest-api-php (API v1 отключён), reaper (мёртв). Причины: логин/пароль,
  имитация приложения, маскировка бота, риск бана. Не предлагать повторно.
- **AliExpress из логики убран полностью.** Поставщиков ищем только после отбора кандидата.
- **ARTMELLIO — не её магазин**, не упоминать. Своего магазина пока нет.
- Ключи — только в `.env` проекта (он в .gitignore). `Get-Content .env` блокируется защитой —
  читать ключ внутри python-скрипта. Токены OAuth — в `data/secrets/` (тоже в .gitignore).
- Объяснять по-русски, просто, «как первокурснице».

## Каналы и команды

| Канал | Скрипт | Что даёт | Файл результата |
|---|---|---|---|
| Google (веб) | `run_trends_bootstrap.py "<слово>" ...` | 2 года по неделям (pytrends, Semaphore(1), паузы 10-25с) | `data/normalized/google_trends/` |
| Google rising | `run_related_queries.py` | растущие запросы по 10 широким словам, 90 дн | `data/processed/candidates_google_rising.csv` |
| YouTube-поиск | `run_trends_bootstrap.py --youtube "<слово>" ...` | 2 года поиска на YouTube (gprop="youtube") | `data/normalized/google_trends_youtube/` |
| YouTube API | `run_youtube_api.py "<слово>" ...` | видео за 90 дн vs те же 90 дн год назад, просмотры, комментарии «где купить» | `data/processed/youtube_api.csv` |
| Pinterest | `run_pinterest_trends.py` (Dolphin) | рост wow/mom/yoy + 2 года по неделям для кандидатов | `data/processed/pinterest_metrics.csv`, сырые кривые `data/raw/pinterest_trends/metrics_*.json` |
| TikTok CC | `run_tiktok_cc.py` (Dolphin) | топ-100 хэштегов США за 90 дн, мода фильтруется по словам | `data/processed/candidates_tiktok_cc.csv` |
| Amazon | `run_amazon.py` (Dolphin) | Best Sellers + New Releases, 8 женских разделов, снимки | `data/normalized/amazon/amazon_<дата>.parquet` |
| Бренды | `run_retailers.py` (Dolphin) | новинки Zara/ASOS/Aritzia/Free People → признаки | `data/processed/retailer_attributes.csv` |
| Подсказки | `run_autocomplete.py "<слово>" ...` | что дописывают в Google/YouTube/Amazon (цвет, фасон) | `data/processed/autocomplete_summary.csv` |

Кандидаты — `config/candidates.csv` (22 шт., задаются вручную).
После любых сборов: `run_radar.py` → `build_dashboard.py`.

## Логика решения (`src/processors/candidate_matrix.py`)

- `window_stats()`: среднее за **последние 8 недель** против **тех же 8 недель год назад**
  (`yoy_pct`), плюс подъём в эти недели год назад (`lift_prev`). Одна неделя не решает.
- Проверка засчитывается при росте **≥ +15%** (`MIN_YOY`) — одинаково для Google, Pinterest,
  YouTube-поиска. Google ещё засчитывается при попадании в rising-запросы.
- **Редкие ряды не считаются** (`MIN_NONZERO = 0.5`): если данные есть меньше чем в половине
  недель, «0→12 = +1000%» — шум. На графике подпись «мало поисков — не учитываем».
- YouTube (Y) = кривая поиска ≥ +15% **или** просмотры свежих видео (API) ≥ +15% к прошлому году.
- TikTok = хэштег кандидата в топе CC; Amazon = ≥2 товара; бренды = ≥2 ритейлера.
- **Сезон** (`is_seasonal`): год назад в эти же недели был подъём ≥20% (`SEASON_LIFT`), а рост
  к прошлому году < 15%. Сначала по Pinterest, если нет ряда — по Google.
- Решение из 6 проверок: **≥4 TEST, 3 WATCH, иначе REJECT** (как в ТЗ «4 из 6»).
- Сопоставление кандидата с товарами/хэштегами — через `fashion_taxonomy.py` (целые слова,
  сезонные слова fall/winter… — стоп-слова, двухкатегорийные «sweater dress» требуют обе категории).

## Дашборд

`build_dashboard.py` пишет две страницы из `data/reports/radar_candidates.csv`:
- `data/reports/trend_radar_dashboard.html` → публикуется в Artifact
  https://claude.ai/artifact/7XN5rKYANe4QX8HwRHKNZF (обновлять тем же file_path / url).
- Блок кривых (`radar_curves.py`) вставляется между маркерами `<!-- RADAR:START/END -->`
  в начало локального `C:\Users\User\dolphin_anty\trend_radar_dashboard.html`; старый сбор
  12–13.09 ниже как «архив».
Карточка: решение, сезон, квадратики G P Y T A R, **вся кривая за 2 года** (Pinterest, Google,
YouTube) с зелёной полосой «последние 8 недель» и серой «те же недели год назад», внизу Amazon,
бренды, подсказки поиска, YouTube API. Пользователь хочет видеть всю кривую за 2 года,
простую прокручиваемую страницу, без окон/канваса.
Проверка рендера: Playwright-браузеры не установлены — открывать файл через Dolphin 859648353.

## Статусы API и сервисов (22.09.2026)

| Сервис | Статус |
|---|---|
| YouTube Data API | ✅ ключ `YOUTUBE_API_KEY` в .env, 10 000 ед/день, ~220 ед на кандидата |
| Etsy API | ⏳ ключ+секрет в .env, приложение «vi» — Pending Personal Approval (об отказе не уведомляют) |
| Pinterest API v5 | ❌ Trial раньше отклоняли; Trends-скоупа в списке нет. Пример `C:\Users\User\Documents\GitHub\api-quickstart`, `pinterest_auth.py` готов (redirect `http://localhost:8085/`). Данные берём со страницы Trends через Dolphin |
| Instagram Graph API | не подключён; путь: аккаунт «Автор» + страница Facebook + приложение Meta (Business, «API setup with Facebook login») в режиме разработки — магазин и App Review не нужны для своего аккаунта |
| Reddit API | ❌ исключён: коммерческое использование требует письменного одобрения |
| Google Merchant Center | ⏸ регистрация просит карту — отложено |
| Meta Ad Library | ⏸ нужна платёжка |
| Apify | FREE $6/мес, до 14.10 осталось ~$0.5 (ушло на AliExpress) |
| Bright Data | токен есть, но пользователь считает дорогим — не запускать без явного «да» |
| Keyword Tool | платный, отложен |

## Грабли

- **Pinterest `/metrics/`** отдаёт рост долями (0.3 = +30%); обязательные параметры country,
  end_date, days=730, aggregation=2, normalize_against_group=false, predicted_days=0.
- **TikTok CC**: URL-параметр периода игнорируется — переписывать `timeRange` в теле
  `GetHashtagList` через `page.route`. Фильтр индустрии не воспроизводится. С 09.2026 CC переехал
  в TikTok One: `/business/creativecenter/hashtag/<name>` редиректит на общий список, аналитика
  только по числовому id, поиска нет; tag-страница tiktok.com данные грузит отдельно и 22.09 ушла в таймаут.
- **Amazon Movers & Shakers** пуст по Fashion — сравниваем свои снимки Best Sellers.
- **YouTube API**: `regionCode=US` не отсекает индийские хаулы (Myntra/Flipkart) — отбрасывать
  каналы IN/PK/BD/NP/LK. Просмотры прошлогодних видео копились дольше — рост занижен, не завышен.
  «price» считать намерением только в вопросе (`price?`, «how much»).
- **YouTube-поиск через Trends** по товарным фразам почти пустой (данные у 4 из 22) — на YouTube
  ищут «fall outfit ideas / how to style», а не «roll neck sweater».
- Google 2y по редким фразам — много нулей (bandana cardigan «+1512%» был артефактом).
- Aritzia отдаёт ~10 товаров (подгрузка при прокрутке).
- PowerShell: here-string с `as p:` в python-коде ловится защитой — писать скрипт в файл в scratchpad.

## Что не сделано (по запросу пользователя)

TikTok по кандидатам (Dolphin-поиск или Apify после 15.10), Instagram (Dolphin-скрипт
`instagram_hashtag_dashboard.py` или Graph API), автоподбор кандидатов, чистка шума Google rising,
больше брендов, насыщение рынка, поставщики/маржа, удаление probe_*.py.
