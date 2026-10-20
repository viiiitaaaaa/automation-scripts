#!/usr/bin/env python3
"""cache_gap_check.py - READ-ONLY. Is raising subagentPromptCacheTtl 5m -> 1h likely worth it?

Scans Claude Code transcripts (~/.claude/projects/**/*.jsonl) for subagent (sidechain)
requests, measures idle gaps between each subagent's consecutive requests, and estimates
cache cost under the current 5m TTL vs a hypothetical 1h TTL, in multiples of base input
price. Python 3 stdlib only. Never writes files and makes no network calls.
"""
import argparse, json, os, sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

W5, W1H = 1.25, 2.0          # cache write multipliers (Anthropic prompt-caching docs)
GAP_LO, GAP_HI = 300.0, 3600.0   # 5 min <= gap < 60 min is the window where 1h can help
VERDICT_PCT = 5.0            # >5% estimated saving => "likely worth it"; within +-5% => marginal


def parse_ts(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except Exception:
        return None


def find_files(path):
    if os.path.isfile(path):
        return [path]
    out = []
    for root, _, files in os.walk(path):
        out += [os.path.join(root, f) for f in files if f.endswith(".jsonl")]
    return sorted(out)


def load_requests(files, since):
    """Return {agent_key: [request dicts]} for sidechain/subagent assistant messages with usage."""
    agents = defaultdict(dict)  # key -> {request_id: req}  (dedupes streamed duplicate lines)
    for f in files:
        in_sub_dir = "subagents" in f.replace("\\", "/").split("/")
        try:
            fh = open(f, "r", encoding="utf-8", errors="replace")
        except OSError:
            continue
        with fh:
            for n, line in enumerate(fh):
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                if not isinstance(o, dict):
                    continue
                msg = o.get("message")
                if not isinstance(msg, dict) or not isinstance(msg.get("usage"), dict):
                    continue
                if not (o.get("isSidechain") is True or o.get("agentId") or in_sub_dir):
                    continue  # main-thread request: not a subagent
                ts = parse_ts(o.get("timestamp"))
                if ts is None:
                    continue
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if ts < since:
                    continue
                u = msg["usage"]
                cc = u.get("cache_creation") if isinstance(u.get("cache_creation"), dict) else {}
                create = int(u.get("cache_creation_input_tokens") or 0)
                w1h = int(cc.get("ephemeral_1h_input_tokens") or 0)
                w5 = int(cc.get("ephemeral_5m_input_tokens") or 0)
                if w1h + w5 < create:           # no/partial breakdown: treat remainder as 5m
                    w5 = create - w1h
                req = dict(ts=ts, create=create, read=int(u.get("cache_read_input_tokens") or 0),
                           w5=w5, w1h=w1h)
                key = o.get("agentId") or f
                rid = msg.get("id") or o.get("requestId") or o.get("uuid") or "%s:%d" % (f, n)
                prev = agents[key].get(rid)
                if prev is None or ts < prev["ts"]:
                    keep_ts = ts
                else:
                    keep_ts = prev["ts"]
                req["ts"] = keep_ts        # earliest line of a streamed message; usage from last line
                agents[key][rid] = req
    return {k: sorted(v.values(), key=lambda r: r["ts"]) for k, v in agents.items()}


def analyze(agents, read_mult):
    s = dict(agents=len(agents), requests=0, with_prev=0, lt5m=0, win=0, ge60m=0,
             win_rewritten=0, already_1h_tokens=0, cost_5m=0.0, cost_1h=0.0)
    for reqs in agents.values():
        prev = None
        for r in reqs:
            total = r["create"] + r["read"]            # cached-prefix tokens this request used
            s["requests"] += 1
            s["already_1h_tokens"] += r["w1h"]
            base = W5 * r["w5"] + W1H * r["w1h"] + read_mult * r["read"]
            hyp_read = r["read"]
            gap = None
            if prev is not None:
                gap = (r["ts"] - prev["ts"]).total_seconds()
                s["with_prev"] += 1
                if gap < GAP_LO:
                    s["lt5m"] += 1
                elif gap < GAP_HI:
                    s["win"] += 1
                    s["win_rewritten"] += r["create"]
                    # with 1h, the previous request's cached prefix would still be alive
                    hyp_read = max(r["read"], min(prev["create"] + prev["read"], total))
                else:
                    s["ge60m"] += 1
            hyp_write = total - hyp_read
            hyp = W1H * hyp_write + read_mult * hyp_read
            s["cost_5m"] += base
            s["cost_1h"] += hyp
            prev = r
    return s


def verdict(s):
    if s["requests"] == 0:
        return "no-data", "No subagent requests found in range - nothing to conclude."
    if s["cost_5m"] <= 0:
        return "no-cache", "Subagents show no cache activity - TTL change would not matter."
    d = (s["cost_1h"] - s["cost_5m"]) / s["cost_5m"] * 100.0
    if d < -VERDICT_PCT:
        return "worth-it", "LIKELY WORTH IT: est. %.1f%% lower cache cost with 1h." % -d
    if d > VERDICT_PCT:
        return "not-worth-it", "NOT WORTH IT: est. %.1f%% higher cache cost with 1h." % d
    return "marginal", "MARGINAL (%+.1f%%): within +-%d%%, leave at 5m unless latency matters." % (d, VERDICT_PCT)


def main():
    ap = argparse.ArgumentParser(description="Estimate whether subagentPromptCacheTtl 5m->1h is worth it (read-only).")
    ap.add_argument("--days", type=float, default=14, help="look-back window in days (default 14)")
    ap.add_argument("--path", default=os.path.expanduser("~/.claude/projects"),
                    help="transcript dir or file (default ~/.claude/projects)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--read-mult", type=float, default=0.1,
                    help="cache-read multiplier (default 0.1; docs list 0.05/0.025 for some newer models)")
    a = ap.parse_args()

    since = datetime.now(timezone.utc) - timedelta(days=a.days)
    files = find_files(a.path)
    agents = load_requests(files, since)
    s = analyze(agents, a.read_mult)
    code, text = verdict(s)
    req = s["requests"]
    pct = lambda n: (100.0 * n / req) if req else 0.0
    delta = ((s["cost_1h"] - s["cost_5m"]) / s["cost_5m"] * 100.0) if s["cost_5m"] else 0.0

    if a.json:
        print(json.dumps(dict(path=a.path, days=a.days, files_scanned=len(files), subagents=s["agents"],
            requests=req, requests_with_prev=s["with_prev"], gap_lt_5m=s["lt5m"],
            gap_5m_to_60m=s["win"], gap_5m_to_60m_pct=round(pct(s["win"]), 1), gap_ge_60m=s["ge60m"],
            tokens_rewritten_after_5m_60m_gaps=s["win_rewritten"],
            tokens_already_written_as_1h=s["already_1h_tokens"],
            cost_now_5m_base_units=round(s["cost_5m"], 1), cost_1h_base_units=round(s["cost_1h"], 1),
            est_change_pct=round(delta, 1), verdict=code, verdict_text=text,
            multipliers=dict(write_5m=W5, write_1h=W1H, read=a.read_mult)), indent=2))
        return 0

    print("Subagent cache-gap check | last %g d | %s" % (a.days, a.path))
    print("Scanned %d files -> %d subagents, %d subagent requests" % (len(files), s["agents"], req))
    if req:
        print("Gap 5m-60m (1h could help): %d (%.1f%% of requests) | <5m: %d | >=60m: %d | first-in-agent: %d"
              % (s["win"], pct(s["win"]), s["lt5m"], s["ge60m"], req - s["with_prev"]))
        print("Cache tokens re-written after those gaps: %s" % format(s["win_rewritten"], ","))
        print("Est. cost now (5m)  : %s base-input-token units" % format(round(s["cost_5m"]), ","))
        print("Est. cost with 1h   : %s base-input-token units (%+.1f%%)" % (format(round(s["cost_1h"]), ","), delta))
        if s["already_1h_tokens"]:
            print("Note: %s written tokens were already 1h in the data (priced 2x in 'now')." % format(s["already_1h_tokens"], ","))
    print("Verdict: " + text)
    print("Rule: 1h write=2x vs 5m=1.25x (+0.75x every write); each avoided expired re-write saves 1.25-%.2g=%.3gx." % (a.read_mult, W5 - a.read_mult))
    return 0


if __name__ == "__main__":
    sys.exit(main())
