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

## Логика отбора кандидатов (пользователя) — применять к новым ДО показа

Выведена из её решений 22–23.09.2026 (из 22 оставила 6), воспроизводит выбор 1:1:
1. **Вещь, а не тема** — не «fall outfit inspo / fall cardigan / womens fall jacket».
2. **Одна идея — одна вещь** — из близких вариантов оставлять более широкий/сильный (plaid skirt, не plaid mini).
3. **Рост к прошлому году обязателен** — падает → вон даже при большом объёме; «большой, но стабильный» — не довод.
4. **Ранний тренд ценнее подтверждённого** — взлёт в Google + живой TikTok США + первые продажи → тест, даже при 2/7.
5. **Сезон по Google Trends, только текущий/ближайший** (≤2 мес.) — учитывать обязательно; далеко → «позже» только
   для сильных; сезон <2 мес. / «под одно событие» — нет.
6. **Реальный объём или рост** — узкие слабые (<~2–3 тыс. поисков/мес, мёртвые хэштеги) отсеивать, кроме раннего тренда.
7. **Рынок США.** 8. **Короткий сильный список.**
Спорные случаи помечать отдельно — решает пользователь.

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
| Google Shopping | `run_trends_bootstrap.py --shopping --all` | 2 года покупательского интереса (gprop=froogle); входит в проверку G | `data/normalized/google_trends_shopping/` |
| Доп. сигналы (Dolphin) | `run_extra_signals.py --pinterest --amazon` | другие формулировки для Pinterest Trends (`VARIANTS`); Amazon: сумма «N+ bought in past month» на 1-й странице поиска | `data/raw/pinterest_trends/variants_*.json`, `data/processed/amazon_bought.csv` |
| TikTok по нашим хэштегам (США) | `run_tiktok_tags.py ["<слово>" ...]` | treg.to → TikHub, $0.001/запрос, 2 на вещь (~$0.044 за 22): карточка хэштега (всего видео/просмотров, statsV2) + до 30 видео `region=US` со ссылками; T засчитывается при ≥5 свежих (30 дн) американских видео и ≥40% выдачи | `data/processed/tiktok_tags.csv`, `tiktok_tag_videos.csv` |
| Instagram по нашим хэштегам | `run_instagram_tags.py ["<слово>" ...]` | treg → TikHub v2 `feed_type=recent`, $0.002/запрос, 3 страницы по 12 постов (~$0.124 за 22); страны нет — весь мир; частота «постов в день» по последним ~36 постам + самые залайканные свежие. Пока только информация на карточке, не голос | `data/processed/instagram_tags.csv`, `instagram_tag_posts.csv` |
| Объём поиска Google (США) | `run_google_volume.py` | DataForSEO через treg: **$0.09 за ОДИН запрос на все слова** (не запускать дважды!) — реальные поиски в месяц за 12 мес, CPC; на карточке столбики + «последний месяц к среднему» | `data/processed/google_volume.csv`, `google_volume_monthly.csv` |
| TikTok Shop (США) | `run_tiktok_shop.py [--from-raw]` | TikHub через treg, $0.001: 1-я страница поиска (до 30 товаров) — **сколько продано**, цены, продавцы, ссылки. `--from-raw` перечитывает сегодняшние ответы бесплатно. Ответ TikHub обёрнут дважды: `data.data.products` | `data/processed/tiktok_shop.csv`, `tiktok_shop_products.csv` |
| TikTok тренды дня | `run_tiktok_trending.py [страниц]` | общемировая лента «Интересное» (~10 видео на запрос) + трендовые поисковые запросы; не про моду | `data/processed/tiktok_trending_<дата>.csv` |
| Trends MCP | `run_trendsmcp.py ["<слово>" ...]` | Amazon: поиски в месяц (4 мес) + рост к прошлому месяцу; TikTok: объём хэштега по дням (только крупные хэштеги). 1 запрос = 1 вещь × 1 источник, кэш 7 дней | `data/processed/trendsmcp.csv` |

Кандидаты — `config/candidates.csv`: с 23.09 **6 шт.** (roll neck sweater, bandana cardigan, plaid skirt,
faux fur coat, flannel shirt women, lace trim top) — пользователь оставила только их; прежние 22 — в
`config/candidates_22_backup_2026-09-23.csv`. Сезонки переводятся в «наблюдать» ручным решением. Колонка `pinterest_term` — формулировка, которую знает Pinterest Trends
(fall cardigan → cardigan); кривая берётся по ней.
После любых сборов: `run_radar.py` → `build_dashboard.py`.

## Логика решения (`src/processors/candidate_matrix.py`)

- `window_stats()`: среднее за **последние 8 недель** против **тех же 8 недель год назад**
  (`yoy_pct`), плюс подъём в эти недели год назад (`lift_prev`). Одна неделя не решает.
- Проверка засчитывается при росте **≥ +5%** (`MIN_YOY`; до 22.09.2026 было 15%, снижено по решению
  пользователя) — одинаково для всех проверок роста ниже. Google ещё засчитывается при попадании в rising-запросы.
  Пользователь считает, что plaid skirt, plaid mini skirt, bandana cardigan, fall cardigan не должны быть в отказе —
  сначала добирать данные (Google Shopping 2 года, формулировки, Amazon «bought in past month», Pinterest-поиск),
  а не подкручивать правила под ответ.
- **Редкие ряды не считаются** (`MIN_NONZERO = 0.5`): если данные есть меньше чем в половине
  недель, «0→12 = +1000%» — шум. На графике подпись «мало поисков — не учитываем».
- YouTube (Y) = кривая поиска ≥ +5% **или** просмотры свежих видео (API) ≥ +5% к прошлому году.
- TikTok = хэштег кандидата в топе CC **или** рост хэштега за 14 дней ≥5% (Trends MCP);
  Amazon = ≥2 товара **или** поиск на Amazon за месяц вырос ≥5% (Trends MCP); бренды = ≥2 ритейлера.
  Рост Trends MCP — «к прошлому периоду», не к прошлому году (90 дней истории), включает сезон.
- **Сезон** (`is_seasonal`): год назад в эти же недели был подъём ≥20% (`SEASON_LIFT`), а рост
  к прошлому году < 5%. **Сначала по Google Trends** (решение пользователя 22.09), если нет ряда — по Pinterest.
- **Календарь сезона и «позже» (LATER)** (пользователь 22.09: «ориентируемся на текущий или предстоящий сезон»):
  `season_calendar()` — месяцы, где сглаженный Google ≥ половины пика, за **чистый год** (104–52 недели назад,
  весенний сбой Google 2026 не попадает); 10+ месяцев = круглый год. Если решение WATCH, а сезон не приходится
  на текущий или 2 ближайших месяца (`SOON_MONTHS`) → LATER с причиной. Порядок: TEST, WATCH, LATER, REJECT.
  Ручной календарь: колонка `season_months` в candidates.csv («5,6,7,8»); lace trim top = лето (решение пользователя).
- **Сезон вот-вот начнётся → «наблюдать» обязательно** (пользователь 22.09, `season_ahead()`): год назад в
  следующие 8 недель (`AHEAD_WEEKS`) интерес вырос на ≥20% (`SEASON_LIFT`), по Google Trends (Pinterest — запасной),
  и рост к прошлому году ≥ −10% (`STEADY_MIN_YOY`). Проверяется до правила «большой спрос».
- **Сезонки не убирать, а наблюдать** (пользователь 22.09; lace trim top и flannel shirt women возвращены): ручное решение WATCH с причиной «сезонка … вернуться
  ближе к сезону» (plaid mini skirt, faux suede skirt, lace trim skirt). Ближе к их сезону — пересмотреть.
- **Сезонные вещи рассматриваем, но сезон ≥ 2 месяцев** (правило пользователя): `season_weeks()` —
  недели подряд вокруг пика не ниже половины пика, сглаживание 3 недели, самый длинный из двух лет,
  без разреза по сентябрю. Меньше 8 недель → REJECT «короткий сезон» поверх любых галочек.
  Хоко-платья (homecoming, 5–6 недель) пользователю не подходят в принципе — вещи «под одно событие» не предлагать.
- **Только стабильно растущие** (правило пользователя): по **Pinterest** последние 8 недель И ≥3 из 4
  последних кварталов выше прошлого года на 5%+. Нет Pinterest-кривой → отказ «рост не проверить».
  Сезонные вещи без роста (стабильные зимние хиты) не рассматриваем — группу «сезонный хит» пользователь отвергла.
- **Google Trends: сбой весной 2026** — почти все слова пикуют в апреле 2026 (даже свитера и осенние
  куртки). Для длинных окон (кварталы, год) Google не использовать, только 8 недель июль–сентябрь.
- **Большой спрос без роста → «наблюдать» (WATCH)** — решение пользователя 22.09.2026 (на примере plaid mini skirt;
  отдельное решение «спрос есть» она отвергла). Пишется `watch_reason`. Условия (`steady_demand()`):
  ≥5000 поисков Amazon в месяц (Trends MCP) **или** ≥5 товаров в хитах; Pinterest не ниже −10%;
  рост поиска Amazon не отрицательный; плюс ≥2 проверок и не короткий сезон.
  На 22.09 сюда попали plaid mini skirt, lace trim skirt, faux suede skirt, flannel shirt women.
- Порядок решения: короткий сезон → стабильный рост? (нет → «наблюдать» при большом спросе, иначе отказ) → голосование каналов.
- **Ручное решение пользователя**: колонки `manual_decision` (TEST/WATCH/REJECT) и `manual_reason` в
  config/candidates.csv. Перекрывает голосование, но на карточке видна плашка «Ручное решение … автоматически
  было бы …», буквы-проверки не трогаются. 22.09: bandana cardigan → TEST («сигнал нового тренда»,
  авто — отказ 1/6). Правила под нужный ответ не подкручивать — для этого есть ручное решение.
- **Сортировка везде** (`sort_candidates()`): тестировать → наблюдать → отказ → отказ с коротким сезоном в самом конце. Причина пишется в `reject_reason`.
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
| Etsy API | ❌ 22.09 ключ приложения «vi» — Banned. Канал закрыт, новых заявок/аккаунтов не предлагать |
| treg.to | ✅ 23.09 `TREG_TOKEN` + `TREG_ORG=vi` в .env; единый ключ к 85 платформам, оплата за запрос с предоплаченного баланса (стартовый $1). Вызов: `GET https://treg.to/call/<endpoint-id>?…` с заголовками `X-Treg-Token`, `X-Treg-Org`; цена — заголовок `X-Treg-Cost-Micro`; каталог `/catalog/platforms[/slug]` бесплатный. Установщик `curl … \| sh` НЕ ставить. Pinterest-поиск, объём поиска Google (DataForSEO), Amazon — ещё не подключены |
| Trends MCP (trendsmcp.ai) | ✅ `TRENDSMCP_API_KEY` в .env; бесплатно 100 запросов/мес, 90 дней истории (2 года — тариф Pro). Журнал расхода `data/logs/trendsmcp_usage.csv`, клиент `src/clients/trendsmcp_client.py`. Google у него совпадает с нашим (корр. 0.82–0.99, `compare_trendsmcp.py`) |
| Pinterest API v5 | ❌ Trial раньше отклоняли, заявку пользователь не подаёт (нет магазина). Раздел Trends в API ЕСТЬ (спека github.com/pinterest/api-description, скоуп `user_accounts:read`): `/trends/keywords/{US}/top/{growing\|monthly\|yearly\|seasonal}` с `interests=womens_fashion`, gender, age; `/trends/product_categories/trending` (FASHION); `/terms/suggested` и `keywords/metrics` — скоуп `ads:read`. Те же данные показывает trends.pinterest.com → берём со страницы через Dolphin. Пример `C:\Users\User\Documents\GitHub\api-quickstart`, `pinterest_auth.py` готов (redirect `http://localhost:8085/`) |
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
- **Графики на карточке** (23.09): кривые Pinterest/Google/Shopping/YouTube + столбики «Amazon · поисков в месяц»
  (сырые ответы Trends MCP, поле volume) и «TikTok США · новых видео в неделю» (12 недель по выборке до 90 видео,
  `run_tiktok_tags.py` листает 3 страницы). Instagram — строкой под графиками.
- **Месячные объёмы (DataForSEO, Trends MCP Amazon) приходят только за закончившиеся месяцы** — текущего месяца
  нет у всех. На графике Google добавляется бледный пунктирный столбик «<месяц> (оценка)» = объём последнего полного
  месяца × (среднее полных недель текущего месяца / среднее недель прошлого) по Google Trends. У Amazon — подпись.
- **Instagram седьмой свидетель** (23.09): I = ≥1 пост в день и последний пост ≤7 дней. Пороги на 7 проверок:
  5–7 тестировать, 3–4 наблюдать, 0–2 отказ (`TEST_MIN`, `WATCH_MIN`).
- **Pinterest-поиск через treg (scrapecreators)** отдаёт только id/ссылки пинов, без дат и сохранений — бесполезен, не подключать.
- **Ответы TikHub обёрнуты дважды** (`data.data.…`) — у Instagram, TikTok Shop; парсить через `data.get("data") or data`.
- **Instagram «recent» у редких хэштегов** отдаёт и старые посты (2017–2021) — частота тогда ≈ 0, это «хэштег мёртвый».
- **Pinterest `/metrics/` → 400**, если end_date = сегодня (данных ещё нет) или в пачке незнакомая фраза:
  брать end_date из собственного запроса страницы, иначе неделя назад; при 400 спрашивать по одной фразе.
- **Google Shopping по узким фразам** почти пустой (нули у ~половины) — такие ряды не учитываются (MIN_NONZERO).
- **Amazon «bought in past month»** — нижняя граница («1K+» = 1000), только 1-я страница (48 товаров),
  раздел `i=fashion`, к фразе дописывается «women». Капча 2 раза → стоп, не обходить. 22.09 капчи не было.
- **bandana cardigan**: ни одной формулировки в Pinterest Trends (bandana/paisley × cardigan/sweater, gap…).
- **Pinterest Trends ≠ поиск Pinterest.** bandana cardigan на pinterest.com ищется отлично (много пинов),
  но раздел трендов по ней ничего не вернул (кривые есть только у достаточно частых запросов) —
  нужна другая формулировка или сигнал из самого поиска Pinterest.
- **Trends MCP**: неделю подписывает её концом (суббота), Google — началом (вс) → сдвиг −6 дней.
  Amazon у него помесячный, TikTok подневный за 30 дн; `no_data` приходит с внутренним statusCode 404
  в теле и квоту не тратит. Ответ `{"statusCode","body":"<JSON-строка>"}` → `trendsmcp_client.rows()`.
- PowerShell 5.1 `Get-Content -Raw | Set-Content` портит кириллицу в .py — править файлы только Edit/Write.
- PowerShell: here-string с `as p:` в python-коде ловится защитой — писать скрипт в файл в scratchpad.

## Что не сделано (по запросу пользователя)

TikTok по кандидатам (Dolphin-поиск или Apify после 15.10), Instagram (Dolphin-скрипт
`instagram_hashtag_dashboard.py` или Graph API), автоподбор кандидатов, чистка шума Google rising,
больше брендов, насыщение рынка, поставщики/маржа, удаление probe_*.py.
