"""
Новости из Telegram одной командой: собрать новые посты -> собрать панель news_panel.html.

    python news.py           # сбор + панель
    python news.py --build   # только пересобрать панель (после правки notes.json)

База tg_monitor.db ничего не удаляет; на панели — последние WINDOW_DAYS дней.
Пересказы (заголовок, суть, «для нас») лежат в notes.json под ключом "канал/номер":
    {"cat": "biz" | "tool" | "soft" | "skip", "headline": ..., "summary": [...], "for_us": ...}
cat=skip — пост просмотрен, в «Главное» не идёт (но остаётся в ленте).
После сбора скрипт печатает новые посты без пересказа — их нужно разобрать.
"""
import html
import json
import re
import sqlite3
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

import tg_monitor as tm

BASE = Path(__file__).resolve().parent
NOTES = BASE / "notes.json"
STATE = BASE / "panel_state.json"
EXTRA = BASE / "panel_extra.html"
OUT = BASE / "news_panel.html"
WINDOW_DAYS = 45        # на панели; в базе хранится всё
CATCHUP_DAYS = 31       # насколько далеко назад догонять пропущенные посты
MAX_PAGES = 6           # страниц t.me/s/ на канал за один сбор (по ~20 постов)

CATS = {"biz": "по делу — shopify / дропшиппинг / тренды",
        "tool": "лично тебе — claude code / инструменты",
        "soft": "фоново"}
QUIET = {  # каналы, которые не разбираем подробно
    "irina_agafonova_ved": "Импорт из Китая и комплаенс Wildberries — доступа к WB сейчас нет, оставлено под общие новости e-commerce.",
    "python_tg": "Общий Python-фон — для кругозора.",
    "LLMScience": "AI-research фон — для кругозора.",
    "slivaker_it": "Курсы пачками — полезное вынесено в раздел «Курсы».",
}
COURSE_CHANNEL = "slivaker_it"   # каталог курсов: посты вида «Название / Размер: / Цена:»
COLORS = ["#4F7358", "#43618A", "#A97A45", "#3E6E6B", "#7A5C8A", "#8A5A4F", "#5C6E3E"]


def load_json(p, default):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return default


# ---------- сбор ----------

def collect(conn):
    """Как tg_monitor.process_channel, но догоняет пропуски: листает назад, пока не встретит
    известный пост или не уйдёт глубже CATCHUP_DAYS."""
    horizon = datetime.now(timezone.utc) - timedelta(days=CATCHUP_DAYS)
    now = datetime.now(timezone.utc).isoformat()
    total = 0
    for ch in tm.load_channels():
        known = {r[0] for r in conn.execute("SELECT post_id FROM posts WHERE channel=?", (ch,))}
        before, new, pages = None, [], 0
        while pages < MAX_PAGES:
            try:
                posts = tm.parse_posts(tm.fetch_page(ch, before))
            except requests.RequestException as e:
                print(f"  [{ch}] ошибка загрузки: {e}")
                break
            pages += 1
            if not posts:
                break
            fresh = [p for p in posts if p["post_id"] not in known]
            new += fresh
            oldest = min(posts, key=lambda p: p["post_id"])
            old_date = datetime.fromisoformat(oldest["post_date"]) if oldest["post_date"] else horizon
            if len(fresh) < len(posts) or old_date < horizon or not known:
                break  # дошли до известных / глубже месяца / канал новый — хватит одной страницы
            before = oldest["post_id"]
            time.sleep(tm.REQUEST_DELAY)
        for p in new:
            conn.execute("INSERT OR IGNORE INTO posts (channel, post_id, post_date, text, photos, videos, scraped_at) "
                         "VALUES (?,?,?,?,?,?,?)", (ch, p["post_id"], p["post_date"], p["text"],
                                                    "\n".join(p["photos"]), "\n".join(p["videos"]), now))
            tm.save_media(ch, p["post_id"], p["photos"], p["videos"])
        conn.commit()
        total += len(new)
        status = "нет постов (закрыт веб-просмотр)" if pages and not new and not known else f"новых: {len(new)}"
        print(f"  [{ch}] {status}")
        time.sleep(tm.REQUEST_DELAY)
    return total


# ---------- панель ----------

def fmt_text(t):
    t = html.escape(t or "")
    t = re.sub(r"(https?://[^\s<]+)", r'<a href="\1" target="_blank" rel="noopener">\1</a>', t)
    return t.replace("\n", "<br>")


def fmt_note(s):
    s = html.escape(s)
    return re.sub(r"`([^`]+)`", r'<code class="inline">\1</code>', s)


def local(dt_iso):
    return datetime.fromisoformat(dt_iso).astimezone() if dt_iso else None


MONTHS = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа",
          "сентября", "октября", "ноября", "декабря"]


def ru_date(d):
    return f"{d.day} {MONTHS[d.month - 1]}"


def build(conn, state, notes):
    since = (datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)).isoformat()
    rows = conn.execute("SELECT channel, post_id, post_date, text, scraped_at FROM posts "
                        "WHERE post_date >= ? ORDER BY post_date DESC", (since,)).fetchall()
    # «новое» = in the DB since the PREVIOUS «новости» run: the hourly TG_Monitor task can scrape posts in between
    last_collect = state.get("prev_collect_started") or state.get("last_collect_started", "")
    if last_collect:   # posts saved BY that previous run carry its start time (+ms) -> they are not new
        last_collect = (datetime.fromisoformat(last_collect) + timedelta(minutes=15)).isoformat()
    channels = tm.load_channels()
    color = {ch: COLORS[i % len(COLORS)] for i, ch in enumerate(channels)}
    readable = {r[0] for r in conn.execute("SELECT DISTINCT channel FROM posts")}
    closed = [ch for ch in channels if ch not in readable]

    def is_new(r):
        return bool(last_collect) and (r[4] or "") >= last_collect

    def head(ch, dt, new):
        return (f'<div class="article-head"><div class="avatar" style="background:{color.get(ch, "#777")}">{html.escape(ch[:1].upper())}</div>'
                f'<div><div class="chan">{html.escape(ch)}</div><div class="date">{ru_date(dt)}, {dt:%H:%M}</div></div>'
                + ('<span class="new">новое</span>' if new else "") + "</div>")

    # Главное: «по делу» и «лично тебе» — два столбца рядом, «фоново» — под ними
    n_notes = 0

    def column(cat):
        nonlocal n_notes
        items = [r for r in rows if notes.get(f"{r[0]}/{r[1]}", {}).get("cat") == cat]
        out = [f'<div class="pill-row"><span class="pill {cat}">{CATS[cat]}</span>'
               f'<span class="rule"></span><span class="cnt">{len(items)}</span></div>']
        for r in items:
            n = notes[f"{r[0]}/{r[1]}"]
            n_notes += 1
            body = "".join(f"<p>{fmt_note(s)}</p>" for s in n.get("summary", []))
            if n.get("for_us"):
                body += f'<p class="forus"><b>Для нас:</b> {fmt_note(n["for_us"])}</p>'
            if n.get("installed"):
                body += f'<p class="mark ok">✓ Установлено: {fmt_note(n["installed"])}</p>'
            elif n.get("declined"):
                body += f'<p class="mark no">Не ставили: {fmt_note(n["declined"])}</p>'
            out.append(
                f'<article class="article" data-ch="{html.escape(r[0])}">{head(r[0], local(r[2]), is_new(r))}'
                f'<h3 class="headline">{html.escape(n["headline"])}</h3>{body}'
                f'<a class="src" href="https://t.me/{r[0]}/{r[1]}" target="_blank" rel="noopener">Открыть пост в Telegram ↗</a></article>')
        return "\n".join(out) if items else ""

    biz, tool, soft = column("biz"), column("tool"), column("soft")
    main_html = [f'<div class="cols"><div class="col">{biz}</div><div class="col">{tool}</div></div>', soft]
    # posts the site hides ("Please open Telegram"): never silently skipped — shown until retold in notes
    hidden = [r for r in rows if r[3] == tm.HIDDEN and notes.get(f"{r[0]}/{r[1]}", {}).get("cat") in (None, "skip")]
    if hidden:
        main_html.insert(0, '<div class="hidden-posts"><b>Не прочитала — Telegram не показывает эти посты на сайте, откройте в приложении:</b> '
                         + " · ".join(f'<a href="https://t.me/{r[0]}/{r[1]}" target="_blank" rel="noopener">'
                                      f'{html.escape(r[0])}, {ru_date(local(r[2]))} {local(r[2]):%H:%M} ↗</a>' for r in hidden)
                         + "</div>")

    # Свежие курсы из канала-каталога: название, цена, размер; пометка «зачем», если есть в notes
    courses = []
    for r in rows:
        if r[0] != COURSE_CHANNEL or not r[3]:
            continue
        lines = [l.strip() for l in r[3].splitlines() if l.strip()]
        title = lines[0] if lines else ""
        field = lambda name: next((lines[i + 1] for i, l in enumerate(lines[:-1]) if l.rstrip(":") == name), "")
        price, size = field("Цена"), field("Размер")
        if not price:
            continue  # не курс (объявление, реклама)
        n = notes.get(f"{r[0]}/{r[1]}", {})
        pick = n.get("cat") == "course"
        courses.append(
            f'<a class="offer{" pick" if pick else ""}" href="https://t.me/{r[0]}/{r[1]}" target="_blank" rel="noopener">'
            f'<span class="otitle">{html.escape(title)}</span>'
            f'<span class="ometa">{html.escape(price)}{" · " + html.escape(size) if size else ""} · {ru_date(local(r[2]))}'
            + (' <span class="new">новое</span>' if is_new(r) else "") + "</span>"
            + (f'<span class="owhy">{fmt_note(n["for_us"])}</span>' if n.get("for_us") else "") + "</a>")

    quiet = "".join(f'<div class="quiet"><h4>{html.escape(ch)}</h4><p>{html.escape(t)}</p></div>'
                    for ch, t in QUIET.items() if ch in channels)
    if closed:
        quiet += (f'<div class="quiet"><h4>{" · ".join(map(html.escape, closed))}</h4>'
                  '<p>Не читаются — владелец отключил веб-просмотр канала.</p></div>')
    if not any(notes.get(f"{r[0]}/{r[1]}", {}).get("cat") == "soft" for r in rows):
        quiet = f'<div class="pill-row"><span class="pill soft">{CATS["soft"]}</span><span class="rule"></span></div>' + quiet

    # всё, что когда-либо поставили из новостей (не только за окно панели)
    inst = [(v.get("tool") or v.get("headline", ""), v["installed"]) for v in notes.values() if v.get("installed")]
    installed_html = ("" if not inst else
                      '<div class="installed"><b>Из новостей установлено:</b> '
                      + " · ".join(f'<span title="{html.escape(w)}">{html.escape(t)}</span>' for t, w in inst) + "</div>")

    upd = datetime.now().astimezone()
    new_count = sum(1 for r in rows if is_new(r))
    page = (TEMPLATE
            .replace("__UPDATED__", f"{ru_date(upd)} {upd.year}, {upd:%H:%M}")
            .replace("__STATS__", "".join(
                f'<div class="stat"><div class="n">{v}</div><div class="l">{l}</div></div>' for v, l in [
                    (new_count, "новых с прошлого обновления"), (len(rows), f"постов за {WINDOW_DAYS} дней"),
                    (n_notes, "разобрано в «Главном»"), (f"{len(readable)}/{len(channels)}", "каналов читается")]))
            .replace("__MAIN__", "\n".join(main_html) if n_notes else '<p class="section-note">Пока нет разобранных постов.</p>')
            .replace("__QUIET__", quiet)
            .replace("__INSTALLED__", installed_html)
            .replace("__OFFERS__", "\n".join(courses) or '<p class="section-note">Новых курсов за этот период нет.</p>')
            .replace("__OFFERS_N__", str(len(courses)))
            .replace("__WINDOW__", str(WINDOW_DAYS))
            .replace("__EXTRA__", EXTRA.read_text(encoding="utf-8") if EXTRA.exists() else ""))
    OUT.write_text(page, encoding="utf-8")
    print(f"Панель: {OUT} — постов {len(rows)}, новых {new_count}, в «Главном» {n_notes}")
    return rows, is_new


def main():
    only_build = "--build" in sys.argv
    conn = tm.init_db()
    state = load_json(STATE, {})
    if not only_build:
        started = datetime.now(timezone.utc).isoformat()
        print("Сбор постов...")
        n = collect(conn)
        state["prev_collect_started"] = state.get("last_collect_started", "")
        state["last_collect_started"] = started
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"Новых постов: {n}")
    notes = load_json(NOTES, {})
    rows, is_new = build(conn, state, notes)
    # needs review = any post in the window without a note, whoever scraped it (23.09 bug: TG_Monitor
    # had scraped 15 posts an hour earlier, they were not «new» for this run and got skipped)
    todo = [r for r in rows if f"{r[0]}/{r[1]}" not in notes]
    if todo:
        print(f"\n=== НУЖЕН РАЗБОР: {len(todo)} новых постов без пересказа ===")
        for r in todo:
            print(f"\n--- {r[0]}/{r[1]}  {local(r[2]):%d.%m %H:%M}\n{(r[3] or '')[:1500]}")


TEMPLATE = """<title>Рабочая панель</title>
<meta name="description" content="Дайджест Telegram-каналов по дропшиппингу, Shopify и инструментам, плюс свежие курсы и что из новостей установлено">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Work+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap">
<style>
  :root {
    --bg: #F6F5F1; --surface: #FFFFFF; --ink: #21241F; --ink-soft: #45473E; --muted: #74746A;
    --border: #E2DFD3; --border-soft: #ECEAE0;
    --biz: #4F7358; --biz-bg: #EDF3EB; --biz-border: #C7DAC1;
    --tool: #43618A; --tool-bg: #EAEFF6; --tool-border: #C4D2E6;
    --soft: #A97A45; --soft-bg: #F5EEE2; --soft-border: #E3D3B8;
    --new: #B0472F; --new-bg: #F7E4DF;
    --shadow: 0 2px 10px rgba(33,36,31,0.06);
    color-scheme: light dark;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #1B1D17; --surface: #24261F; --ink: #ECEAE0; --ink-soft: #C9C7B9; --muted: #9B9A8B;
      --border: #383A30; --border-soft: #2D2F27;
      --biz: #8FBF8A; --biz-bg: #253128; --biz-border: #3C5A3F;
      --tool: #8FB1DE; --tool-bg: #212B38; --tool-border: #384D6B;
      --soft: #D9AC72; --soft-bg: #332A1E; --soft-border: #55442C;
      --new: #E5876F; --new-bg: #3D231C;
      --shadow: 0 2px 10px rgba(0,0,0,0.35);
    }
  }
  :root[data-theme="dark"] {
    --bg: #1B1D17; --surface: #24261F; --ink: #ECEAE0; --ink-soft: #C9C7B9; --muted: #9B9A8B;
    --border: #383A30; --border-soft: #2D2F27;
    --biz: #8FBF8A; --biz-bg: #253128; --biz-border: #3C5A3F;
    --tool: #8FB1DE; --tool-bg: #212B38; --tool-border: #384D6B;
    --soft: #D9AC72; --soft-bg: #332A1E; --soft-border: #55442C;
    --new: #E5876F; --new-bg: #3D231C;
    --shadow: 0 2px 10px rgba(0,0,0,0.35);
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--ink); font-family: "Work Sans", system-ui, sans-serif;
         font-size: 15px; line-height: 1.55; }
  h1, h2, h3 { font-family: "Fraunces", Georgia, serif; text-wrap: balance; margin: 0; }
  a { color: var(--tool); }
  .wrap { max-width: 1240px; margin: 0 auto; padding-inline: 20px; padding-block: 0 90px; }
  .hero, #courses, #offers { max-width: 880px; }
  .offers { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 260px), 1fr)); gap: 10px; }
  .offer { display: flex; flex-direction: column; gap: 4px; text-decoration: none; color: var(--ink);
           background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; }
  .offer:hover, .offer:focus-visible { border-color: var(--tool); }
  .offer.pick { border-color: var(--biz-border); background: var(--biz-bg); }
  .otitle { font-weight: 600; font-size: 13.5px; }
  .ometa { font: 500 11.5px "JetBrains Mono", monospace; color: var(--muted); display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
  .ometa .new { margin-left: 0; }
  .owhy { font-size: 12.5px; color: var(--ink-soft); }
  .cols { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 420px), 1fr)); gap: 0 24px; align-items: start; }
  .col { min-width: 0; }
  .col .pill-row { margin-top: 0; position: sticky; top: calc(env(safe-area-inset-top, 0px) + 50px); z-index: 5;
                   background: var(--bg); padding-block: 8px; }
  .cnt { font: 600 11px "JetBrains Mono", monospace; color: var(--muted); }
  nav.top { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 20; background: var(--bg); border-bottom: 1px solid var(--border); }
  .top-inner { max-width: 1240px; margin: 0 auto; padding: 12px 20px; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
  .brand { font-family: "Fraunces", serif; font-weight: 700; font-size: 16px; margin-right: auto; }
  .navlink { font-size: 12.5px; font-weight: 600; text-decoration: none; color: var(--muted); padding: 6px 12px;
             border-radius: 999px; border: 1px solid transparent; }
  .navlink:hover, .navlink:focus-visible { border-color: var(--border); color: var(--ink); }
  .hero { padding-block: 32px 4px; }
  .eyebrow { font-family: "JetBrains Mono", monospace; font-size: 11px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }
  .eyebrow b { color: var(--new); font-weight: 600; }
  .hero h1 { font-size: 32px; margin-top: 6px; }
  .hero p { color: var(--ink-soft); max-width: 62ch; margin: 10px 0 0; }
  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 20px; }
  .stat { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 10px 14px; }
  .stat .n { font: 700 22px "Fraunces", serif; font-variant-numeric: tabular-nums; }
  .stat .l { font-size: 12px; color: var(--muted); }
  section { padding-block: 44px 8px; border-top: 1px solid var(--border-soft); margin-top: 36px; scroll-margin-top: 64px; }
  .section-head { display: flex; align-items: baseline; gap: 12px; margin-bottom: 18px; flex-wrap: wrap; }
  .section-head h2 { font-size: 22px; }
  .section-head .count { font-family: "JetBrains Mono", monospace; font-size: 11.5px; color: var(--muted); }
  .section-note { color: var(--muted); font-size: 13px; margin: -8px 0 22px; max-width: 62ch; }
  .pill-row { display: flex; align-items: center; gap: 10px; margin: 28px 0 14px; }
  .pill { font-size: 11.5px; font-weight: 700; padding: 5px 12px; border-radius: 999px; font-family: "JetBrains Mono", monospace; }
  .pill.biz { background: var(--biz-bg); color: var(--biz); border: 1px solid var(--biz-border); }
  .pill.tool { background: var(--tool-bg); color: var(--tool); border: 1px solid var(--tool-border); }
  .pill.soft { background: var(--soft-bg); color: var(--soft); border: 1px solid var(--soft-border); }
  .pill-row .rule { flex-grow: 1; height: 1px; background: var(--border); }
  .article { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 18px 20px;
             margin-bottom: 12px; box-shadow: var(--shadow); }
  .article-head { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
  .avatar { width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
            font-family: "Fraunces", serif; font-weight: 700; font-size: 14px; color: #fff; flex-shrink: 0; }
  .chan { font-size: 12.5px; font-weight: 700; }
  .date { font-size: 11px; color: var(--muted); font-family: "JetBrains Mono", monospace; }
  .new { font: 600 10.5px "JetBrains Mono", monospace; color: var(--new); background: var(--new-bg); border-radius: 999px;
         padding: 2px 8px; margin-left: auto; white-space: nowrap; }
  .headline { font-family: "Work Sans", sans-serif; font-size: 15.5px; font-weight: 700; margin: 0 0 8px; }
  .article p { margin: 0 0 8px; font-size: 13.5px; color: var(--ink-soft); }
  .article b { color: var(--ink); }
  .forus { border-left: 3px solid var(--biz-border); padding-left: 10px; }
  .article p.mark { font-size: 12.5px; font-weight: 600; border-radius: 8px; padding: 6px 10px; }
  .mark.ok { background: var(--biz-bg); color: var(--biz); }
  .mark.no { background: var(--border-soft); color: var(--muted); font-weight: 500; }
  .installed { margin-top: 12px; font-size: 13px; color: var(--ink-soft); background: var(--biz-bg);
               border: 1px solid var(--biz-border); border-radius: 12px; padding: 10px 14px; }
  .installed b { color: var(--biz); }
  .hidden-posts { margin-bottom: 16px; font-size: 14px; color: var(--ink-soft); background: var(--soft-bg);
                  border: 1px solid var(--soft-border); border-radius: 12px; padding: 10px 14px; line-height: 1.7; }
  .hidden-posts b { color: var(--ink); }
  .hidden-posts a { color: var(--tool); font-weight: 600; white-space: nowrap; }
  .installed span { font-weight: 600; color: var(--ink); }
  .src { font-size: 12px; text-decoration: none; }
  code.inline { font-family: "JetBrains Mono", monospace; font-size: 12px; background: var(--border-soft); padding: 1px 6px;
                border-radius: 5px; overflow-wrap: anywhere; }
  .quiet { background: var(--border-soft); border-radius: 12px; padding: 12px 16px; margin-bottom: 8px; }
  .quiet h4 { margin: 0 0 3px; font-size: 12.5px; color: var(--ink-soft); }
  .quiet p { margin: 0; font-size: 12px; color: var(--muted); }
  .chips { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
  .chip { font: 600 12px "Work Sans", sans-serif; color: var(--ink-soft); background: var(--surface); border: 1px solid var(--border);
          border-radius: 999px; padding: 5px 12px; min-height: 32px; cursor: pointer; }
  .chip[aria-pressed="true"] { background: var(--ink); color: var(--bg); border-color: var(--ink); }
  .chip:focus-visible, summary:focus-visible { outline: 2px solid var(--tool); outline-offset: 2px; }
  .day { font-size: 16px; margin: 22px 0 8px; color: var(--ink-soft); }
  .post { background: var(--surface); border: 1px solid var(--border-soft); border-radius: 10px; margin-bottom: 6px; }
  .post summary { list-style: none; cursor: pointer; padding: 9px 12px; display: flex; align-items: baseline; gap: 10px; min-width: 0; }
  .post summary::-webkit-details-marker { display: none; }
  .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; align-self: center; }
  .ptime { font: 500 11.5px "JetBrains Mono", monospace; color: var(--muted); font-variant-numeric: tabular-nums; }
  .pch { font-size: 12px; font-weight: 700; color: var(--ink-soft); white-space: nowrap; }
  .ptitle { font-size: 13.5px; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
  .post[open] .ptitle { white-space: normal; }
  .ptext { padding: 0 14px 12px 30px; font-size: 13.5px; color: var(--ink-soft); overflow-wrap: anywhere; }
  .course { display: flex; gap: 14px; align-items: flex-start; background: var(--surface); border: 1px solid var(--biz-border);
            border-radius: 14px; padding: 16px 18px; margin-bottom: 12px; box-shadow: var(--shadow); }
  .course.note { border-color: var(--soft-border); }
  .num { flex-shrink: 0; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
         font: 700 13px "JetBrains Mono", monospace; color: #fff; background: var(--biz); }
  .course.note .num { background: var(--soft); }
  .course h3 { font-size: 14.5px; font-family: "Work Sans", sans-serif; font-weight: 700; margin-bottom: 3px; }
  .course .price { font: 700 12px "JetBrains Mono", monospace; color: var(--biz); }
  .course.note .price { color: var(--soft); }
  .course .why { font-size: 12.5px; color: var(--ink-soft); margin-top: 5px; }
  .total-line { text-align: right; font-weight: 700; color: var(--biz); font-size: 13px; margin: 6px 0 26px; }
  .skip-list { font-size: 12px; color: var(--muted); line-height: 1.8; padding: 14px 18px; background: var(--border-soft); border-radius: 12px; }
  footer.page { max-width: 1240px; margin: 40px auto 0; padding: 20px; font-size: 11.5px; color: var(--muted); border-top: 1px solid var(--border-soft); }
  @media (max-width: 520px) { .pch { display: none; } .hero h1 { font-size: 26px; } }
</style>

<nav class="top"><div class="top-inner">
  <div class="brand">Панель</div>
  <a class="navlink" href="#digest">Главное</a>
  <a class="navlink" href="#courses">Курсы</a>
  <a class="navlink" href="https://claude.ai/artifact/3TFmbuqrhc4s1j9eauX2my">Экосистема ↗</a>
</div></nav>

<div class="wrap">
  <div class="hero">
    <div class="eyebrow">Telegram-каналы · обновлено <b>__UPDATED__</b></div>
    <h1>Дайджест и рекомендации</h1>
    <p>Что важного было в отслеживаемых каналах за __WINDOW__ дней, и какие курсы стоит взять. Старые новости не удаляются.</p>
    <div class="stats">__STATS__</div>
    __INSTALLED__
  </div>

  <section id="digest">
    <div class="section-head"><h2>Главное</h2></div>
    __MAIN__
    __QUIET__
  </section>

__EXTRA__
  <section id="offers">
    <div class="section-head"><h2>Свежие курсы в slivaker_it</h2><span class="count">__OFFERS_N__ за __WINDOW__ дней</span></div>
    <p class="section-note">Всё, что выложили в канале, новые сверху. Зелёным — то, что пересекается с нашими задачами, с пояснением зачем.</p>
    <div class="offers">__OFFERS__</div>
  </section>
</div>
<footer class="page">Собирается командой «новости»: tg_monitor.db → news.py. База хранит все посты, панель показывает разобранное за последние __WINDOW__ дней.</footer>

"""

if __name__ == "__main__":
    main()
