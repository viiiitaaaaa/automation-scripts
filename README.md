# automation-scripts

Личный архив рабочих скриптов и автоматизаций (Python/JS/PowerShell), собранных в разных проектах.

## Структура

- `dolphin_anty/` — автоматизация антидетект-браузера Dolphin{anty}: профили, скрины магазинов, импорт в Dsers, поиск ссылок товаров, дашборды Instagram/TikTok
- `fashion-trend-radar/` — парсинг трендов (Google Trends/Pinterest/TikTok через Bright Data) и подбор товаров AliExpress (Apify/Dolphin)
- `tg_monitor/` — мониторинг публичных Telegram-каналов через веб-версию t.me/s/
- `claude-skills/` — набор Claude Code skills, написанных для этих задач
- `wb-tools/` — скрипты под Wildberries (парсинг, рейтинги, отчёты)
- `my-bot/` — браузерная автоматизация (JS/Playwright) под разные отчёты и загрузки
- `downloads-scripts/` — разрозненные разовые скрипты (аналитика топов, скриншоты, транскрибация и т.д.)

## Секреты

Ни один файл в репозитории не содержит реальных токенов/паролей. Все credentials передаются через `.env` (см. `.env.example` в соответствующих папках) или читаются из файлов вне репозитория.
