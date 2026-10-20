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
import os
import re
import sqlite3
import subprocess
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
BOOKS = BASE / "panel_books.html"   # user 09.10: книги — выжимка и что ушло в скиллы, отдельный блок панели
BOOKS_FULL = BASE / "panel_books_full.html"   # 09.10 «маловато»: все приёмы и конспекты целиком, строит build_books.py
OUT = BASE / "news_panel.html"
NUMS = BASE / "post_numbers.json"   # 07.10: every post has its own permanent simple number on the panel
WINDOW_DAYS = 45        # на панели; в базе хранится всё
CATCHUP_DAYS = 45       # догонять всё окно панели (29.09: «исчерпывающий сбор»)
MAX_PAGES = 30          # страниц t.me/s/ на канал за один сбор (по ~20 постов)

CATS = {"biz": "по делу — shopify / дропшиппинг / маркетплейсы",
        "tool": "лично тебе — claude code / инструменты",
        "soft": "фоново"}
TREND_CATS = {"biz": "мода — что носят и продают", "tool": "тренды контента и инструменты", "soft": "фоново"}
QUIET = {  # каналы, которые не разбираем подробно
    "irina_agafonova_ved": "Импорт из Китая и комплаенс Wildberries — доступа к WB сейчас нет, оставлено под общие новости e-commerce.",
    "LLMScience": "AI-research фон — для кругозора.",
    "slivaker_it": "Курсы пачками — полезное вынесено в раздел «Курсы».",
    "uxlive": "UX и тренды, много шума — поглядывать для сайта (05.10).",
    "tproger_web": "Фронтенд/бэкенд — справочно для сборки сайта (05.10).",
    "marketingmass": "Маркетинг (tgstat 09.10), фон: строго только полезное — B2B-маркетинг от экс-CMO Битрикса: «портрет целевого клиента и как проверить», «хорошая уп…",
    "HelloDigitalWorld": "Маркетинг (tgstat 09.10), фон: строго только полезное — Практик SEO: межсезонье в SEO (07.10), обзор AI Tracker Топвизора для видимости в ИИ-ответ…",
    "Meo_marketing": "Маркетинг (tgstat 09.10), фон: строго только полезное — CMO B2B IT-компании: как заставить холодные продажи работать в сложном B2B, кастдев через …",
    "TexterraBlog": "Маркетинг (tgstat 09.10), фон: строго только полезное — Полезные статьи про GEO (видимость компании в ответах нейросетей, кейс ошибок ИИ о бренде)…",
    "coreboot_marketing": "Маркетинг (tgstat 09.10), фон: строго только полезное — Перфоманс-агентство: советы по рекламе в Авито (в т.ч. B2B и премиум), реклама в Max через…",
    "molyanov_blog": "Маркетинг (tgstat 09.10), фон: строго только полезное — Иногда практичные ИИ-приёмы: субагенты обновляют устаревшие статьи сайта, 2–3 варианта хук…",
    "websstudio": "Маркетинг (tgstat 09.10), фон: строго только полезное — Бывают практичные посты: реклама в MAX и таргет Директа в MAX (01.10, 08.10), маржа на каж…",
    "copywritersdigest": "Маркетинг (tgstat 09.10), фон: строго только полезное — Для текстов иногда полезно: подборка сервисов редактуры (Diffchecker и др., 11.09), итоги …",
    "sukhachevk": "Маркетинг (tgstat 09.10), фон: строго только полезное — Деловые эссе собственника: как сверять CTR/конверсию с нормой рынка, low ticket, ролики о …",
    "eduard_trubcheninov": "Маркетинг (tgstat 09.10), фон: строго только полезное — SEO под Яндекс от практика: зачем Яндекс Вебмастер, как Яндекс маскирует рекламу в SEO-выд…",
    "maps_biz": "Маркетинг (tgstat 09.10), фон: строго только полезное — Тема ровно наша — геомаркетинг (Яндекс Карты/2ГИС, GEO-выдача), но последние недели почти …",
    "c/3493639787": "CodeGuard: Academy (папка Tech, подписалась сама 09.10) — ИБ для начинающих; брать только то, что защищает наши ПК и аккаунты (в pc-check).",
    "projplus": "ИИ (tgstat/папка Tech 09.10), фон: строго только полезное — Есть полезные находки для Claude Code — команда /insights (04.10), Mods (05.10), бесплатны…",
    "ppprompt": "ИИ (tgstat/папка Tech 09.10), фон: строго только полезное — Автор строит «personal AI OS» и скиллы (/slides-generator, 22.09), дельно про Haiku 5.5 по…",
    "kdoronin_blog": "ИИ (tgstat/папка Tech 09.10), фон: строго только полезное — Практик, но пишет ~3 раза в неделю и много анонсов эфиров; ценное — статистика банов Claud…",
    "ai_vibe": "ИИ (tgstat/папка Tech 09.10), фон: строго только полезное — Практик ИИ-видео: гайд «ролик с любыми персонажами и окружением» (05.10), как подстраховат…",
    "RixAiHub": "ИИ (tgstat/папка Tech 09.10), фон: строго только полезное — Практик на Claude: готовый плагин для Claude, который монтирует длинные видео (08.10), раз…",
    "TochkiNadAI": "ИИ (tgstat/папка Tech 09.10), фон: строго только полезное — Иногда полезное: библиотека 475 промптов видео/эксплейнеров для повтора под свой бренд, га…",
    "free_republic_ai": "ИИ (tgstat/папка Tech 09.10), фон: строго только полезное — Справочники для ИИ-видео: 45 движений камеры, шпаргалка по объективам, эмоции лица (FACS) …",
    "NeuroLuv": "ИИ (tgstat/папка Tech 09.10), фон: строго только полезное — Практичные туториалы для визуала: промпт «фото товара → обложка журнала» с сохранением тов…",
    "ai4svoi": "ИИ (tgstat/папка Tech 09.10), фон: строго только полезное — Попадаются рабочие советы по Claude Code — /claude-api prompt-audit (26.09), мод прогрева …",
    "its_capitan": "ИИ (tgstat/папка Tech 09.10, прислала сама), фон: строго только полезное — Честно: это дневник инди-разработчика микро-SaaS (bota.chat, ai-flip, legalai) — показывае…",
    "digital_ponos": "ИИ (tgstat/папка Tech 09.10), фон: строго только полезное — CTO делится найденными фичами агентов: Dreams — оптимизация памяти Claude Code (04.08), ка…",
    "aiwizards": "ИИ (tgstat/папка Tech 09.10), фон: строго только полезное — По делу бывают рецепты: свой Telegram CLI с демоном (07.09), список стека агентных инструм…",
    "dev_salikhov": "ИИ (tgstat/папка Tech 09.10), фон: строго только полезное — CTO RetailCRM с реальным опытом агентной разработки: Claude Code с 2.1.277 читает AGENTS.m…",
    "deksden_notes": "Вайбкодинг (12.10), фон: строго только полезное — DEKSDEN notes: новости Codex/Claude Code с практическими советами (TTL кэша субагентов, Agent SDK по подписке)",
    "nobilix": "Вайбкодинг (12.10), фон: строго только полезное — Refat Talks: приёмы работы с кодовыми агентами (диплинки, регламенты как инструкции агенту) + субботний дайджест",
    "sergiobulaev": "Вайбкодинг (12.10), фон: строго только полезное — Сергей Булаев: разборы про агентов и Claude Code (облачные сессии), много пересказа новостей",
    "neuraldeep": "Вайбкодинг (12.10), фон: строго только полезное — Валера Ковальский: опыт с Claude Code и агентами, статистика банов Claude, инструменты терминала",
    "ultravibecoder": "Вайбкодинг (12.10), фон: строго только полезное — Ультра ВайбКодер: практика сайтов с 3D и анимациями через ИИ, сценарии Codex; часть постов личные",
    "vibecodings": "Вайбкодинг (12.10), фон: строго только полезное — Станислав Быстрицкий: гайды по Claude Design и промпты для макетов, но много продажи обучения",
    "max_about_ai": "Вайбкодинг (12.10), фон: строго только полезное — Max: вдумчивые посты про скиллы, RAG, универсальных агентов; пишет редко",
    "typetoday": "Дизайн сайтов (12.10), фон: строго только полезное — type.today: шрифты и типографика, новые гарнитуры и примеры айдентики — для выбора шрифтов",
    "figmaweb": "Дизайн сайтов (12.10), фон: строго только полезное — Веб-дизайн в Figma: бесплатные макеты лендингов и магазинов по темам + статьи; есть реклама",
    "figma_pro": "Дизайн сайтов (12.10), фон: строго только полезное — Figma Pro: плагины, наборы иконок и UI-китов (в т.ч. Типограф Бычкова)",
    "onlyfigma": "Дизайн сайтов (12.10), фон: строго только полезное — Только Figma: шрифтовые пары, градиенты, мини-уроки эффектов; бывают мемы",
    "pdigest": "Дизайн сайтов (12.10), фон: строго только полезное — Дайджест продуктового дизайна: ежемесячные подборки паттернов и дизайн-систем для ИИ; бывает реклама курсов",
    "designdealer": "Дизайн сайтов (12.10), фон: строго только полезное — Designdealer: новые ИИ-инструменты для дизайна и анимации (SVG-генераторы, скиллы для 3D-иконок)",
    "prouxui": "Дизайн сайтов (12.10), фон: строго только полезное — Про UX, UI и AI: Figma + MCP (вытащить шейдеры, анимации как стили), мысли про интерфейсы",
    "frontendnoteschannel_ru": "Дизайн сайтов (12.10), фон: строго только полезное — Frontender's notes: новости фронтенда и ИИ-разработки (Next.js, Chrome, Claude) короткими пересказами",
    "nikitonsky_pub": "Дизайн сайтов (12.10), фон: строго только полезное — Никита Прокопов (Tonsky): мнения про UX интерфейсов и форм, иногда про ИИ",
}
# channels with their own block on the panel (user 29.09: «python_tg — для новостей и полезностей», not lost in «фоново»)
# 05.10: she starts building the site — the four web-design channels share one block «Дизайн сайтов», shown first
DESIGN_BLOCK = ("design", "Дизайн сайтов — новости и полезное")
OWN_BLOCKS = {"intelligentdesign": DESIGN_BLOCK, "sitodel": DESIGN_BLOCK, "uxlive": DESIGN_BLOCK, "tproger_web": DESIGN_BLOCK,
              "python_tg": ("python", "Python — новости и полезное")}
# 09.10: marketing channels from tgstat.ru/tag/marketing (104 read, 18 kept) share one block «Маркетинг»
# 09.10: private channels without @username (she subscribed; read only through Telegram Web): c/<id> -> name on the panel
PRIVATE_TITLES = {"c/3128735547": "CodeGuard: Python", "c/3493639787": "CodeGuard: Academy"}
OWN_BLOCKS["c/3128735547"] = OWN_BLOCKS["python_tg"]
OWN_BLOCKS.update({c: DESIGN_BLOCK for c in ['webstandards_ru', 'mozhno', 'fourdesign', 'htmlacademy', 'typetoday', 'figmaweb', 'figma_pro', 'onlyfigma', 'pdigest', 'designdealer', 'prouxui', 'frontendnoteschannel_ru', 'nikitonsky_pub']})  # 12.10 new web-design channels
MARKETING_BLOCK = ("marketing", "Маркетинг — реклама, лиды, тексты")
OWN_BLOCKS.update({c: MARKETING_BLOCK for c in ['serezha_pro_marketing', 'boringmarketer', 'vanzhula', 'b2b_marketing_ru', 'target_nata', 'irina_trafik', 'glvrdru', 'marketingmass', 'HelloDigitalWorld', 'Meo_marketing', 'TexterraBlog', 'coreboot_marketing', 'molyanov_blog', 'websstudio', 'copywritersdigest', 'sukhachevk', 'eduard_trubcheninov', 'maps_biz']})
COURSE_CHANNEL = "slivaker_it"   # каталог курсов: посты вида «Название / Размер: / Цена:»
# fashion & trend channels: their cards go to a separate «Мода и тренды» block BELOW dropshipping/AI news
# (user 23.09.2026: «не смешивай с новостями дропшип и ИИ»)
TREND_CHANNELS = {"now_trends", "moda_po_sprosu", "odezhda_stil_moda", "shop_sekret", "shoppingfyou", "topoeva_olesya",
                  "runtobuy", "svetlana_nechego_nadet", "moda_vtelege", "my_image_and_style", "valeri_bloc", "pro_reelss",
                  "promty_by_irri", "photopingvin_ai", "BrandAnalytics", "thetrends_journal"}
COLORS = ["#4F7358", "#43618A", "#A97A45", "#3E6E6B", "#7A5C8A", "#8A5A4F", "#5C6E3E"]
FASHION_OUT = BASE / "fashion_panel.html"   # old separate page, kept only as a local copy
FASHION_DATA = BASE / "fashion_data.json"   # -> «Мода — ориентиры» section of the radar dashboard
FASHION_URL = "https://claude.ai/artifact/7XN5rKYANe4QX8HwRHKNZF#fashion"   # merged into the radar 23.09
RADAR_URL = "https://claude.ai/artifact/7XN5rKYANe4QX8HwRHKNZF"


def build_fashion(rows, notes, t_biz, t_tool, t_soft):
    """fashion_panel.html: what repeats across fashion posts, phrases to check in the trend radar, then the cards."""
    from collections import defaultdict
    themes, phrases = defaultdict(list), defaultdict(list)
    for r in rows:
        n = notes[f"{r[0]}/{r[1]}"]
        src = (n.get("headline", "")[:60], f"https://t.me/{r[0]}/{r[1]}")
        for t in n.get("themes", []):
            themes[t].append(src)
        for p in n.get("radar", []):
            phrases[p].append(src)
    rep = sorted(((t, s) for t, s in themes.items() if len(s) >= 2), key=lambda x: -len(x[1]))
    rep_html = "".join(
        f'<div class="theme"><b>{html.escape(t)}</b> <span class="cnt">{len(s)} постов</span><br>'
        + " · ".join(f'<a href="{u}" target="_blank" rel="noopener">{html.escape(h)}</a>' for h, u in s[:5]) + "</div>"
        for t, s in rep) or '<p class="section-note">Пока ничего не повторяется.</p>'
    ph_html = "".join(
        f'<tr><td><code class="inline">{html.escape(p)}</code></td><td>'
        + " · ".join(f'<a href="{u}" target="_blank" rel="noopener">{html.escape(h)}</a>' for h, u in s) + "</td></tr>"
        for p, s in sorted(phrases.items(), key=lambda x: (-len(x[1]), x[0])))
    # data for the «Мода — ориентиры» section of the trend radar dashboard (user 23.09.2026: merge the two pages)
    cards = []
    for r in rows:
        n = notes[f"{r[0]}/{r[1]}"]
        cards.append({"channel": r[0], "date": local(r[2]).strftime("%d.%m"), "cat": n.get("cat"),
                      "headline": n.get("headline", ""), "summary": n.get("summary", []), "for_us": n.get("for_us", ""),
                      "radar": n.get("radar", []), "link": f"https://t.me/{r[0]}/{r[1]}"})
    FASHION_DATA.write_text(json.dumps({
        "updated": datetime.now().astimezone().strftime("%d.%m.%Y %H:%M"),
        "themes": [{"theme": t, "posts": [{"title": h, "link": u} for h, u in s]} for t, s in rep],
        "phrases": [{"phrase": p, "posts": [{"title": h, "link": u} for h, u in s]}
                    for p, s in sorted(phrases.items(), key=lambda x: (-len(x[1]), x[0]))],
        "cards": cards}, ensure_ascii=False, indent=1), encoding="utf-8")
    style = re.search(r"<style>.*?</style>", TEMPLATE, re.S).group(0)
    fonts = re.search(r'<link rel="stylesheet"[^>]+>', TEMPLATE).group(0)
    upd = datetime.now().astimezone()
    page = f"""<title>Мода — ориентиры</title>
<meta name="description" content="Новости модных Telegram-каналов как ориентир для радара трендов: что повторяется и что проверить">
{fonts}
{style}
<style>
  .theme {{ background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 10px 14px; margin-bottom: 8px; font-size: 13.5px; }}
  .theme b {{ font-size: 15px; }}
  table.ph {{ width: 100%; border-collapse: collapse; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; font-size: 13.5px; }}
  table.ph td {{ padding: 8px 12px; border-top: 1px solid var(--border-soft); vertical-align: top; }}
  .themes {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 360px), 1fr)); gap: 0 12px; }}
</style>
<div class="wrap">
  <div class="hero">
    <div class="eyebrow">Мода и тренды · обновлено {ru_date(upd)} {upd.year}, {upd:%H:%M}</div>
    <h1>Мода — ориентиры для радара</h1>
    <p>Новости модных каналов нужны не сами по себе, а как подсказка: какие вещи, цвета и детали проверить в
    <a href="{RADAR_URL}" target="_blank" rel="noopener">радаре трендов</a>. Российские каналы опережают или повторяют западные
    тренды — поэтому всё, что здесь, мы проверяем на спросе в США.</p>
  </div>
  <section><div class="section-head"><h2>Что повторяется</h2><span class="count">тема встречается в 2+ постах</span></div>
    <div class="themes">{rep_html}</div></section>
  <section><div class="section-head"><h2>Проверить в радаре</h2><span class="count">{len(phrases)} фраз (как ищут в США)</span></div>
    <p class="section-note">Сначала — фразы, которые встретились в нескольких постах. Добавить в кандидаты радара решаете вы.</p>
    <div style="overflow-x:auto"><table class="ph">{ph_html}</table></div></section>
  <section><div class="section-head"><h2>Новости</h2><span class="count">{len(rows)}</span></div>
    <div class="cols"><div class="col">{t_biz}</div><div class="col">{t_tool or t_soft}</div></div>{t_soft if t_tool else ""}</section>
</div>"""
    FASHION_OUT.write_text(NUM_RE.sub("", page), encoding="utf-8")


def num_tag(key, date_iso):
    """Placeholder for the post's number; number_posts() swaps it for the permanent number."""
    return f'<span class="postnum">⟦{key}|{date_iso}⟧</span>'


NUM_RE = re.compile(r'<span class="postnum">⟦([^|⟧]+)\|([^⟧]*)⟧</span>')


def number_posts(page):
    """07.10 «каждый пост своей уникальной простой цифрой»: a number once given never changes;
    new posts get the next free numbers, older posts first."""
    nums = load_json(NUMS, {})
    new = {}
    for k, d in NUM_RE.findall(page):
        if k not in nums:
            new.setdefault(k, d)
    nxt = max(nums.values(), default=0)
    for k in sorted(new, key=lambda k: (new[k], k)):
        nxt += 1
        nums[k] = nxt
    if new:
        NUMS.write_text(json.dumps(nums, ensure_ascii=False, indent=0), encoding="utf-8")
    return NUM_RE.sub(lambda m: f'<span class="postnum" title="пост № {nums[m.group(1)]}">{nums[m.group(1)]}</span>', page)


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
    full = "--full" in sys.argv  # 29.09 «исчерпывающий сбор»: walk the whole window, filling every gap
    only = set(filter(None, os.environ.get("TG_ONLY", "").split(",")))  # 12.10: collect just the newly added channels
    chans = [c for c in tm.load_channels() if not only or c in only]
    for idx, ch in enumerate(chans, 1):  # 12.10: «N из M» по каналам
        known = {r[0] for r in conn.execute("SELECT post_id FROM posts WHERE channel=?", (ch,))}
        # history does not reach the window start yet -> keep paging back past known posts down to the horizon
        first = conn.execute("SELECT min(post_date) FROM posts WHERE channel=?", (ch,)).fetchone()[0]
        backfill = full or not first or datetime.fromisoformat(first) > horizon + timedelta(days=1)
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
            if old_date < horizon or (len(fresh) < len(posts) and not backfill):
                break  # глубже окна / дошли до известных (если история уже полная)
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
        print(f"  {idx} из {len(chans)} [{ch}] {status}")
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


# group chats read through Telegram Web: chat -> (topic on the panel, pill colour). Same logic for every chat:
# only important questions with their chosen answers (notes cat "chat"). vibecoding_community added 24.09.2026.
# groups of «Не забыть» (notes "when"), in the order of launching a store
WHEN_ORDER = ["Всегда: кому можно отдавать данные", "Всегда: лимит Claude и чужие скиллы", "Экономика товара и теста", "Реклама и креативы", "Платежи, корзина, каналы", "После запуска рекламы",
              "Страны и доставка", "Когда будет время (инструменты)"]
CHATS = {"shopify_chat": ("дропшиппинг", "biz"), "vibecoding_community": ("вайбкодинг", "tool")}


# user 29.09: «я прочла» — the panel shows only what she has not seen yet (any date).
# user 07.10: already taken into account («noted») never goes to the panel — it lives in the skill noted-news
# (noted_to_skill.py); the panel is only for new, not yet taken news
SEEN_FILE = BASE / "seen.json"
SEEN = set(json.loads(SEEN_FILE.read_text(encoding="utf-8"))["keys"]) if SEEN_FILE.exists() else set()


def shown(key, note):
    return not note.get("noted") and key not in SEEN


def chat_block(conn, notes, CHAT="shopify_chat"):
    """Question from the chat -> retelling -> the chosen answers (notes: cat "chat", "replies": [ids], "extra_roots")."""
    topic, pill = CHATS[CHAT]
    try:
        msgs = {r[0]: r for r in conn.execute("SELECT msg_id, date, text, reply_to FROM chat_msgs WHERE chat=?", (CHAT,))}
    except sqlite3.OperationalError:
        return ""
    items = sorted(((int(k.split("/")[1]), v) for k, v in notes.items() if k.startswith(CHAT + "/") and v.get("cat") == "chat"
                    and shown(k, v)),
                   key=lambda x: msgs.get(x[0], (0, ""))[1], reverse=True)
    if not items:
        return ""
    clip = lambda t, n: html.escape(t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…")
    link = lambda mid: f"https://t.me/{CHAT}/{mid}"

    def msg_html(mid, cls):
        m = msgs.get(mid)
        if not m:
            return ""
        d = local(m[1])
        return (f'<div class="{cls}"><span class="date">{ru_date(d)}, {d:%H:%M}</span> '
                f'{clip(m[2] or "", 420)} <a href="{link(mid)}" target="_blank" rel="noopener">↗</a></div>')

    cards = []
    for root, n in items:
        body = "".join(f"<p>{fmt_note(s)}</p>" for s in n.get("summary", []))
        if n.get("for_us"):
            body += f'<p class="forus"><b>Для нас:</b> {fmt_note(n["for_us"])}</p>'
        if n.get("noted"):
            body += f'<p class="mark note">📌 Принято к сведению: {fmt_note(n["noted"])}</p>'
        thread = msg_html(root, "chat-q") + "".join(msg_html(r, "chat-a") for r in n.get("replies", []))
        for extra in n.get("extra_roots", []):   # other threads on the same topic: question + all its answers
            thread += msg_html(extra, "chat-q") + "".join(
                msg_html(k, "chat-a") for k, m in sorted(msgs.items()) if m[3] == extra)
        cards.append(f'<article class="article">{num_tag(f"{CHAT}/{root}", msgs.get(root, (0, ""))[1] or "")}<h3 class="headline">{html.escape(n["headline"])}</h3>{body}'
                     f'<div class="chat-thread"><b>Из чата — вопрос и ответы:</b>{thread}</div></article>')
    return (f'<div class="pill-row"><span class="pill {pill}">чат {CHAT} ({topic}) — важное с ответами</span><span class="rule"></span>'
            f'<span class="cnt">{len(cards)}</span></div><div class="chat-cards">{"".join(cards)}</div>')


def build(conn, state, notes):
    # user 07.10: everything taken into account always goes to the skill noted-news — rebuilt on every panel build
    subprocess.run([sys.executable, str(BASE / "noted_to_skill.py")], check=False)
    since =(datetime.now(timezone.utc) - timedelta(days=WINDOW_DAYS)).isoformat()
    rows = conn.execute("SELECT channel, post_id, post_date, text, scraped_at FROM posts "
                        "WHERE post_date >= ? ORDER BY post_date DESC", (since,)).fetchall()
    # unseen posts count whatever their date (29.09: «не важно от какой даты, если я их не видела»)
    rows += [r for r in conn.execute("SELECT channel, post_id, post_date, text, scraped_at FROM posts WHERE post_date < ? "
                                     "ORDER BY post_date DESC", (since,)) if SEEN and f"{r[0]}/{r[1]}" not in SEEN]
    panel_rows = [r for r in rows if shown(f"{r[0]}/{r[1]}", notes.get(f"{r[0]}/{r[1]}", {}))]
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
        return (f'<div class="article-head"><div class="avatar" style="background:{color.get(ch, "#777")}">{html.escape(PRIVATE_TITLES.get(ch, ch)[:1].upper())}</div>'
                f'<div><div class="chan">{html.escape(PRIVATE_TITLES.get(ch, ch))}</div><div class="date">{ru_date(dt)}, {dt:%H:%M}</div></div>'
                + ('<span class="new">новое</span>' if new else "") + "</div>")

    # Главное: «по делу» и «лично тебе» — два столбца рядом, «фоново» — под ними
    n_notes = 0

    def column(cat, trends=False, only=None):
        nonlocal n_notes
        cats = (cat,) if isinstance(cat, str) else cat
        items = [r for r in panel_rows if notes.get(f"{r[0]}/{r[1]}", {}).get("cat") in cats
                 and (r[0] in TREND_CHANNELS) == trends and (OWN_BLOCKS.get(r[0]) == only if only else r[0] not in OWN_BLOCKS)]
        if only:
            out = [f'<div class="pill-row" id="{only[0]}"><span class="pill tool">{only[1]}</span>'
                   f'<span class="rule"></span><span class="cnt">{len(items)}</span></div><div class="chat-cards">']
        else:
            out = [f'<div class="pill-row"><span class="pill {cat}">{(TREND_CATS if trends else CATS)[cat]}</span>'
                   f'<span class="rule"></span><span class="cnt">{len(items)}</span></div>']
        for r in items:
            n = notes[f"{r[0]}/{r[1]}"]
            n_notes += 1
            body = "".join(f"<p>{fmt_note(s)}</p>" for s in n.get("summary", []))
            if n.get("for_us"):
                body += f'<p class="forus"><b>Для нас:</b> {fmt_note(n["for_us"])}</p>'
            if n.get("radar"):
                body += ('<p class="forus"><b>Проверить в радаре:</b> '
                         + ", ".join(f'<code class="inline">{html.escape(p)}</code>' for p in n["radar"]) + "</p>")
            if n.get("installed"):
                body += f'<p class="mark ok">✓ Установлено: {fmt_note(n["installed"])}</p>'
            elif n.get("declined"):
                body += f'<p class="mark no">Не ставили: {fmt_note(n["declined"])}</p>'
            if n.get("noted"):  # user 27.09: lessons she took into account are marked, and listed in «Не забыть»
                body += f'<p class="mark note">📌 Принято к сведению: {fmt_note(n["noted"])}</p>'
            out.append(
                f'<article class="article" data-ch="{html.escape(r[0])}">{num_tag(f"{r[0]}/{r[1]}", r[2])}{head(r[0], local(r[2]), is_new(r))}'
                f'<h3 class="headline">{html.escape(n["headline"])}</h3>{body}'
                f'<a class="src" href="https://t.me/{r[0]}/{r[1]}" target="_blank" rel="noopener">Открыть пост в Telegram ↗</a></article>')
        if only:
            out.append("</div>")
        return "\n".join(out) if items else ""

    biz, tool, soft = column("biz"), column("tool"), column("soft")
    main_html = [f'<div class="cols"><div class="col">{biz}</div><div class="col">{tool}</div></div>', soft]
    # «Чат shopify_chat» (user 23.09.2026): important questions with their answers right under them
    for i, chat in enumerate(CHATS):
        main_html.insert(1 + i, chat_block(conn, notes, chat))
    for i, blk in enumerate(dict.fromkeys(OWN_BLOCKS.values())):  # several channels may share one block
        main_html.insert(1 + i, column(("tool", "biz", "soft"), only=blk))
    # «Мода и тренды» — a separate page (user 23.09.2026: fashion news only as a guide for the trend radar,
    # never mixed with dropshipping / AI); here only a link to it
    t_biz, t_tool, t_soft = column("biz", True), column("tool", True), column("soft", True)
    fashion_rows = [r for r in rows if r[0] in TREND_CHANNELS and notes.get(f"{r[0]}/{r[1]}", {}).get("cat") in ("biz", "tool", "soft")]
    build_fashion(fashion_rows, notes, t_biz, t_tool, t_soft)
    main_html.append(f'<a class="fashion-link" href="{FASHION_URL}" target="_blank" rel="noopener">'
                     f'<b>Мода и тренды — в дашборде радара трендов ↗</b><span>{len(fashion_rows)} новостей из модных каналов '
                     'и что из них проверить в радаре трендов</span></a>')
    # posts the site hides ("Please open Telegram"): never silently skipped — shown until retold in notes
    hidden = [r for r in panel_rows if r[3] == tm.HIDDEN and notes.get(f"{r[0]}/{r[1]}", {}).get("cat") in (None, "skip")]
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
            f'{num_tag(f"{r[0]}/{r[1]}", r[2])}<span class="otitle">{html.escape(title)}</span>'
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
    # «Не забыть» (принятое к сведению) убрано с панели 07.10 — оно в скилле noted-news (noted_to_skill.py)

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
            .replace("__EXTRA__", "".join(p.read_text(encoding="utf-8") for p in (BOOKS, BOOKS_FULL) if p.exists())
                     + (EXTRA.read_text(encoding="utf-8") if EXTRA.exists() else "")))
    OUT.write_text(number_posts(page), encoding="utf-8")
    print(f"Панель: {OUT} — постов {len(rows)}, новых {new_count}, в «Главном» {n_notes}")
    return rows, is_new


STALE_HOURS = 30  # 12.10: a collection gap went unnoticed for 3.5 days elsewhere (boringmarketer/1331) -> warn, no schedule


def warn_if_stale(conn):
    """Print a warning when the newest post in the DB is older than STALE_HOURS (collector or VPN probably broke)."""
    last = conn.execute("SELECT max(post_date) FROM posts").fetchone()[0]
    if not last:
        return
    age = datetime.now(timezone.utc) - datetime.fromisoformat(last)
    if age > timedelta(hours=STALE_HOURS):
        print(f"\n!!! ВНИМАНИЕ: последний пост в базе от {local(last):%d.%m %H:%M} — {age.total_seconds() / 3600:.0f} ч назад "
              f"(порог {STALE_HOURS} ч). Похоже, сбор не работает: проверить VPN/Happ и доступ к t.me/s.")


def main():
    if "--seen" in sys.argv:  # she said «прочла»: everything in the DB and every chat note becomes read
        conn = sqlite3.connect(tm.DB_PATH)
        notes = load_json(NOTES, {})
        if "--from" in sys.argv:  # 29.09 «прочла первый блок до 1 сентября»: only the «по делу» + «инструменты» columns,
            # posts from that date on; older posts, «фоново», chats, Python, fashion and courses stay unread
            since = sys.argv[sys.argv.index("--from") + 1]
            keys = SEEN | {f"{c}/{i}" for c, i, d in conn.execute("SELECT channel, post_id, post_date FROM posts")
                           if local(d).date().isoformat() >= since and c not in TREND_CHANNELS and c not in OWN_BLOCKS
                           and c != COURSE_CHANNEL and notes.get(f"{c}/{i}", {}).get("cat") in ("biz", "tool")}
        else:
            keys = SEEN | {f"{c}/{i}" for c, i in conn.execute("SELECT channel, post_id FROM posts")} \
                   | {k for k, v in notes.items() if v.get("cat") == "chat"}
        SEEN_FILE.write_text(json.dumps({"_why": "прочитанное: на панель не выводится, кроме принятого к сведению",
                                         "keys": sorted(keys)}, ensure_ascii=False), encoding="utf-8")
        print(f"Отмечено прочитанным: {len(keys)}")
        sys.exit(0)
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
    warn_if_stale(conn)
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
  .article, .offer { position: relative; }
  .postnum { position: absolute; top: -10px; left: -10px; z-index: 2; min-width: 30px; height: 30px; padding: 0 8px;
    border-radius: 15px; background: var(--bg); color: var(--ink-soft); border: 1px solid var(--border); font: 700 15px/30px Arial, sans-serif; text-align: center;
    box-shadow: var(--shadow); }
  .offer .postnum { left: auto; right: -10px; }
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
  .mark.note { background: var(--tool-bg); color: var(--tool); }
  .remember { margin-top: 12px; font-size: 13px; color: var(--ink-soft); background: var(--tool-bg);
              border: 1px solid var(--tool-border); border-radius: 12px; padding: 10px 14px; }
  .remember summary { cursor: pointer; color: var(--tool); }
  .remember summary b { color: var(--tool); }
  .rem-note { margin: 6px 0 4px; font-size: 12.5px; color: var(--muted); }
  .rem-group { margin-top: 8px; }
  .rem-group b { color: var(--ink); font-size: 12.5px; }
  .rem-group ul { margin: 3px 0 0; padding-left: 18px; }
  .rem-group li { margin: 2px 0; }
  .rem-group a { color: var(--ink-soft); text-decoration: none; border-bottom: 1px dotted var(--tool-border); }
  .installed { margin-top: 12px; font-size: 13px; color: var(--ink-soft); background: var(--biz-bg);
               border: 1px solid var(--biz-border); border-radius: 12px; padding: 10px 14px; }
  .installed b { color: var(--biz); }
  .chat-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 480px), 1fr)); gap: 0 24px; align-items: start; }
  .chat-thread { margin-top: 10px; font-size: 13px; border-top: 1px solid var(--border-soft); padding-top: 8px; }
  .chat-thread > b { font-size: 12px; color: var(--muted); display: block; margin-bottom: 6px; }
  .chat-q { background: var(--tool-bg); border-radius: 10px; padding: 7px 10px; margin: 8px 0 4px; color: var(--ink); }
  .chat-a { border-left: 3px solid var(--biz-border); padding: 3px 0 3px 10px; margin: 4px 0 4px 14px; color: var(--ink-soft); }
  .chat-q .date, .chat-a .date { font-size: 10.5px; }
  .fashion-link { display: flex; flex-direction: column; gap: 4px; margin: 36px 0 8px; padding: 16px 20px; text-decoration: none;
                  color: var(--ink); background: var(--surface); border: 1px solid var(--biz-border); border-radius: 16px; }
  .fashion-link b { font-size: 17px; color: var(--biz); }
  .fashion-link span { font-size: 13px; color: var(--muted); }
  .trends-h { font-size: 24px; margin: 44px 0 6px; padding-top: 28px; border-top: 1px solid var(--border); }
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
  <a class="navlink" href="#design">Дизайн сайтов</a>
  <a class="navlink" href="#marketing">Маркетинг</a>
  <a class="navlink" href="#python">Python</a>
  <a class="navlink" href="#books">Книги</a>
  <a class="navlink" href="#books-all">Все приёмы</a>
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
