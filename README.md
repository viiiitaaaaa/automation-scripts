# automation-scripts

Личный архив рабочих скриптов и автоматизаций (Python/JS/PowerShell), собранных в разных проектах.

## Структура

- `dolphin_anty/` — автоматизация антидетект-браузера Dolphin{anty}: профили, скрины магазинов, импорт в Dsers, поиск ссылок товаров, дашборды Instagram/TikTok
- `fashion-trend-radar/` — мультиканальный тренд-радар женской одежды: Google Trends и YouTube-поиск за 2 года, Pinterest Trends, TikTok Creative Center, YouTube Data API, Amazon, новинки брендов, подсказки поиска → решение «тестировать / наблюдать / отказ» с меткой сезона и дашборд с кривыми. Логика и статусы — `fashion-trend-radar/TZ_trend_scoring.md` и скилл `claude-skills/trend-radar`
- `tg_monitor/` — мониторинг публичных Telegram-каналов через веб-версию t.me/s/
- `claude-skills/` — набор Claude Code skills, написанных для этих задач
- `wb-tools/` — скрипты под Wildberries (парсинг, рейтинги, отчёты)
- `my-bot/` — браузерная автоматизация (JS/Playwright) под разные отчёты и загрузки
- `downloads-scripts/` — разрозненные разовые скрипты (аналитика топов, скриншоты, транскрибация и т.д.)

## Секреты

Ни один файл в репозитории не содержит реальных токенов/паролей. Все credentials передаются через `.env` (см. `.env.example` в соответствующих папках) или читаются из файлов вне репозитория.
