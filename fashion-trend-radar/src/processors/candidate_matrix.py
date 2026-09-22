"""
Cross-channel candidate matrix: one row per trend candidate, one column per
independent "witness" (Google, Pinterest, TikTok, Amazon, retailers), plus a
checks-passed count and a decision. Implements the TZ rule "min 4 of 6
checks" on 6 automated checks: Google, Pinterest, YouTube search, TikTok,
Amazon, retailers (content potential stays manual).

Matching a candidate phrase to items (Amazon titles, retailer names,
TikTok hashtags, Google rising queries) uses the fashion taxonomy:
  - if the candidate has a category (skirt/top/...), the item must share it;
  - AND share at least one non-category attribute (pattern/material/
    neckline/silhouette/detail/audience), or -- when the candidate has no
    such attribute (e.g. "hoco dress") -- contain its remaining words.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd

from src.processors.fashion_taxonomy import extract_fashion_features, normalize_text

STOP = {"women", "womens", "woman", "for", "the", "a", "and", "with", "outfit", "outfits", "inspo",
        # season words are SEO filler in marketplace titles ("Fall Outfits 2026"), not attributes
        "fall", "autumn", "winter", "spring", "summer", "2025", "2026", "2027"}


@dataclass
class CandidateSpec:
    phrase: str
    categories: set
    attrs: set          # {(group, label)} excluding category
    words: set          # leftover significant words


def spec_for(phrase: str) -> CandidateSpec:
    f = extract_fashion_features(phrase)
    cats = set(f.get("category", []))
    attrs = {(g, l) for g, ls in f.items() if g != "category" for l in ls}
    cat_words = {"skirt", "dress", "top", "sweater", "cardigan", "jacket", "coat",
                 "jeans", "pants", "shirt", "blouse", "set", "trousers"}
    words = set(normalize_text(phrase).split()) - STOP - cat_words
    return CandidateSpec(phrase, cats, attrs, words)


def matches(spec: CandidateSpec, text: str) -> bool:
    t = normalize_text(text)
    f = extract_fashion_features(t)
    if spec.categories and not (spec.categories & set(f.get("category", []))):
        return False
    if spec.attrs:
        item_attrs = {(g, l) for g, ls in f.items() if g != "category" for l in ls}
        return bool(spec.attrs & item_attrs)
    if spec.words:
        return all(re.search(rf"\b{re.escape(w)}", t) for w in spec.words)
    # No attributes and no leftover words: only meaningful for a two-category
    # item like "sweater dress" (knitwear + dress) -- require ALL categories.
    if len(spec.categories) >= 2:
        return spec.categories <= set(f.get("category", []))
    return False  # too generic ("cardigan" alone) to count as evidence


def hashtag_matches(spec: CandidateSpec, hashtag: str) -> bool:
    """Hashtags have no spaces (#falloutfitinspo) -- match on raw substrings."""
    h = (hashtag or "").lower()
    keys = {w for w in spec.words if len(w) >= 3}
    for g, l in spec.attrs:
        keys.add(l.replace("_", ""))
    return bool(keys) and any(k in h for k in keys)


WINDOW = 8          # weeks compared against the same weeks a year earlier
SEASON_LIFT = 20    # % rise last year in these weeks that marks a recurring season
MIN_YOY = 15        # % growth vs the same weeks last year for the Google, Pinterest and YouTube checks
MIN_NONZERO = 0.5   # share of weeks with data; below this the series is too sparse to judge


def window_stats(values: list, w: int = WINDOW) -> dict | None:
    """Two-year comparison on weekly values (oldest first):
      yoy_pct   -- mean of the last w weeks vs the same w weeks a year earlier
      lift_now  -- last w weeks vs the w weeks before them (this year's rise)
      lift_prev -- the same, one year earlier (did these weeks rise last year too?)
    Averaging w weeks keeps a single spiky week from deciding the check."""
    v = [float(x) for x in values if x is not None and pd.notna(x)]
    if len(v) < 52 + 2 * w:
        return None
    # Low-volume phrases come back as mostly zeros (0 -> 12 reads as +1000%): not evidence
    if sum(1 for x in v if x > 0) / len(v) < MIN_NONZERO:
        return None
    mean = lambda xs: sum(xs) / len(xs)
    now, now_before = mean(v[-w:]), mean(v[-2 * w:-w])
    prev, prev_before = mean(v[-52 - w:-52]), mean(v[-52 - 2 * w:-52 - w])
    pct = lambda a, b: round((a - b) / b * 100, 1) if b else None
    return {"yoy_pct": pct(now, prev), "lift_now": pct(now, now_before), "lift_prev": pct(prev, prev_before)}


def is_seasonal(st: dict | None) -> bool:
    """Same weeks rose last year as well, and this year is not clearly higher -> the season repeating."""
    return bool(st and st["lift_prev"] is not None and st["yoy_pct"] is not None
                and st["lift_prev"] >= SEASON_LIFT and st["yoy_pct"] < MIN_YOY)


def build_matrix(
    candidates: list[str],
    google_rising: pd.DataFrame,      # keyword, value
    google_history: pd.DataFrame,     # date, keyword, interest, is_partial (2y)
    pinterest: pd.DataFrame,          # term, wow_pct, mom_pct, yoy_pct
    tiktok: pd.DataFrame,             # hashtag, posts, views
    amazon: pd.DataFrame,             # list, category, title
    retailers: pd.DataFrame,          # retailer, name
    pinterest_series: dict | None = None,   # term -> weekly values, 2y, oldest first
    youtube_history: pd.DataFrame | None = None,  # same shape as google_history, YouTube search
    youtube_api: pd.DataFrame | None = None,      # run_youtube_api.py output, one row per candidate
) -> pd.DataFrame:
    yt_api = youtube_api.set_index("candidate") if youtube_api is not None and not youtube_api.empty else pd.DataFrame()
    rows = []
    pin = pinterest.set_index("term") if not pinterest.empty else pd.DataFrame()
    pinterest_series = pinterest_series or {}
    for phrase in candidates:
        s = spec_for(phrase)
        r = {"candidate": phrase}

        # Google: rising related query OR growth over the same 8 weeks last year
        g_hits = google_rising[google_rising["keyword"].apply(lambda k: matches(s, k))] if not google_rising.empty else google_rising
        r["google_rising_hits"] = len(g_hits)
        r["google_rising_top"] = " | ".join(f"{k} (+{int(v)}%)" for k, v in zip(g_hits["keyword"].head(2), g_hits["value"].head(2))) if len(g_hits) else ""
        g_st = None
        if not google_history.empty:
            h = google_history[google_history["keyword"] == phrase]
            g_st = window_stats(h[~h["is_partial"].astype(bool)].sort_values("date")["interest"].tolist())
        r["google_yoy_pct"] = g_st["yoy_pct"] if g_st else None
        r["google_season_lift_prev"] = g_st["lift_prev"] if g_st else None
        # +1..3% over 8 weeks is noise, not growth -- same bar as Pinterest
        r["check_google"] = bool(len(g_hits)) or (r["google_yoy_pct"] is not None and r["google_yoy_pct"] >= MIN_YOY)

        # Pinterest: grew vs the same 8 weeks last year (not just the season)
        p_st = window_stats(pinterest_series[phrase]) if phrase in pinterest_series else None
        p = pin.loc[phrase] if phrase in pin.index else {}
        r["pin_mom_pct"] = p.get("mom_pct") if len(p) else None
        r["pin_yoy_1w_pct"] = p.get("yoy_pct") if len(p) else None      # Pinterest's own single-week number
        r["pin_yoy_pct"] = p_st["yoy_pct"] if p_st else None
        r["pin_season_lift_prev"] = p_st["lift_prev"] if p_st else None
        r["check_pinterest"] = r["pin_yoy_pct"] is not None and r["pin_yoy_pct"] >= MIN_YOY

        # YouTube search ("how to wear ..."): same 8-week comparison as Google
        y_st = None
        if youtube_history is not None and not youtube_history.empty:
            h = youtube_history[youtube_history["keyword"] == phrase]
            y_st = window_stats(h[~h["is_partial"].astype(bool)].sort_values("date")["interest"].tolist())
        r["youtube_yoy_pct"] = y_st["yoy_pct"] if y_st else None
        # YouTube API: views of videos from the last 90 days vs the same 90 days a year ago.
        # Last year's videos had a year longer to collect views, so growth here is conservative.
        a = yt_api.loc[phrase] if phrase in yt_api.index else None
        r["yt_views_yoy_pct"] = a["yt_views_yoy_pct"] if a is not None and pd.notna(a["yt_views_yoy_pct"]) else None
        r["yt_views_90d"] = int(a["yt_views_90d"]) if a is not None else None
        r["yt_intent_comments"] = int(a["yt_intent_comments"]) if a is not None else None
        r["yt_comments_read"] = int(a["yt_comments_read"]) if a is not None else None
        r["yt_intent_examples"] = a["yt_intent_examples"] if a is not None and pd.notna(a["yt_intent_examples"]) else ""
        r["check_youtube"] = ((r["youtube_yoy_pct"] is not None and r["youtube_yoy_pct"] >= MIN_YOY)
                              or (r["yt_views_yoy_pct"] is not None and r["yt_views_yoy_pct"] >= MIN_YOY))

        # Season, judged on two years: Pinterest first, Google if Pinterest has no series
        r["seasonal_flag"] = is_seasonal(p_st) if p_st else is_seasonal(g_st)

        # TikTok: fashion hashtag in the 90-day top list
        t_hits = tiktok[tiktok["hashtag"].apply(lambda h: hashtag_matches(s, h))] if not tiktok.empty else tiktok
        r["tiktok_hashtags"] = " ".join("#" + h for h in t_hits["hashtag"].head(3)) if len(t_hits) else ""
        r["check_tiktok"] = bool(len(t_hits))

        # Amazon: >=2 matching items in new releases / best sellers
        a_hits = amazon[amazon["title"].fillna("").apply(lambda t: matches(s, t))] if not amazon.empty else amazon
        r["amazon_items"] = len(a_hits)
        r["amazon_new_releases"] = int((a_hits["list"] == "new_releases").sum()) if len(a_hits) else 0
        r["amazon_median_price"] = round(float(a_hits["price"].median()), 2) if len(a_hits) and a_hits["price"].notna().any() else None
        r["check_amazon"] = len(a_hits) >= 2

        # Retailers: >=2 brands releasing it
        re_hits = retailers[retailers["name"].fillna("").apply(lambda n: matches(s, n))] if not retailers.empty else retailers
        r["retailer_brands"] = int(re_hits["retailer"].nunique()) if len(re_hits) else 0
        r["retailer_list"] = ", ".join(sorted(re_hits["retailer"].unique())) if len(re_hits) else ""
        r["check_retailers"] = r["retailer_brands"] >= 2

        checks = ["check_google", "check_pinterest", "check_youtube", "check_tiktok", "check_amazon", "check_retailers"]
        r["checks_passed"] = int(sum(bool(r[c]) for c in checks))
        if r["checks_passed"] >= 4:
            r["decision"] = "TEST"
        elif r["checks_passed"] == 3:
            r["decision"] = "WATCH"
        else:
            r["decision"] = "REJECT"
        rows.append(r)

    return pd.DataFrame(rows).sort_values(
        ["checks_passed", "pin_yoy_pct"], ascending=[False, False], na_position="last"
    ).reset_index(drop=True)
