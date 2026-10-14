---
name: artmellio-system
description: "Связка инструментов вокруг магазина ARTMELLIO — репозиторий artmellio-system, роли Shopify / Cursor / Claude Code / n8n / ComfyUI / GitHub, этапы сборки по PDF-плану и их состояние. Используй, когда просят \"продолжаем ARTMELLIO\", \"собрать связку\", \"настроить n8n\", \"этап такой-то\", \"структура проекта\", \"какие ветки\", \"куда класть скрипты\". Триггеры: \"artmellio система\", \"связка программ\", \"n8n\", \"оркестратор\", \"этапы сборки\", \"продолжаем артмеллио\"."
---

# Система ARTMELLIO: связка инструментов

План: `C:\Users\User\Downloads\Ты тут__5916124473984317705.pdf` — 10 этапов плюс
расписание по неделям. Страница с разбором плана:
https://claude.ai/code/artifact/7d31149d-ae55-4bbd-a9a1-89451a2eec35

Коротко: **Shopify хранит бизнес, Cursor и Claude Code строят код, n8n всё
связывает, ComfyUI делает визуалы.**

## Роли

| Инструмент | Роль | Граница |
|---|---|---|
| Shopify | товары, коллекции, метаполя, заказы, витрина | источник правды о товаре |
| Shopify Flow | trigger → condition → action | только внутри Shopify |
| Cursor | тема, секции, schema, CSS, JS | ручная работа с кодом |
| Claude Code | рефакторинг, скрипты, импортеры, API | большие задачи в терминале |
| n8n | webhooks, cron, очереди, уведомления | всё, что между сервисами |
| ComfyUI | генерация визуалов | только картинки |
| Sheets / Notion | тренды, боли, статусы | человеческий слой |
| GitHub | версии, ветки, история | память проекта |

**Правило разделения:** действие целиком внутри Shopify → Flow. Выходит наружу → n8n.

## Репозиторий

`C:\Users\User\decor-store-ops`, приватный на GitHub: `viiiitaaaaa/decor-store-ops`.

```
shopify-theme/      живая тема (Dawn 16, сильно доработана)
scripts/
  audit/            сверка магазина с курсом
  content-prep/     SEO, страницы, политики
  metafields/       определения и заливка метаполей
  importer/         AliExpress, отзывы, сопоставление, браузер
  theme/            правки темы скриптами
comfyui-workflows/  воркфлоу в JSON
n8n/exports/        воркфлоу n8n — версионировать здесь
data/               trend-board, voc, products
docs/               план, backlog темы, лекция
.cursor/rules/      правила для Cursor
```

Правила проекта — `AGENTS.md` в корне, на него ссылаются `CLAUDE.md` и
`.cursor/rules/artmellio.mdc`. Cursor открывается командой `cursor C:\Users\User\decor-store-ops`.

Ветки: `main` — то, что в магазине; `dev` — собранные правки;
`feature/…` — одна задача. Есть `feature/remove-tax-note` (правки карточки,
залито на превью), плюс заготовки `feature/pairs-well-with`,
`feature/mobile-sticky-atc`, `feature/product-details-metafields`.

## Состояние этапов

| Этап | Что | Состояние |
|---|---|---|
| 1 | Фундамент: репозиторий, структура, правила, ветки, копия темы | **готово** |
| 2 | Shopify как ядро: метаполя, статусы, коллекции, Flow | **готово** |
| 3 | Тема магазина | **основное закрыто** — блок Details, липкая кнопка, значки платежей; остаток в `docs/theme-backlog.md` |
| 4 | n8n как центр | **каркас готов** — установлен, 4 воркфлоу, связь проверена; поверх — операционная панель `panel/` (03.09.2026) |
| 5 | ComfyUI как production engine | не начат |
| 6 | База трендов | не начат |
| 7 | База болей покупателей | не начат |
| 8 | Контент и публикация | не начат |
| 9 | Система approval | частично: процессы Flow созданы неактивными |
| 10 | Очерёдность запуска | — |

Что именно сделано по магазину — в скилле [[dropship-audit]], там же список
оставшихся доработок.

## Операционная панель (03.09.2026)

Второй плановый документ — ТЗ «Art Melio Operations System»
(`docs/operations-system-spec.md`, карта соответствия
`docs/operations-system-map.md`). Это интерфейсный слой поверх n8n, план
не заменяет.

MVP лежит в `panel/` на ветке `feature/operations-panel`: `server.py` на
stdlib Python, `index.html`, `registry.json` (реестр сценариев — единственное,
что правится при добавлении сценария). Запуск: `.\n8n\start-n8n.ps1`, затем
`.\panel\start-panel.ps1`, панель на http://localhost:8787.

Кнопка бьёт в вебхук `panel/<имя>` — узел «Кнопка в панели» с
`responseMode: lastNode`. Отвечает только у **включённого** воркфлоу.
Включены `artmSelfTest001`, `artmDailyRep001`, `artmOrdersRec01` (последние
заказы, кнопка), `artmMarkupQ001` (очередь разметки: 20 товаров с пустыми
метаполями + ссылки в админку; владелец размечает сам, на 03.09 осталось 696
из 786) и `artmOrderNew001` (`orders/create` → уведомление в панель
через `POST 127.0.0.1:8787/api/notify`, именно 127.0.0.1 — на localhost
n8n даёт EACCES по IPv6). Событийные `products/update`, `collections/update`
выключены, кнопки у них нет. После `n8n publish:workflow`
n8n нужно перезапустить. Сразу после старта n8n ~1 минуту отдаёт 503
«Database is not ready» — подождать строку «Editor is now accessible».

Проверено 03.09: все кнопки и уведомление о заказе (примером) отработали.
Магазин отвечает **856 товаров, USD** (в августе 131, PLN); сводка читает
весь каталог — метаполя заполнены только у первой сотни. Заказов в магазине
пока ноль.

**Публичный адрес — бесплатный туннель Cloudflare**, решение владельца
03.09 (хостинг отложен, бюджет ограничен). `.\n8n\start-tunnel.ps1` поднимает
`cloudflared` quick tunnel и сам перерегистрирует вебхуки Shopify через
`scripts/webhooks/register_shopify_webhooks.py` (адрес меняется при каждом
запуске). По умолчанию регистрируются `ORDERS_CREATE,PRODUCTS_UPDATE` (владелец дал
«да» на автотег 03.09); `COLLECTIONS_UPDATE` добавлять флагом `-Topics`,
только когда воркфлоу включён. Автотег `needs:data`: `10-products-update-gaps`
идемпотентен (add/remove/none), кнопка «Пометить всё неразмеченное»
(`70-markup-tag-all`) сверяет весь каталог; 03.09 помечено 696 из 786.
Долгие Code-узлы с сотнями запросов — оборачивать `httpRequest` в повтор:
Shopify даёт ECONNRESET. Три окна: start-n8n, start-tunnel, start-panel.
**PS-скрипты сохранять с UTF-8 BOM** — иначе PowerShell 5.1 ломает русские
строки в кавычках (ParserError).

**04.09.2026:** панель принимает отчёты (`POST /api/report` → `data/reports/*.xlsx`
и `.csv`, блок «Отчёты»), сбои любого воркфлоу уходят в панель и Telegram через
Error Workflow `05-error-alert` (`settings.errorWorkflow` у всех), появился раздел
«Поставщики»: `80-supplier-check` (Execute Command → `scripts/suppliers/check_suppliers.py`,
Dsers через Dolphin-профиль 859648353, метаполя `artmellio.supplier_check/supplier_cost/
supplier_checked_at`, тег `supplier:unavailable`, 10–15 мин) и `85-supplier-draft`
(снять недоступные с продажи, с подтверждением). В n8n 2.x Execute Command выключен
по умолчанию — `NODES_EXCLUDE='[]'` в `start-n8n.ps1`. После правки коллекций —
`scripts/collections/reconcile_leftover.py` (контроль «пересечение 11 ∩ N: 0»).

## Этап 4: n8n — что уже стоит (26.08.2026)

**Установлен**, версия 2.36.7, панель http://localhost:5678, база SQLite в
`C:\Users\User\.n8n`. Запуск — `.\n8n\start-n8n.ps1`, проверка связи —
`.\n8n\selftest.ps1`. Подробности и грабли — `n8n/README.md` в репозитории.

**Развилка с токеном решена без постоянного токена и без браузера:** каждый
воркфлоу первым узлом сам выпускает свежий по client credentials. Ключи берутся
из переменных окружения, в репозиторий не попадают.

Четыре воркфлоу импортированы и **выключены**: `00-selftest-token`,
`10-products-update-gaps` (тег `needs:data` по пустым метаполям),
`20-daily-catalog-report` (утренняя сводка), `30-collections-update`
(коллекция без баннеров). Связь проверена насквозь: n8n получил из Shopify
ARTMELLIO / PLN / 131 товар.

**Осталось по этапу:** туннель, чтобы Shopify достучался до localhost, и
регистрация самих вебхуков; уведомление о новом заказе.

## Этап 4: справочно — как выбирали

Ставится последним из инструментов: оркестратору нужно, чтобы связываемое уже
существовало и имело стабильные точки входа.

```powershell
npm install -g n8n
n8n start          # панель на http://localhost:5678
```

**Оговорка:** на машине Node 24, n8n официально поддерживает 20 и 22. Скорее
всего запустится с предупреждением. Если начнёт падать — Docker Desktop и
контейнер. Docker не установлен и заранее не нужен.

Первые сценарии, которые окупаются:

1. **Новый заказ → уведомление.** Webhook Shopify → фильтр → Telegram или почта.
2. **Товар без метаполей → задача.** Cron раз в сутки → Admin API → строка в таблице.
3. **Очередь пересъёмки фото.** Метка «нужна пересъёмка» → задача в ComfyUI →
   готовая картинка обратно в Shopify.
4. **`products/update`** — то, что Flow не умеет: реакция на изменение товара
   (например, проставили `approved_for_publish`).
5. **`collections/update`** — тоже мимо Flow, триггеров по коллекциям там нет.

Экспорт каждого рабочего воркфлоу класть в `n8n/exports/` и коммитить — это
единственный способ их версионировать.

**Главная развилка при подключении n8n к Shopify.** Наш токен Admin API живёт
24 часа (client credentials). Для ручной работы это нормально — `shop.ps1`
перевыпускает сам. Но n8n работает круглосуточно и встанет через сутки.
Варианты: шаг перевыпуска токена перед каждым запросом внутри воркфлоу, либо
custom app с постоянным токеном. Второе проще.
Узел Shopify в n8n подключать **только по токену, не по OAuth** — OAuth открывает
системный Chrome, а он для этого магазина запрещён.

## Команды

```powershell
# Shopify CLI — только через обёртку, она подставляет токен
& C:\Users\User\dolphin_anty\shop.ps1 theme list
& C:\Users\User\dolphin_anty\shop.ps1 theme dev --path .\shopify-theme
& C:\Users\User\dolphin_anty\shop.ps1 theme check --path .\shopify-theme
```

**Живая тема — `artmellio-live` (`188850930044`)**, опубликована 26.08.2026.
Прежняя live `artmellio-theme/main` (`188705603964`) цела и годится для отката.
Чужую `decor-shell-theme-v3` (`188704358780`) не трогать.

Работа с темой — своими скриптами, не CLI:

```powershell
python scripts\theme\sync_live_theme.py            # живая тема -> репозиторий
python scripts\theme\push_files.py sections\x.liquid   # точечная заливка
```

`theme push` затирает тему целиком, поэтому правки идут через `themeFilesUpsert`.

## Грабли

- **`dev` дважды оказывалась отставшей** от `main`, и фича-ветки уходили без темы
  и скриптов. Отпочковывать от актуальной `main`, либо сначала подтянуть `dev`.
- **`git push` в этой сессии блокировался разрешениями** — ветка `dev` и часть
  коммитов остались только локально. Пушить пользователю самому.
- **Вход в Shopify только через профиль Dolphin `859648353`.** Системный Chrome
  запрещён, `shopify app` и `shopify store auth` заблокированы обёрткой.
- **В live-тему публиковать только вручную.** Автоматически — никогда.

Связано: [[dropship-audit]], [[shopify-admin-api-dostup]],
[[shopify-cli-tolko-po-tokenu]], [[dolphin-vstroennye-prilozheniya]]
