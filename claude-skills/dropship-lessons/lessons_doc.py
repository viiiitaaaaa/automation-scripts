"""Copy the dropship-lessons skill into decor-store-ops/docs/uroki-iz-novostey.md (the reminder file in git)."""
import re, sys
sys.stdout.reconfigure(encoding="utf-8")
skill = open(r"C:\Users\User\.claude\skills\dropship-lessons\SKILL.md", encoding="utf-8").read()
body = re.sub(r"\A---.*?---\s*", "", skill, flags=re.S)
body = body.replace("# Уроки из новостей (записано по просьбе пользователя 27.09.2026)",
                    "# 📌 Не забыть: уроки из новостей для запуска магазина")
head = ("> Отобрано владелицей с панели новостей 27.09.2026. Источник правды — скилл `dropship-lessons` "
        "(`~/.claude/skills/dropship-lessons/SKILL.md`), этот файл — его копия в проекте, обновляется вместе с ним.\n"
        "> На панели новостей эти посты отмечены «📌 Принято к сведению», сверху — блок «Не забыть».\n"
        "> Ссылки вида `канал/номер` — это посты `https://t.me/канал/номер`.\n\n")
lines = body.split("\n", 1)
out = lines[0] + "\n\n" + head + lines[1].lstrip("\n")
open(r"C:\Users\User\decor-store-ops\docs\uroki-iz-novostey.md", "w", encoding="utf-8").write(out)
print(out[:600])
