# Система знаний — план (12.10.2026)

## Готово =
1. Скилл `znaniya` (C:\Users\User\.claude\skills\znaniya): SKILL.md + `katalog.py` + `poisk.py` + `sobytiya.json`.
   - `python poisk.py "запрос"` — ищет по всем скиллам, принятому (notes.json), книгам/курсам; ответ со ссылками на источник.
   - `python katalog.py [--send]` — страница `C:\Users\User\tg_monitor\katalog_umeniy.html`: что умеем (скиллы + фразы),
     принятое со статусами ✅ применено / ⏳ ждёт события / ❌ отказались, привязка к событиям; `--send` — файлом в бот.
2. У всех принятых пунктов есть статус (авто по полям + ручные правки `statusy.json`).
3. Глобальный CLAUDE.md: правило «новый проект → сначала каталог и принятое по событию».
4. Копии: память → GitHub (artmellio-skills/memory) через sync_skills.ps1; tg_monitor.db → Google Диск; tg-news в конце
   цикла: копия в automation-scripts + sync_skills.ps1 + каталог пересобрать.
5. Память: запись про систему знаний. Каталог отправлен в бот.

## Чеклист (всё сделано 12.10)
- [x] поля notes.json (noted/when/installed/declined) — посмотреть
- [x] sobytiya.json: событие → группы принятого + скиллы
- [x] katalog.py, poisk.py, SKILL.md
- [x] статусы — проверить раскладку, ручные правки (✅ 50 / ⏳ 139 / ❌ 4)
- [x] CLAUDE.md
- [x] sync_skills.ps1 + память, база на Диск
- [x] tg-news шаг 4б «в конце»
- [x] память, GitHub, отправка в бот
- [ ] ждёт её слова: автоматический ежедневный разбор новостей
