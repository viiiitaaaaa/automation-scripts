"""
Builds the Trend Radar dashboard (single self-contained HTML) from the latest
radar outputs. Re-run after run_radar.py, then publish the file.
Output: data/reports/trend_radar_dashboard.html
"""
import json
from datetime import date
from pathlib import Path

import pandas as pd

from radar_curves import build_block

LOCAL = Path(r"C:\Users\User\dolphin_anty\trend_radar_dashboard.html")

CHANNELS = [
    {"key": "check_google", "short": "G", "name": "Google", "status": "ok",
     "note": "растущие запросы (10 широких слов) + история за 2 года: 8 недель к тем же неделям прошлого года"},
    {"key": "check_pinterest", "short": "P", "name": "Pinterest", "status": "ok",
     "note": "2 года по неделям: рост к прошлому году в среднем за 8 недель, метка сезона"},
    {"key": "check_youtube", "short": "Y", "name": "YouTube", "status": "ok",
     "note": "поиск на YouTube за 2 года (Google Trends) + YouTube API для лидеров: просмотры свежих видео к прошлому году, комментарии «где купить»"},
    {"key": "check_tiktok", "short": "T", "name": "TikTok", "status": "partial",
     "note": "90 дней; видна только мода из общего топ-100 — фильтр «Одежда» пока не работает"},
    {"key": "check_amazon", "short": "A", "name": "Amazon", "status": "ok",
     "note": "новинки + хиты продаж в 8 разделах женской одежды"},
    {"key": "check_retailers", "short": "R", "name": "Бренды", "status": "ok",
     "note": "новинки Zara, ASOS, Aritzia, Free People"},
]
PENDING = [
    ("Etsy", "ключ есть, ждём одобрения Etsy (Pending Personal Approval)"),
    ("Reddit", "для коммерческого использования нужно письменное одобрение Reddit — пока исключён"),
    ("Meta Ad Library", "нужна платёжка"),
    ("Google Merchant Center", "Best Sellers Google Shopping; регистрация просит карту — отложено"),
    ("Keyword Tool", "платный тариф"),
]


def main():
    cand = pd.read_csv("data/reports/radar_candidates.csv")
    cand = cand.sort_values(["checks_passed", "pin_yoy_pct"], ascending=[False, False], na_position="last")
    for col in ["google_yoy_pct", "pin_mom_pct", "pin_yoy_pct", "youtube_yoy_pct"]:
        cand[col] = cand[col].round(0)
    cand["amazon_median_price"] = cand["amazon_median_price"].round(2)
    ac_f = Path("data/processed/autocomplete_summary.csv")
    if ac_f.exists():  # what people type after the item name (Google / YouTube / Amazon)
        ac = pd.read_csv(ac_f)[["candidate", "top_modifiers", "colors", "amazon_examples"]]
        ac = ac.rename(columns={"top_modifiers": "ac_modifiers", "colors": "ac_colors", "amazon_examples": "ac_amazon"})
        cand = cand.merge(ac, on="candidate", how="left")
    attrs_f = Path("data/processed/retailer_attributes.csv")
    attrs = pd.read_csv(attrs_f) if attrs_f.exists() else pd.DataFrame()
    attrs = attrs[attrs["brands"] >= 2] if not attrs.empty else attrs

    payload = {
        "date": date.today().strftime("%d.%m.%Y"),
        "channels": CHANNELS,
        "pending": [{"name": n, "why": w} for n, w in PENDING],
        "candidates": json.loads(cand.to_json(orient="records", force_ascii=False)),
        "attributes": json.loads(attrs.to_json(orient="records", force_ascii=False)) if not attrs.empty else [],
    }
    data_json = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")

    curves = build_block(cand, with_header=False, date_str=payload["date"])
    html = TEMPLATE.replace("__CURVES__", curves).replace("__DATA__", data_json)
    out = Path("data/reports/trend_radar_dashboard.html")
    out.write_text(html, encoding="utf-8")
    print(f"Сохранено: {out} ({len(cand)} кандидатов)")

    update_local(cand, payload["date"])


def update_local(cand, date_str):
    """Put the curve cards on top of the local Dolphin dashboard, keep the old 12.09 collection below."""
    if not LOCAL.exists():
        print(f"Нет файла {LOCAL} — пропускаю")
        return
    page = LOCAL.read_text(encoding="utf-8")
    block = build_block(cand, with_header=True, date_str=date_str,
                        archive_note="Ниже — архив: сбор 12–13.09 по старой логике (Google Trends 12 мес, TikTok-видео, Instagram).")
    start, end = page.find("<!-- RADAR:START"), page.find("<!-- RADAR:END -->")
    if start != -1 and end != -1:
        page = page[:start] + block + page[end + len("<!-- RADAR:END -->\n"):]
    else:
        anchor = '<div class="wrap">'
        i = page.index(anchor) + len(anchor)
        page = page[:i] + "\n" + block + page[i:]
        page = page.replace("<h1>Радар трендов: одежда</h1>",
                            '<h2 style="font-size:22px;margin:6px 0 8px">Архив: радар трендов 12–13.09</h2>', 1)
    LOCAL.write_text(page, encoding="utf-8")
    print(f"Обновлён локальный дашборд: {LOCAL}")


TEMPLATE = r"""<title>Trend Radar</title>
<meta name="description" content="Кандидаты в тренды женской одежды: сколько независимых каналов подтверждают каждый">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Work+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap">
<style>
  :root {
    --page: #f7f6f2; --surface: #ffffff; --surface-2: #efede6;
    --text: #1d1f1a; --text-2: #4b4c45; --muted: #83827a; --border: #e0ddd2;
    --pass: #2f7d5b; --pass-bg: #e3f1ea;
    --fail: #b9b6aa; --fail-bg: #f1efe8;
    --test: #2f7d5b; --test-bg: #e3f1ea;
    --watch: #a0671a; --watch-bg: #f7ecd9;
    --reject: #8a8980; --reject-bg: #efede6;
    --season: #b0472f; --season-bg: #f7e4df;
    --bar: #3f6fa8; --bar-neg: #b0472f;
    color-scheme: light dark;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --page: #151613; --surface: #1f201c; --surface-2: #2a2b26;
      --text: #eceae2; --text-2: #c4c2b6; --muted: #8f8e84; --border: #35362f;
      --pass: #6cc49a; --pass-bg: #1d3329; --fail: #5d5c55; --fail-bg: #262722;
      --test: #6cc49a; --test-bg: #1d3329; --watch: #e0a857; --watch-bg: #3a2d19;
      --reject: #9a998f; --reject-bg: #2a2b26; --season: #e5876f; --season-bg: #3d231c;
      --bar: #7ea7dc; --bar-neg: #e5876f;
    }
  }
  :root[data-theme="dark"] {
    --page: #151613; --surface: #1f201c; --surface-2: #2a2b26;
    --text: #eceae2; --text-2: #c4c2b6; --muted: #8f8e84; --border: #35362f;
    --pass: #6cc49a; --pass-bg: #1d3329; --fail: #5d5c55; --fail-bg: #262722;
    --test: #6cc49a; --test-bg: #1d3329; --watch: #e0a857; --watch-bg: #3a2d19;
    --reject: #9a998f; --reject-bg: #2a2b26; --season: #e5876f; --season-bg: #3d231c;
    --bar: #7ea7dc; --bar-neg: #e5876f;
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--page); color: var(--text);
         font-family: "Work Sans", system-ui, sans-serif; font-size: 14.5px; line-height: 1.5; }
  .wrap { max-width: 1060px; margin: 0 auto; padding-inline: 20px; padding-block: 28px 72px; }
  h1, h2 { font-family: "Fraunces", Georgia, serif; margin: 0; text-wrap: balance; }
  h1 { font-size: 30px; }
  h2 { font-size: 20px; margin-bottom: 4px; }
  .mono { font-family: "JetBrains Mono", ui-monospace, monospace; }
  .eyebrow { font: 600 11px "JetBrains Mono", monospace; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
  .lead { color: var(--text-2); max-width: 66ch; margin: 8px 0 0; }
  section { margin-top: 36px; }
  .note { color: var(--muted); font-size: 13px; margin: 0 0 14px; max-width: 70ch; }

  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-top: 20px; }
  .stat { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 12px 16px; }
  .stat .n { font: 700 24px "Fraunces", serif; font-variant-numeric: tabular-nums; }
  .stat .l { font-size: 12px; color: var(--muted); }

  .rule { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; font-size: 13px; color: var(--text-2); }
  .rule span { background: var(--surface); border: 1px solid var(--border); border-radius: 999px; padding: 4px 12px; }

  .filters { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
  .filters button { font: 600 12.5px "Work Sans", sans-serif; color: var(--text-2); background: var(--surface);
                    border: 1px solid var(--border); border-radius: 999px; padding: 6px 14px; cursor: pointer; min-height: 34px; }
  .filters button[aria-pressed="true"] { background: var(--text); color: var(--page); border-color: var(--text); }
  .filters button:focus-visible, summary:focus-visible { outline: 2px solid var(--bar); outline-offset: 2px; }

  .list { display: flex; flex-direction: column; gap: 8px; }
  details.row { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; }
  details.row.test { border-color: var(--test); box-shadow: 0 0 0 1px var(--test) inset; }
  summary { list-style: none; cursor: pointer; padding: 12px 16px;
            display: grid; grid-template-columns: minmax(150px, 1.6fr) auto auto minmax(110px, 1fr); gap: 14px; align-items: center; }
  summary::-webkit-details-marker { display: none; }
  .name { font-weight: 600; }
  .name small { display: block; font-weight: 400; color: var(--muted); font-size: 12px; }
  .checks { display: flex; gap: 4px; }
  .chk { width: 26px; height: 26px; border-radius: 7px; display: grid; place-items: center;
         font: 600 11px "JetBrains Mono", monospace; }
  .chk.on { background: var(--pass-bg); color: var(--pass); }
  .chk.off { background: var(--fail-bg); color: var(--fail); }
  .pill { font: 600 11.5px "JetBrains Mono", monospace; padding: 4px 10px; border-radius: 999px; white-space: nowrap; }
  .pill.TEST { background: var(--test-bg); color: var(--test); }
  .pill.WATCH { background: var(--watch-bg); color: var(--watch); }
  .pill.REJECT { background: var(--reject-bg); color: var(--reject); }
  .pill.season { background: var(--season-bg); color: var(--season); margin-left: 6px; }
  .yoy { display: flex; align-items: center; gap: 8px; font-size: 12.5px; font-variant-numeric: tabular-nums; }
  .yoy .track { flex: 1; height: 8px; background: var(--surface-2); border-radius: 4px; position: relative; min-width: 60px; }
  .yoy .zero { position: absolute; left: 50%; top: -2px; bottom: -2px; width: 1px; background: var(--muted); }
  .yoy .fill { position: absolute; top: 0; bottom: 0; border-radius: 4px; }
  .evidence { padding: 0 16px 14px; display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; }
  .ev { background: var(--page); border-radius: 10px; padding: 10px 12px; font-size: 13px; }
  .ev b { display: block; font-size: 11px; font-family: "JetBrains Mono", monospace; letter-spacing: .05em;
          text-transform: uppercase; color: var(--muted); margin-bottom: 3px; }
  .ev .no { color: var(--muted); }

  .grid2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 12px; }
  .card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; }
  .ch { display: flex; gap: 10px; align-items: flex-start; padding: 8px 0; border-top: 1px solid var(--border); }
  .ch:first-of-type { border-top: 0; }
  .dot { width: 9px; height: 9px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
  .dot.ok { background: var(--pass); } .dot.partial { background: var(--watch); } .dot.wait { background: var(--fail); }
  .ch small { display: block; color: var(--muted); font-size: 12px; }
  .attr { display: flex; justify-content: space-between; gap: 10px; padding: 7px 0; border-top: 1px solid var(--border); font-size: 13.5px; }
  .attr:first-of-type { border-top: 0; }
  .attr .b { color: var(--muted); font-size: 12px; text-align: right; }

  @media (max-width: 640px) {
    summary { grid-template-columns: 1fr auto; }
    .yoy { grid-column: 1 / -1; }
  }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>

<div class="wrap">
  <div class="eyebrow">Trend Radar · женская одежда · США</div>
  <h1>Какие вещи подтверждают сразу несколько каналов</h1>
  <p class="lead">Один сигнал — это шум. Радар проверяет каждого кандидата шестью независимыми «свидетелями» и считает, сколько из них видят рост. Данные на <span class="mono" id="dt"></span>.</p>
  <div class="stats" id="stats"></div>
  <div class="rule">
    <span><b>4–6 проверок</b> — тестировать</span>
    <span><b>3</b> — наблюдать</span>
    <span><b>0–2</b> — отказ</span>
    <span><b>Сезон</b> — в эти же недели прошлого года был такой же подъём</span>
  </div>

  <section>
    <h2>Кандидаты</h2>
    <p class="note">G — Google, P — Pinterest, Y — поиск на YouTube (у всех трёх: последние 8 недель выше тех же недель прошлого года на 15%+), T — TikTok, A — Amazon (≥2 товара), R — бренды (≥2 ритейлера). Полоска — рост на Pinterest к прошлому году, в среднем за 8 недель. Нажмите на строку, чтобы увидеть доказательства.</p>
    <div class="filters" role="group" aria-label="Фильтр по решению">
      <button type="button" data-f="ALL" aria-pressed="true">Все</button>
      <button type="button" data-f="TEST" aria-pressed="false">Тестировать</button>
      <button type="button" data-f="WATCH" aria-pressed="false">Наблюдать</button>
      <button type="button" data-f="REJECT" aria-pressed="false">Отказ</button>
    </div>
    <div class="list" id="list"></div>
  </section>

  <section>
    <h2>Кривые</h2>
    <p class="note">Вся кривая за 2 года. Зелёная полоса — последние 8 недель, серая — те же недели год назад: радар сравнивает их. Горб справа выше прошлогоднего — настоящий рост; одинаковые — просто сезон. Шкала 0–100, где 100 — пик за 2 года.</p>
    __CURVES__
  </section>

  <section class="grid2">
    <div>
      <h2>Каналы</h2>
      <p class="note">Что радар уже слушает и чего пока не хватает.</p>
      <div class="card" id="channels"></div>
    </div>
    <div>
      <h2>Что выпускают бренды</h2>
      <p class="note">Признаки, которые есть в новинках сразу у нескольких ритейлеров.</p>
      <div class="card" id="attrs"></div>
    </div>
  </section>
</div>

<script id="radar-data" type="application/json">__DATA__</script>
<script>
(() => {
  const D = JSON.parse(document.getElementById("radar-data").textContent);
  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const DEC = { TEST: "тестировать", WATCH: "наблюдать", REJECT: "отказ" };
  const GROUP = { material: "ткань", pattern: "принт", neckline: "ворот", silhouette: "силуэт", detail: "деталь", audience_occasion: "аудитория" };
  const ATTR = { knit: "трикотаж", oversized: "оверсайз", plaid: "клетка", roll_neck: "высокий ворот", stripe: "полоска",
                 faux_fur: "искусственный мех", v_neck: "V-вырез", leather: "кожа", wool: "шерсть", boat_neck: "лодочка",
                 maxi: "макси", lace: "кружево", cashmere: "кашемир", mesh: "сетка", drawstring: "кулиска",
                 plus_size: "plus size", ruffle: "рюши", bow: "бант", satin: "атлас", suede: "замша", sequin: "пайетки",
                 flannel: "фланель", leopard: "леопард", floral: "цветы", ribbed: "рубчик", denim: "деним", halter: "халтер" };

  $("dt").textContent = D.date;
  const c = D.candidates, n = (d) => c.filter((x) => x.decision === d).length;
  $("stats").innerHTML = [
    [c.length, "кандидатов проверено"], [n("TEST"), "тестировать"], [n("WATCH"), "наблюдать"],
    [D.channels.length, "каналов подключено"],
  ].map(([v, l]) => `<div class="stat"><div class="n">${v}</div><div class="l">${l}</div></div>`).join("");

  const pct = (v) => v === null || v === undefined ? null : Number(v);
  const yoyBar = (v) => {
    if (v === null) return `<div class="yoy"><span class="mono" style="color:var(--muted)">нет на Pinterest</span></div>`;
    const w = Math.min(Math.abs(v), 100) / 2;
    const left = v >= 0 ? 50 : 50 - w;
    const col = v >= 0 ? "var(--bar)" : "var(--bar-neg)";
    return `<div class="yoy"><div class="track"><div class="zero"></div><div class="fill" style="left:${left}%;width:${w}%;background:${col}"></div></div><span class="mono">${v > 0 ? "+" : ""}${v}%</span></div>`;
  };
  const ev = (label, body) => `<div class="ev"><b>${label}</b>${body || '<span class="no">нет сигнала</span>'}</div>`;

  function render(filter) {
    $("list").innerHTML = c.filter((x) => filter === "ALL" || x.decision === filter).map((x) => {
      const chips = D.channels.map((ch) => `<span class="chk ${x[ch.key] ? "on" : "off"}" title="${ch.name}: ${x[ch.key] ? "да" : "нет"}">${ch.short}</span>`).join("");
      const y = pct(x.pin_yoy_pct), m = pct(x.pin_mom_pct);
      const g = [x.google_rising_top, x.google_yoy_pct !== null && x.google_yoy_pct !== undefined ? `8 недель к прошлому году: ${x.google_yoy_pct > 0 ? "+" : ""}${x.google_yoy_pct}%` : ""].filter(Boolean).map(esc).join("<br>");
      const lift = x.pin_season_lift_prev;
      const p = m === null && y === null ? "" : `за месяц ${m > 0 ? "+" : ""}${m ?? "—"}% · 8 недель к прошлому году ${y > 0 ? "+" : ""}${y ?? "—"}%`
        + (lift !== null && lift !== undefined ? `<br>год назад в эти недели: ${lift > 0 ? "+" : ""}${Math.round(lift)}%` : "");
      const a = x.amazon_items ? `${x.amazon_items} товаров (новинок ${x.amazon_new_releases}), медиана $${x.amazon_median_price}` : "";
      return `<details class="row ${x.decision === "TEST" ? "test" : ""}">
        <summary>
          <div class="name">${esc(x.candidate)}<small>${x.checks_passed} из ${D.channels.length} проверок</small></div>
          <div class="checks">${chips}</div>
          <div><span class="pill ${x.decision}">${DEC[x.decision]}</span>${x.seasonal_flag ? '<span class="pill season">сезон</span>' : ""}</div>
          ${yoyBar(y)}
        </summary>
        <div class="evidence">
          ${ev("Google", g)}${ev("Pinterest", p)}${ev("YouTube", [
            x.youtube_yoy_pct === null || x.youtube_yoy_pct === undefined ? "" : `поиск, 8 недель к прошлому году: ${x.youtube_yoy_pct > 0 ? "+" : ""}${x.youtube_yoy_pct}%`,
            x.yt_views_yoy_pct === null || x.yt_views_yoy_pct === undefined ? "" : `просмотры видео за 90 дн: ${x.yt_views_yoy_pct > 0 ? "+" : ""}${Math.round(x.yt_views_yoy_pct)}% к прошлому году`,
            x.yt_comments_read ? `«где купить»: ${x.yt_intent_comments} из ${x.yt_comments_read} комментариев` : ""
          ].filter(Boolean).join("<br>"))}${ev("TikTok", esc(x.tiktok_hashtags))}
          ${ev("Amazon", a)}${ev("Бренды", x.retailer_brands ? `${x.retailer_brands}: ${esc(x.retailer_list)}` : "")}
        </div>
      </details>`;
    }).join("") || '<p class="note">Нет кандидатов в этой группе.</p>';
  }
  render("ALL");
  document.querySelectorAll(".filters button").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll(".filters button").forEach((o) => o.setAttribute("aria-pressed", String(o === b)));
    render(b.dataset.f);
  }));

  $("channels").innerHTML =
    D.channels.map((ch) => `<div class="ch"><span class="dot ${ch.status}"></span><div><b>${ch.name}</b><small>${esc(ch.note)}</small></div></div>`).join("") +
    D.pending.map((p) => `<div class="ch"><span class="dot wait"></span><div><b>${p.name}</b><small>не подключено — ${esc(p.why)}</small></div></div>`).join("");

  $("attrs").innerHTML = D.attributes.length ? D.attributes.map((a) =>
    `<div class="attr"><span>${ATTR[a.attribute] || esc(a.attribute)} <span style="color:var(--muted)">· ${GROUP[a.group] || a.group}</span></span><span class="b">${a.brands} бренда · ${a.items} шт</span></div>`).join("")
    : '<p class="note">Нет данных.</p>';
})();
</script>
"""

if __name__ == "__main__":
    main()
