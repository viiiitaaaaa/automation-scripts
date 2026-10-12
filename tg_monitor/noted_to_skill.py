"""Память «принято к сведению»: все заметки notes.json с пометкой noted → скилл noted-news (SKILL.md + принятое.md).
Её правило 07.10: «принятые к сведению новости не выводи в дашборд — сохраняй в отдельный скилл и скрипт памяти;
на дашборде только новые, ранее не принятые». Запуск после каждой новой пометки noted: python noted_to_skill.py
Файлы пересобираются целиком, notes.json не меняется."""
import json, os, sqlite3, sys

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.expanduser(r"~\.claude\skills\noted-news")
WHEN_ORDER = ["Всегда: кому можно отдавать данные", "Всегда: лимит Claude и чужие скиллы", "Экономика товара и теста",
              "Реклама и креативы", "Платежи, корзина, каналы", "После запуска рекламы", "Страны и доставка",
              "Когда будет время (инструменты)"]

notes = json.load(open(os.path.join(HERE, "notes.json"), encoding="utf-8"))
db = sqlite3.connect(os.path.join(HERE, "tg_monitor.db"))
dates = {f"{c}/{i}": d[:10] for c, i, d in db.execute("SELECT channel, post_id, post_date FROM posts")}
dates.update({f"{c}/{i}": d[:10] for c, i, d in db.execute("SELECT chat, msg_id, date FROM chat_msgs")})
nums_file = os.path.join(HERE, "post_numbers.json")
nums = json.load(open(nums_file, encoding="utf-8")) if os.path.exists(nums_file) else {}
nums = nums.get("numbers", nums) if isinstance(nums, dict) else {}

groups = {}
for k, v in notes.items():
    if isinstance(v, dict) and v.get("noted"):
        groups.setdefault(v.get("when", "Другое"), []).append((dates.get(k, ""), k, v))
order = sorted(groups, key=lambda w: WHEN_ORDER.index(w) if w in WHEN_ORDER else len(WHEN_ORDER))
total = sum(map(len, groups.values()))

full = ["# Принято к сведению из новостей — полный текст\n\n",
        "Собирается автоматически (`tg_monitor/noted_to_skill.py`) из notes.json (пометка `noted`). На панель новостей "
        "это больше не выводится (решение 07.10).\n"]
index = []
for w in order:
    items = sorted(groups[w], reverse=True)
    full.append(f"\n# {w}\n")
    index.append(f"\n### {w} ({len(items)})\n")
    for d, k, v in items:
        title = v.get("noted_title") or v.get("headline", k)
        num = f"пост {nums[k]} · " if isinstance(nums.get(k), (int, str)) and nums.get(k) else ""
        full.append(f"\n## {title}\n{num}{d} · [источник](https://t.me/{k}) · `{k}`\n\n")
        full += [s + "\n\n" for s in v.get("summary", [])]
        if v.get("for_us"):
            full.append(f"**Для нас:** {v['for_us']}\n\n")
        full.append(f"**📌 Принято:** {v['noted']}\n")
        if v.get("installed"):
            full.append(f"\n✓ Установлено: {v['installed']}\n")
        index.append(f"- {title} — {v['noted']} ([{k}](https://t.me/{k}))\n")

os.makedirs(SKILL, exist_ok=True)
open(os.path.join(SKILL, "принятое.md"), "w", encoding="utf-8").write("".join(full))
head = f"""---
name: noted-news
description: "Память «принято к сведению» из Telegram-новостей — {total} уроков и инструментов, которые она отметила с панели (экономика товара, реклама, платежи, страны, данные, лимиты Claude, инструменты «когда будет время»). Используй, когда просят «что мы приняли к сведению», «что было в новостях про …», «напомни уроки из новостей», «что я отмечала», перед решениями по рекламе, ценам, платежам, доставке, новой стране, установке инструментов, и при разборе новостей — чтобы не показывать повторно уже принятое. Триггеры: \\"принято к сведению\\", \\"что я отмечала\\", \\"напомни из новостей\\", \\"принятые новости\\", \\"память новостей\\"."
---

# Принято к сведению из новостей (память)

Её правило 07.10: принятые к сведению новости **на панель новостей не выводятся** — хранятся здесь. На панели только
новые, ещё не принятые и не прочитанные.

- Этот файл и `принятое.md` (полный текст карточек) **пересобираются скриптом** `C:\\Users\\User\\tg_monitor\\noted_to_skill.py`
  из `notes.json` (пометка `noted`, группа `when`). Руками не править — править заметку в notes.json и перезапустить.
- Новая карточка, которую она переслала с панели = «принято к сведению»: в notes.json дописать `"noted": "что берём"`,
  `"when": "<группа ниже>"` → `python noted_to_skill.py` → `python news.py --build` (карточка уходит с панели) →
  дальше процедура скилла dropship-lessons (урок в нужный раздел, GitHub, применить к делу).
- Когда нужен подробный текст урока — открыть `принятое.md` и найти по заголовку или ключу `канал/номер`.
- При разборе новых постов: если новость повторяет уже принятое — `skip` (дубль), не показывать снова.
- Изучение ссылок принятого (12.10): помощникам на чтение статей, доков, уроков курсов, кода GitHub — `model: sonnet`,
  на сбор ссылок со страниц `?embed=1` — `model: haiku`; решение «ставить / 🟢🟡🔴» и правка скиллов/скриптов — Opus.
  В брифе: что сделать, формат ответа, «готово» = файл; без «подумай / шаг за шагом».

## Оглавление — всего {total}
"""
open(os.path.join(SKILL, "SKILL.md"), "w", encoding="utf-8").write(head + "".join(index))
print(f"noted-news: принято к сведению {total}, групп {len(groups)}")
