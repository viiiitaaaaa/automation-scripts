"""Блок панели «Книги — всё целиком» (её просьба 09.10: «маловато инфы и приёмов»).

Берёт конспекты купленных книг из knowledge-library и строит panel_books_full.html:
  1) все приёмы «Что применяем у нас», сгруппированные по скиллам (с книгой-источником);
  2) по каждой книге — полный конспект глав, все приёмы и «Чего НЕ брать».
news.py вставляет файл в панель сразу после panel_books.html. Запуск: python build_books.py
"""
import html
import re
from pathlib import Path

import markdown

BASE = Path(__file__).parent
KNIGI = Path.home() / ".claude" / "skills" / "knowledge-library" / "references" / "knigi"
SKILLS = {p.name for p in (Path.home() / ".claude" / "skills").iterdir() if p.is_dir()}
OUT = BASE / "panel_books_full.html"

DOP = KNIGI / "dop"   # второе прочтение оригиналов (09.10, «ты ещё раз прочти книги»)
DOP3 = KNIGI / "dop3"   # третье прочтение (09.10, «делай прогон в третий раз»)
# (короткое имя, файлы первого конспекта, файлы второго прочтения в dop\) — порядок как в блоке «Книги»
BOOKS = [
    ("Marketing Management (Котлер)", ["kotler_marketing_management_1.md", "kotler_marketing_management_2.md"],
     ["kotler_mm_a.md", "kotler_mm_b.md", "kotler_mm_c.md"]),
    ("Marketing (Grewal)", ["grewal_marketing_1.md", "grewal_marketing_2.md"], ["grewal_a.md", "grewal_b.md"]),
    ("Французский учебник Vuibert", ["french_marketing_strategique_operationnel.md"], ["french_vuibert.md"]),
    ("10 смертных грехов (Котлер)", ["kotler_10_grehov.md"], ["kotler_10_grehov.md"]),
    ("Marketing (Трейси)", ["tracy_marketing.md"], ["tracy_marketing.md"]),
    ("Marketing 4.0", ["kotler_marketing_4_0.md"], ["kotler_4_0.md"]),
    ("Marketing 6.0", ["kotler_marketing_6_0.md"], ["kotler_6_0.md"]),
    ("Marketing 7.0", ["kotler_marketing_7_0.md"], ["kotler_7_0.md"]),
    ("Strategy in the Digital Age", ["kotler_digital_age.md"], ["kotler_digital_age.md"]),
    ("Entrepreneurial Marketing", ["kotler_entrepreneurial_marketing.md"], ["kotler_entrepreneurial.md"]),
    ("SEO 2025 (Clarke)", ["seo_2025_clarke.md"], ["seo_2025_clarke.md"]),
    ("Step-by-Step SEO (Davidson)", ["seo_davidson_2013.md"], ["seo_davidson_2013.md"]),
    ("Social Media Marketing", ["social_media_marketing.md"], ["social_media_marketing.md"]),
    ("SaaS Marketing Playbook", ["saas_marketing_playbook.md"], ["saas_marketing_playbook.md"]),
    ("Design Matters: Portfolios", ["design_matters_portfolios.md"], ["design_matters_portfolios.md"]),
    ("Mastering Claude AI (Dickey)", ["mastering_claude_ai_dickey.md"], ["mastering_claude_ai_dickey.md"]),
    ("Claude Code (Мукминов)", ["claude_code_mukminov.md"], ["claude_code_mukminov.md"]),
]
DOP_PARTS = ["Главные тезисы", "Новые приёмы", "Модели и чек-листы целиком", "Цифры и факты", "Кейсы",
             "Расходится с её решениями"]


def dop_sections(text):
    """разделы второго прочтения по заголовкам «## …»"""
    parts, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m and not line.startswith("###"):
            cur = next((p for p in DOP_PARTS if m.group(1).startswith(p)), m.group(1))
            parts.setdefault(cur, "")
        elif cur:
            parts[cur] += line + "\n"
    return parts

APPLY_RE = re.compile(r"^#{1,2} Что применяем", re.M)
NOT_RE = re.compile(r"^#{1,2} Чего НЕ брать", re.M)
ITEM_RE = re.compile(r"^\s{0,3}(\d+)\.\s+(.*)")
MD = lambda t: markdown.markdown(t, extensions=["tables", "sane_lists"])


def inline(t):
    """markdown одного пункта без обёртки <p>"""
    h = MD(t).strip()
    return h[3:-4] if h.startswith("<p>") and h.endswith("</p>") and h.count("<p>") == 1 else h


def split(text):
    a, n = APPLY_RE.search(text), NOT_RE.search(text)
    if not a:
        return text, "", ""
    body = text[:a.start()]
    apply_ = text[a.end():n.start()] if n else text[a.end():]
    not_ = text[n.end():] if n else ""
    return body, apply_.split("\n", 1)[1] if "\n" in apply_ else apply_, not_.split("\n", 1)[1] if "\n" in not_ else not_


def items(apply_md):
    """пункты «N. …» с продолжением строк; группа = последний подзаголовок или жирная строка"""
    out, cur, group = [], None, ""
    for line in apply_md.splitlines():
        s = line.strip()
        if s.startswith("#") or (s.startswith("**") and s.endswith("**") and len(s) < 90):
            group = s.lstrip("#").strip().strip("*").strip()
            cur = None
            continue
        m = ITEM_RE.match(line)
        if m:
            cur = {"group": group, "text": m.group(2)}
            out.append(cur)
        elif cur is not None and s and not s.startswith("---"):
            cur["text"] += " " + s
        elif not s:
            pass
    return out


def skills_of(t):
    tail = t[t.find("→"):] if "→" in t else ""
    found = [s for s in re.findall(r"[a-z][a-z0-9-]+(?::[a-z-]+)?", tail) if s in SKILLS]
    return list(dict.fromkeys(found)) or ["(без скилла)"]


def main():
    by_skill, books_html, total, total2 = {}, [], 0, 0
    for name, files, dops in BOOKS:
        bodies, applies, nots, its = [], [], [], []
        for f in files:
            text = (KNIGI / f).read_text(encoding="utf-8")
            b, a, n = split(text)
            bodies.append(b); applies.append(a); nots.append(n)
            its += items(a)
        total += len(its)
        for it in its:
            for sk in skills_of(it["text"]):
                by_skill.setdefault(sk, []).append((name, it))
        # второе прочтение: склеиваем одноимённые разделы всех частей книги
        dp = {}
        for f in dops:
            if (DOP / f).exists():
                for k, v in dop_sections((DOP / f).read_text(encoding="utf-8")).items():
                    dp[k] = dp.get(k, "") + v
        dp3 = {}   # третье прочтение (её просьба 09.10 «делай прогон в третий раз»)
        for f in dops:
            if (DOP3 / f).exists():
                for k, v in dop_sections((DOP3 / f).read_text(encoding="utf-8")).items():
                    dp3[k] = dp3.get(k, "") + v
        its3 = items(dp3.get("Новые приёмы", ""))
        total2 += len(its3)
        for it in its3:
            for sk in skills_of(it["text"]):
                by_skill.setdefault(sk, []).append((name + " · 3-е чтение", it))
        li3 = "".join(
            (f'<li><span class="grp">{html.escape(it["group"])}</span> ' if it["group"] else "<li>") + inline(it["text"]) + "</li>"
            for it in its3)
        third = "" if not dp3 else (
            f'<details class="bkf-sub" open><summary>Третье прочтение: новые приёмы — {len(its3)}</summary><ol class="bkf-list">{li3}</ol></details>'
            + "".join(f'<details class="bkf-sub"><summary>Третье прочтение: {p.lower()}</summary><div class="bkf-md">{MD(dp3[p])}</div></details>'
                      for p in DOP_PARTS if p != "Новые приёмы" and dp3.get(p, "").strip()))
        its2 = items(dp.get("Новые приёмы", ""))
        total2 += len(its2)
        for it in its2:
            for sk in skills_of(it["text"]):
                by_skill.setdefault(sk, []).append((name + " · 2-е чтение", it))
        li = "".join(
            (f'<li><span class="grp">{html.escape(it["group"])}</span> ' if it["group"] else "<li>") + inline(it["text"]) + "</li>"
            for it in its)
        li2 = "".join(
            (f'<li><span class="grp">{html.escape(it["group"])}</span> ' if it["group"] else "<li>") + inline(it["text"]) + "</li>"
            for it in its2)
        second = ""
        if dp:
            second = (f'<details class="bkf-sub" open><summary>Второе прочтение: главные тезисы</summary><div class="bkf-md">{MD(dp.get("Главные тезисы", ""))}</div></details>'
                      f'<details class="bkf-sub" open><summary>Второе прочтение: новые приёмы — {len(its2)}</summary><ol class="bkf-list">{li2}</ol></details>'
                      + "".join(f'<details class="bkf-sub"><summary>{p}</summary><div class="bkf-md">{MD(dp[p])}</div></details>'
                                for p in DOP_PARTS[2:] if dp.get(p, "").strip()))
        books_html.append(
            f'<details class="bkf-book"><summary><b>{html.escape(name)}</b>'
            f'<span class="bkf-n">{len(its) + len(its2) + len(its3)} приёмов'
            + (f' (2-е чтение +{len(its2)}, 3-е +{len(its3)})' if its2 or its3 else "")
            + f' · {sum(len(b) for b in bodies) // 1000} тыс. знаков конспекта</span></summary>'
            + second + third +
            f'<details class="bkf-sub"><summary>Первое прочтение: что применяем у нас — {len(its)}</summary><ol class="bkf-list">{li}</ol></details>'
            f'<details class="bkf-sub"><summary>Конспект по главам целиком</summary><div class="bkf-md">{"".join(MD(b) for b in bodies)}</div></details>'
            f'<details class="bkf-sub"><summary>Чего НЕ брать</summary><div class="bkf-md">{"".join(MD(n) for n in nots)}</div></details>'
            f'<p class="bkf-file">Файл: {" + ".join(files)}</p></details>')

    order = sorted(by_skill, key=lambda s: (s == "(без скилла)", -len(by_skill[s])))
    skills_html = "".join(
        f'<details class="bkf-book"><summary><code>{html.escape(sk)}</code><span class="bkf-n">{len(by_skill[sk])} приёмов</span></summary>'
        f'<ol class="bkf-list">' + "".join(
            f'<li><span class="src">{html.escape(b)}</span> {inline(it["text"])}</li>' for b, it in by_skill[sk]) + "</ol></details>"
        for sk in order)

    OUT.write_text(f"""  <style>
    #books-all .bkf-book {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; margin-bottom: 8px; padding: 0 16px; }}
    #books-all .bkf-book > summary {{ cursor: pointer; padding: 12px 0; display: flex; gap: 10px; align-items: baseline; flex-wrap: wrap; font-size: 15px; }}
    #books-all .bkf-n {{ font: 500 11.5px "JetBrains Mono", monospace; color: var(--muted); }}
    #books-all .bkf-sub {{ border-top: 1px solid var(--border-soft); padding: 4px 0; }}
    #books-all .bkf-sub > summary {{ cursor: pointer; padding: 8px 0; font-weight: 600; font-size: 13.5px; color: var(--tool); }}
    #books-all .bkf-list {{ font-size: 13.5px; color: var(--ink-soft); padding-left: 24px; margin: 4px 0 14px; }}
    #books-all .bkf-list li {{ margin-bottom: 7px; }}
    #books-all .grp, #books-all .src {{ font: 600 10.5px "JetBrains Mono", monospace; text-transform: uppercase; color: var(--muted);
                                        background: var(--border-soft); border-radius: 6px; padding: 1px 6px; }}
    #books-all .bkf-md {{ font-size: 13.5px; color: var(--ink-soft); max-width: 900px; overflow-x: auto; padding-bottom: 12px; }}
    #books-all .bkf-md h1 {{ font-size: 20px; margin: 10px 0; }} #books-all .bkf-md h2 {{ font-size: 18px; margin: 18px 0 8px; }}
    #books-all .bkf-md h3, #books-all .bkf-md h4 {{ font-size: 15px; margin: 14px 0 6px; font-family: "Work Sans", sans-serif; }}
    #books-all .bkf-md table {{ border-collapse: collapse; font-size: 12.5px; }}
    #books-all .bkf-md td, #books-all .bkf-md th {{ border: 1px solid var(--border); padding: 4px 8px; vertical-align: top; }}
    #books-all .bkf-file {{ font: 500 11px "JetBrains Mono", monospace; color: var(--muted); margin: 0 0 12px; }}
    #books-all h3.bkf-h {{ font-size: 20px; margin: 22px 0 10px; }}
  </style>
  <section id="books-all">
    <div class="section-head"><h2>Книги — все приёмы и конспекты целиком</h2><span class="count">{total + total2} приёмов ({total} первое чтение + {total2} второе и третье) · 17 книг</span></div>
    <p class="section-note">Собирается скриптом <code>build_books.py</code> прямо из конспектов, ничего не сокращено. Нажми на строку, чтобы раскрыть.
    Один приём может стоять у нескольких скиллов.</p>
    <h3 class="bkf-h">Все приёмы по скиллам</h3>
    {skills_html}
    <h3 class="bkf-h">По книгам: все приёмы, конспект глав, чего не брать</h3>
    {"".join(books_html)}
  </section>
""", encoding="utf-8")
    print(f"{OUT.name}: приёмов {total} + второе чтение {total2}, скиллов {len(by_skill)}, {OUT.stat().st_size // 1024} КБ")
    for sk in order:
        print(f"  {sk}: {len(by_skill[sk])}")


if __name__ == "__main__":
    main()
