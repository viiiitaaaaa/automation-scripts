"""
Curve cards for every radar candidate: this year's weekly interest vs the same
weeks a year ago (Pinterest, and Google where 2-year history exists).
build_block() returns a self-contained HTML fragment (style + markup + script)
that works inside both dashboards -- colours come from the host page tokens.
"""
import html
import json
from pathlib import Path

import pandas as pd

from src.processors.candidate_matrix import MIN_NONZERO

WEEKS = 52


def pinterest_aliases() -> dict:
    """candidate -> wording Pinterest Trends knows (config/candidates.csv, column pinterest_term)."""
    c = pd.read_csv("config/candidates.csv")
    if "pinterest_term" not in c:
        return {}
    return {r.candidate: r.pinterest_term for r in c.itertuples() if isinstance(r.pinterest_term, str) and r.pinterest_term}


def _pinterest_series():
    """term -> weekly points, keyed by CANDIDATE: latest metrics_*.json plus variants_*.json
    (other wordings, run_extra_signals.py); a candidate with an alias gets its alias's curve."""
    root = Path("data/raw/pinterest_trends")
    files = sorted(root.glob("metrics_*.json"))[-1:] + sorted(root.glob("variants_*.json"))
    out = {}
    for f in files:   # later files win
        for batch in json.loads(f.read_text(encoding="utf-8")).values():
            for t in batch:
                if not t:
                    continue
                pts = [(c["date"], c["normalizedCount"]) for c in t.get("counts", [])
                       if c.get("normalizedCount") is not None]
                out[t["term"]] = pts
    for cand, alias in pinterest_aliases().items():
        if alias in out:
            out[cand] = out[alias]
    return out


def _google_series(root="data/normalized/google_trends"):
    root = Path(root)
    if not root.exists():
        return {}
    g = pd.read_parquet(root).sort_values("date").drop_duplicates(["date", "keyword", "region"], keep="last")
    g = g[(g["region"] == "US") & ~g["is_partial"].astype(bool)]
    out = {}
    for k, grp in g.groupby("keyword"):
        if grp["interest"].max() > 0:   # all zeros = too few searches to draw anything
            out[k] = [(str(d)[:10], float(v)) for d, v in zip(grp["date"], grp["interest"])]
    return out


def _split(pts):
    """The whole 2-year weekly curve, oldest first."""
    pts = pts[-2 * WEEKS:]
    if len(pts) < WEEKS + 4:
        return None
    vals = [v for _, v in pts]
    sparse = sum(1 for v in vals if v) / len(vals) < MIN_NONZERO
    return {"dates": [d for d, _ in pts], "vals": vals, "sparse": sparse}


def gaps_html(gaps) -> str:
    """Static 'what the radar is missing' cards for the local page (styles live in BLOCK)."""
    if not gaps:
        return ""
    e = html.escape
    cards = "".join(
        f'<div class="rd-gap"><div class="rd-gap-head"><b>{e(g["what"])}</b><span>{e(g["have"])}</span></div>'
        f'<div class="rd-gap-why">{e(g["why"])}</div><div class="rd-gap-fix">→ {e(g["fix"])}</div></div>'
        for g in gaps)
    return (f'<h2 class="rd-h2">Чего не хватает радару</h2>'
            f'<p class="rd-lead">Что ещё не собирается или собрано не по всем кандидатам.</p>'
            f'<div class="rd-gaps">{cards}</div>')


def build_block(cand: pd.DataFrame, with_header: bool, date_str: str, archive_note: str = "",
                gaps=None) -> str:
    pin, goo = _pinterest_series(), _google_series()
    yt = _google_series("data/normalized/google_trends_youtube")
    shop = _google_series("data/normalized/google_trends_shopping")
    aliases = pinterest_aliases()
    # colour follows the item (color_slot 1-8 in config/candidates.csv, else its place there), never its rank on the page
    cfg = pd.read_csv("config/candidates.csv")
    order = {c: i for i, c in enumerate(cfg["candidate"])}
    fixed = dict(zip(cfg["candidate"], cfg["color_slot"])) if "color_slot" in cfg else {}
    rows = []
    for _, r in cand.iterrows():
        name = r["candidate"]
        rec = json.loads(r.to_json(force_ascii=False))
        s = fixed.get(name)
        rec["color_slot"] = int(s) if pd.notna(s) and s else order.get(name, 0) % 8 + 1
        rec["pin_curve"] = _split(pin[name]) if name in pin else None
        rec["pin_alias"] = aliases.get(name, "")
        rec["google_curve"] = _split(goo[name]) if name in goo else None
        rec["shop_curve"] = _split(shop[name]) if name in shop else None
        rec["youtube_curve"] = _split(yt[name]) if name in yt else None
        rows.append(rec)
    data = json.dumps(rows, ensure_ascii=False).replace("</", "<\\/")
    n_curves = sum(1 for x in rows if x["pin_curve"] or x["google_curve"] or x["shop_curve"] or x["youtube_curve"])
    header = f"""
  <div class="rd-eyebrow">Новый радар · 6 каналов · данные на {date_str}</div>
  <h1 class="rd-h1">Кривые по каждому кандидату</h1>
  <p class="rd-lead">Вся кривая интереса за 2 года, неделя за неделей. Радар сравнивает последние 8 недель с теми же неделями
  год назад. Если справа горб выше, чем год назад, — вещь растёт по-настоящему;
  если горбы одинаковые — это сезон, который повторяется каждый год. Шкала 0–100: 100 — пик интереса к слову за 2 года.</p>""" if with_header else ""
    archive = gaps_html(gaps) + (f'<div class="rd-archive">{archive_note}</div>\n' if archive_note else "")
    return BLOCK.replace("__HEADER__", header).replace("__ARCHIVE__", archive).replace("__DATA__", data) \
        .replace("__NCURVES__", str(n_curves)).replace("__NTOTAL__", str(len(rows)))


BLOCK = r"""<!-- RADAR:START (генерируется build_dashboard.py — правки вручную затрутся) -->
<style>
  .rd { --rd-surface: var(--surface-1, var(--surface)); --rd-soft: var(--surface-2);
        --rd-text: var(--text-primary, var(--text)); --rd-text-2: var(--text-secondary, var(--text-2));
        --rd-line: var(--series-1, var(--bar)); --rd-grid: var(--gridline, var(--border));
        --rd-prev: var(--baseline, var(--muted));
        --rd-good: #2f7d5b; --rd-good-bg: rgba(47,125,91,.13);
        --rd-warn: #a0671a; --rd-warn-bg: rgba(160,103,26,.14);
        --rd-hot: #b0472f; --rd-hot-bg: rgba(176,71,47,.13);
        /* 8-slot categorical palette (validated for CVD), one colour per item */
        --c1: #2a78d6; --c2: #eb6834; --c3: #1baf7a; --c4: #eda100;
        --c5: #e87ba4; --c6: #008300; --c7: #4a3aa7; --c8: #e34948; }
  @media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .rd {
        --rd-good: #6cc49a; --rd-good-bg: rgba(108,196,154,.16); --rd-warn: #e0a857; --rd-warn-bg: rgba(224,168,87,.16);
        --rd-hot: #e5876f; --rd-hot-bg: rgba(229,135,111,.16);
        --c1: #3987e5; --c2: #d95926; --c3: #199e70; --c4: #c98500;
        --c5: #d55181; --c6: #008300; --c7: #9085e9; --c8: #e66767; } }
  :root[data-theme="dark"] .rd {
        --rd-good: #6cc49a; --rd-good-bg: rgba(108,196,154,.16); --rd-warn: #e0a857; --rd-warn-bg: rgba(224,168,87,.16);
        --rd-hot: #e5876f; --rd-hot-bg: rgba(229,135,111,.16);
        --c1: #3987e5; --c2: #d95926; --c3: #199e70; --c4: #c98500;
        --c5: #d55181; --c6: #008300; --c7: #9085e9; --c8: #e66767; }
  .rd { margin-bottom: 44px; }
  .rd-eyebrow { font: 600 11.5px "IBM Plex Mono", "JetBrains Mono", ui-monospace, monospace; letter-spacing: .09em;
                text-transform: uppercase; color: var(--rd-line); }
  .rd-h1 { font-size: clamp(24px, 3.4vw, 34px); line-height: 1.15; margin: 6px 0 8px; text-wrap: balance; }
  .rd-lead { color: var(--rd-text-2); font-size: 14.5px; max-width: 70ch; line-height: 1.55; margin: 0; }
  .rd-bar { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 18px; margin-top: 16px; }
  .rd-legend { display: flex; flex-wrap: wrap; gap: 14px; font-size: 12px; color: var(--rd-text-2); }
  .rd-legend svg { vertical-align: middle; margin-right: 5px; }
  .rd-filters { display: flex; gap: 6px; flex-wrap: wrap; margin-left: auto; }
  .rd-filters button { font: 600 12.5px inherit; font-family: inherit; color: var(--rd-text-2); background: var(--rd-surface);
                       border: 1px solid var(--border); border-radius: 999px; padding: 6px 13px; min-height: 34px; cursor: pointer; }
  .rd-filters button[aria-pressed="true"] { background: var(--rd-text); color: var(--page); border-color: var(--rd-text); }
  .rd-filters button:focus-visible { outline: 2px solid var(--rd-line); outline-offset: 2px; }
  /* one wide card per row, charts two-up inside: the curves are the point of the page */
  .rd-grid { display: grid; grid-template-columns: 1fr; gap: 18px; margin-top: 16px; }
  .rd-charts { display: grid; grid-template-columns: 1fr; gap: 18px; }   /* one chart per row, full card width */
  .rd-card { background: var(--rd-surface); border: 1px solid var(--border); border-left: 8px solid var(--k, var(--border));
             border-radius: 12px; padding: 18px 22px; display: flex; flex-direction: column; gap: 12px; }
  .rd-sw { display: inline-block; width: 14px; height: 14px; border-radius: 4px; background: var(--k); margin-right: 8px;
           vertical-align: -1px; }
  .rd-card.is-test { border-color: var(--rd-good); border-left-color: var(--k, var(--rd-good)); box-shadow: 0 0 0 1px var(--rd-good); }
  .rd-head { display: flex; justify-content: space-between; gap: 10px; align-items: flex-start; }
  .rd-name { font-weight: 600; font-size: 18px; line-height: 1.3; }
  .rd-sub { font-size: 12.5px; color: var(--muted); margin-top: 2px; }
  .rd-pills { display: flex; gap: 5px; flex-wrap: wrap; justify-content: flex-end; }
  .rd-pill { font: 600 11px "IBM Plex Mono", "JetBrains Mono", monospace; padding: 3px 8px; border-radius: 999px; white-space: nowrap; }
  .rd-pill.TEST { background: var(--rd-good-bg); color: var(--rd-good); }
  .rd-pill.WATCH { background: var(--rd-warn-bg); color: var(--rd-warn); }
  .rd-pill.LATER { background: var(--rd-soft); color: var(--rd-text-2); border: 1px dashed var(--border); }
  .rd-pill.REJECT { background: var(--rd-soft); color: var(--muted); }
  .rd-pill.season { background: var(--rd-hot-bg); color: var(--rd-hot); }
  .rd-checks { display: flex; gap: 4px; align-items: center; }
  .rd-chk { width: 24px; height: 24px; border-radius: 6px; display: grid; place-items: center;
            font: 600 10.5px "IBM Plex Mono", "JetBrains Mono", monospace; }
  .rd-chk.on { background: var(--rd-good-bg); color: var(--rd-good); }
  .rd-chk.off { background: var(--rd-soft); color: var(--muted); opacity: .75; }
  .rd-nums { margin-left: auto; font: 500 12px "IBM Plex Mono", "JetBrains Mono", monospace; color: var(--rd-text-2);
             font-variant-numeric: tabular-nums; text-align: right; }
  .rd-nums .up { color: var(--rd-good); } .rd-nums .down { color: var(--rd-hot); }
  .rd-chart-label { font: 600 13px "IBM Plex Mono", "JetBrains Mono", monospace; text-transform: uppercase;
                    letter-spacing: .05em; color: var(--rd-text-2); margin-bottom: 4px; }
  .rd-card svg { display: block; width: 100%; height: auto; overflow: visible; cursor: crosshair; touch-action: pan-y; }
  .rd-g { stroke: var(--rd-grid); stroke-width: 1; }
  .rd-t { fill: var(--muted); font-family: "IBM Plex Mono", "JetBrains Mono", monospace; font-size: 17px; }
  .rd-now { fill: none; stroke: var(--k, var(--rd-line)); stroke-width: 3.5; stroke-linejoin: round; stroke-linecap: round; }
  .rd-q { font-family: "IBM Plex Mono", "JetBrains Mono", monospace; color: var(--rd-text-2); }
  .rd-why { font-size: 12px; color: var(--rd-hot); background: var(--rd-hot-bg); border-radius: 6px; padding: 5px 8px; }
  .rd-sparse { color: var(--rd-hot); text-transform: none; letter-spacing: 0; }
  .rd-manual { font-size: 12px; color: var(--rd-warn); background: var(--rd-warn-bg); border-radius: 6px; padding: 5px 8px; }
  .rd-band-now { fill: var(--rd-good-bg); }
  .rd-band-prev { fill: var(--rd-prev); fill-opacity: .28; }
  .rd-year { stroke: var(--rd-prev); stroke-dasharray: 2 2; }
  .rd-hl { stroke: var(--rd-prev); stroke-width: 1; opacity: 0; pointer-events: none; }
  .rd-hd { fill: var(--k, var(--rd-line)); stroke: var(--rd-surface); stroke-width: 2; opacity: 0; pointer-events: none; }
  .rd-nocurve { font-size: 12px; color: var(--muted); background: var(--rd-soft); border-radius: 8px; padding: 14px 12px; }
  .rd-foot { font-size: 11.5px; color: var(--rd-text-2); line-height: 1.45; border-top: 1px solid var(--border); padding-top: 8px; }
  .rd-foot b { color: var(--muted); font-weight: 600; font-family: "IBM Plex Mono", "JetBrains Mono", monospace; font-size: 10px; letter-spacing: .04em; }
  .rd-tip { position: fixed; pointer-events: none; z-index: 30; background: var(--rd-text); color: var(--page);
            font: 11.5px/1.4 "IBM Plex Mono", "JetBrains Mono", monospace; padding: 5px 9px; border-radius: 6px;
            opacity: 0; transform: translate(-50%, -130%); white-space: nowrap; }
  .rd-h2 { font-size: 22px; margin: 40px 0 6px; text-wrap: balance; }
  .rd-gaps { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 10px; margin-top: 14px; }
  .rd-gap { background: var(--rd-surface); border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px;
            display: flex; flex-direction: column; gap: 4px; font-size: 13px; }
  .rd-gap-head { display: flex; justify-content: space-between; gap: 10px; align-items: baseline; }
  .rd-gap-head span { font: 600 11.5px "IBM Plex Mono", "JetBrains Mono", monospace; color: var(--rd-warn); white-space: nowrap; }
  .rd-gap-why { color: var(--rd-text-2); }
  .rd-gap-fix { color: var(--muted); }
  .rd-archive { margin-top: 40px; padding-top: 18px; border-top: 1px dashed var(--border); font-size: 13px; color: var(--muted); }
  @media (max-width: 520px) { .rd-filters { margin-left: 0; } }
</style>
<section class="rd" aria-label="Новый тренд-радар">
__HEADER__
  <div class="rd-bar">
    <div class="rd-legend">
      <span><svg width="22" height="8" aria-hidden="true"><line x1="0" y1="4" x2="22" y2="4" class="rd-now"/></svg>интерес за 2 года</span>
      <span>кривые есть у __NCURVES__ из __NTOTAL__</span>
    </div>
    <div class="rd-filters" role="group" aria-label="Фильтр по решению">
      <button type="button" data-f="ALL" aria-pressed="true">Все</button>
      <button type="button" data-f="TEST" aria-pressed="false">Тестировать</button>
      <button type="button" data-f="WATCH" aria-pressed="false">Наблюдать</button>
      <button type="button" data-f="LATER" aria-pressed="false">Позже</button>
      <button type="button" data-f="REJECT" aria-pressed="false">Отказ</button>
    </div>
  </div>
  <div class="rd-grid" id="rd-grid"></div>
  <div class="rd-tip" id="rd-tip"></div>
</section>
<script id="rd-data" type="application/json">__DATA__</script>
<script>
(() => {
  const ROWS = JSON.parse(document.getElementById("rd-data").textContent);
  const grid = document.getElementById("rd-grid"), tip = document.getElementById("rd-tip");
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const MON = ["янв","фев","мар","апр","май","июн","июл","авг","сен","окт","ноя","дек"];
  const DEC = { TEST: "тестировать", WATCH: "наблюдать", LATER: "позже", REJECT: "отказ" };
  const CH = [["check_google","G","Google"],["check_pinterest","P","Pinterest"],["check_youtube","Y","YouTube"],["check_tiktok","T","TikTok"],
              ["check_amazon","A","Amazon"],["check_retailers","R","Бренды"]];
  const W = 1100, H = 340, L = 52, R = 12, T = 14, B = 36, pw = W - L - R, ph = H - T - B;
  const x = (i, n) => L + (i / (n - 1)) * pw, y = (v) => T + (1 - v / 100) * ph;
  const fmtDate = (s) => { const [yy, mm, dd] = s.split("-"); return `${+dd} ${MON[+mm - 1]} ${yy}`; };
  const signed = (v) => v === null || v === undefined ? "—" : `${v > 0 ? "+" : ""}${Math.round(v)}%`;
  const cls = (v) => v > 0 ? "up" : v < 0 ? "down" : "";

  function path(vals) {
    let d = "", on = false;
    vals.forEach((v, i) => {
      if (v === null || v === undefined) { on = false; return; }
      d += (on ? "L" : "M") + x(i, vals.length).toFixed(1) + "," + y(v).toFixed(1) + " "; on = true;
    });
    return d.trim();
  }
  function band(i0, i1, n, cls) {
    const a = x(Math.max(0, i0), n), b = x(Math.min(n - 1, i1), n);
    return `<rect class="${cls}" x="${a.toFixed(1)}" y="${T}" width="${(b - a).toFixed(1)}" height="${ph}"/>`;
  }
  function chart(c, label) {
    if (!c) return "";
    const n = c.dates.length;
    let last = null;
    // a tick per quarter (янв/апр/июл/окт), with the year on January
    const ticks = c.dates.map((d, i) => {
      const m = +d.slice(5, 7);
      if (m === last) return ""; last = m;
      if (i < 2 || i > n - 3 || (m - 1) % 3 !== 0) return "";
      const tx = x(i, n).toFixed(1);
      const lab = m === 1 ? `янв’${d.slice(2, 4)}` : MON[m - 1];
      return `<line class="rd-g${m === 1 ? " rd-year" : ""}" x1="${tx}" x2="${tx}" y1="${T}" y2="${T + ph}"/><text class="rd-t" x="${tx}" y="${H - 9}" text-anchor="middle">${lab}</text>`;
    }).join("");
    // the two windows the radar compares: last 8 weeks and the same 8 weeks a year earlier
    const bands = "";   // user 23.09.2026: no green/grey comparison bands on the charts
    const note = c.sparse ? ' <span class="rd-sparse">· мало поисков — не учитываем</span>' : "";
    return `<div><div class="rd-chart-label">${label}${note}</div>
      <svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${label}: вся кривая за 2 года">
        ${bands}
        <line class="rd-g" x1="${L}" x2="${W - R}" y1="${y(0)}" y2="${y(0)}"/>
        <line class="rd-g" x1="${L}" x2="${W - R}" y1="${y(50)}" y2="${y(50)}"/>
        <line class="rd-g" x1="${L}" x2="${W - R}" y1="${y(100)}" y2="${y(100)}"/>
        <text class="rd-t" x="${L - 10}" y="${y(100) + 6}" text-anchor="end">100</text><text class="rd-t" x="${L - 10}" y="${y(50) + 6}" text-anchor="end">50</text><text class="rd-t" x="${L - 10}" y="${y(0) + 6}" text-anchor="end">0</text>
        ${ticks}
        <path class="rd-now" d="${path(c.vals)}"/>
        <line class="rd-hl" x1="0" x2="0" y1="${T}" y2="${T + ph}"/><circle class="rd-hd" r="8"/>
      </svg></div>`;
  }
  function wire(svg, c) {
    const n = c.dates.length, hl = svg.querySelector(".rd-hl"), hd = svg.querySelector(".rd-hd");
    const hide = () => { hl.style.opacity = 0; hd.style.opacity = 0; tip.style.opacity = 0; };
    svg.addEventListener("pointermove", (e) => {
      const r = svg.getBoundingClientRect();
      const i = Math.max(0, Math.min(n - 1, Math.round((((e.clientX - r.left) / r.width * W) - L) / pw * (n - 1))));
      const v = c.vals[i]; if (v === null || v === undefined) return hide();
      const px = x(i, n);
      hl.setAttribute("x1", px); hl.setAttribute("x2", px); hl.style.opacity = 1;
      hd.setAttribute("cx", px); hd.setAttribute("cy", y(v)); hd.style.opacity = 1;
      const p = i >= 52 ? c.vals[i - 52] : null;
      tip.textContent = `${fmtDate(c.dates[i])} · ${Math.round(v)}` + (p === null || p === undefined ? "" : ` · год назад ${Math.round(p)}`);
      tip.style.left = e.clientX + "px"; tip.style.top = e.clientY + "px"; tip.style.opacity = 1;
    });
    svg.addEventListener("pointerleave", hide);
  }

  function render(f) {
    grid.innerHTML = "";
    ROWS.filter((r) => f === "ALL" || r.decision === f).forEach((r) => {
      const card = document.createElement("article");
      card.className = "rd-card" + (r.decision === "TEST" ? " is-test" : "");
      card.style.setProperty("--k", `var(--c${r.color_slot || 1})`);
      const chips = CH.map(([k, s, nm]) => `<span class="rd-chk ${r[k] ? "on" : "off"}" title="${nm}: ${r[k] ? "подтверждает" : "не видит"}">${s}</span>`).join("");
      const pinNums = r.pin_yoy_pct === null && r.pin_mom_pct === null ? "нет на Pinterest"
        : `месяц <span class="${cls(r.pin_mom_pct)}">${signed(r.pin_mom_pct)}</span> · к году <span class="${cls(r.pin_yoy_pct)}" title="среднее за 8 недель против тех же недель прошлого года">${signed(r.pin_yoy_pct)}</span>`;
      const curves = chart(r.pin_curve, "Pinterest · интерес 0–100" + (r.pin_alias ? ` · по фразе «${esc(r.pin_alias)}»` : ""))
        + chart(r.google_curve, "Google · интерес 0–100")
        + chart(r.shop_curve, "Google Shopping · покупательский интерес 0–100")
        + chart(r.youtube_curve, "YouTube · поиск 0–100");
      const foot = [];
      if (r.amazon_items) foot.push(`<b>AMAZON</b> ${r.amazon_items} шт, медиана $${Number(r.amazon_median_price).toFixed(2)}`);
      if (r.amazon_monthly_searches) foot.push(`<b>ПОИСК AMAZON</b> ${Math.round(r.amazon_monthly_searches / 1000)} тыс./мес, `
        + `${r.amazon_mcp_lift_pct > 0 ? "+" : ""}${Math.round(r.amazon_mcp_lift_pct)}% к прошлому месяцу`);
      if (r.amazon_bought_sum) foot.push(`<b>КУПИЛИ НА AMAZON</b> за месяц ≥ ${Number(r.amazon_bought_sum).toLocaleString("ru-RU")} шт. `
        + `(у ${r.amazon_bought_items} товаров с первой страницы поиска есть пометка «bought in past month»)`);
      if (r.google_shop_yoy_pct !== null && r.google_shop_yoy_pct !== undefined)
        foot.push(`<b>GOOGLE SHOPPING</b> 8 недель к прошлому году: ${r.google_shop_yoy_pct > 0 ? "+" : ""}${Math.round(r.google_shop_yoy_pct)}%`);
      if (r.retailer_brands) foot.push(`<b>БРЕНДЫ</b> ${esc(r.retailer_list)}`);
      if (r.google_rising_top) foot.push(`<b>GOOGLE</b> ${esc(String(r.google_rising_top).split(" | ")[0])}`);
      if (r.tiktok_hashtags) foot.push(`<b>TIKTOK</b> ${esc(r.tiktok_hashtags)}`);
      if (r.ac_modifiers) {
        const words = String(r.ac_modifiers).split(" | ").slice(0, 8).map((m) => m.split(" (")[0]);
        foot.push(`<b>ДОПИСЫВАЮТ В ПОИСКЕ</b> ${esc(words.join(", "))}`
          + (r.ac_colors ? `; цвета: ${esc(r.ac_colors)}` : ""));
      }
      if (r.yt_views_90d !== null && r.yt_views_90d !== undefined) {
        const vy = r.yt_views_yoy_pct;
        foot.push(`<b>YOUTUBE</b> видео за 90 дн: ${(r.yt_views_90d / 1e6).toFixed(1)} млн просмотров`
          + (vy === null || vy === undefined ? "" : ` (${vy > 0 ? "+" : ""}${Math.round(vy)}% к тем же дням год назад)`)
          + `; «где купить / хочу» — ${r.yt_intent_comments} из ${r.yt_comments_read} комментариев`
          + (r.yt_intent_examples ? `<br><span style="color:var(--muted)">«${esc(String(r.yt_intent_examples).split(" | ").slice(0, 2).join("», «"))}»</span>` : ""));
      }
      card.innerHTML = `
        <div class="rd-head">
          <div><div class="rd-name"><span class="rd-sw" aria-hidden="true"></span>${esc(r.candidate)}</div><div class="rd-sub">${r.checks_passed} из ${CH.length} каналов подтверждают${r.season_months ? ` · сезон: ${esc(r.season_months)}${r.season_source === "вручную" ? " (задан вручную)" : ""}` : ""}</div></div>
          <div class="rd-pills"><span class="rd-pill ${r.decision}">${DEC[r.decision]}</span>${r.short_season ? '<span class="rd-pill season">короткий сезон</span>' : r.seasonal_flag ? '<span class="rd-pill season">сезон</span>' : ""}</div>
        </div>
        <div class="rd-checks">${chips}<span class="rd-nums">${pinNums}</span></div>
        ${r.pin_quarters ? `<div class="rd-sub">Pinterest по кварталам к прошлому году: <span class="rd-q">${esc(r.pin_quarters)}</span></div>` : ""}
        ${r.reject_reason ? `<div class="rd-why">Почему отказ: ${esc(r.reject_reason)}</div>` : ""}
        ${r.later_reason ? `<div class="rd-manual">Позже: ${esc(r.later_reason)}</div>` : ""}
        ${r.watch_reason && r.decision === "WATCH" ? `<div class="rd-sub">Почему наблюдать: ${esc(r.watch_reason)}</div>` : ""}
        ${r.manual_reason ? `<div class="rd-manual">Ручное решение: ${esc(r.manual_reason)} · автоматически было бы «${DEC[r.auto_decision] || r.auto_decision}»</div>` : ""}
        ${curves ? `<div class="rd-charts">${curves}</div>` : '<div class="rd-nocurve">Кривой нет: ни Pinterest, ни Google, ни YouTube не дали 2-летней истории по этому запросу.</div>'}
        ${foot.length ? `<div class="rd-foot">${foot.join("<br>")}</div>` : ""}`;
      grid.appendChild(card);
      const svgs = card.querySelectorAll("svg[role=img]");
      [r.pin_curve, r.google_curve, r.shop_curve, r.youtube_curve].filter(Boolean).forEach((c, i) => wire(svgs[i], c));
    });
    if (!grid.children.length) grid.innerHTML = '<p class="rd-lead">Нет кандидатов в этой группе.</p>';
  }
  render("ALL");
  document.querySelectorAll(".rd-filters button").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll(".rd-filters button").forEach((o) => o.setAttribute("aria-pressed", String(o === b)));
    render(b.dataset.f);
  }));
})();
</script>
__ARCHIVE__<!-- RADAR:END -->
"""
