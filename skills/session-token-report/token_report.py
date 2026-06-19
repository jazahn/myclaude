#!/usr/bin/env python3
"""Tally Claude Code session token usage and estimate cost.

Walks ~/.claude/projects/**/*.jsonl (main session transcripts plus subagent
logs), sums the four token types per session, and applies per-model list
pricing. Subagent transcripts are folded into their parent session's totals.

Usage:
    python3 token_report.py [--projects-dir DIR] [--json] [--by-project]

Pricing lives in the RATES table below — update it when Anthropic changes
prices (see SKILL.md for the source). Rates are USD per 1M tokens.
"""
import argparse
import glob
import json
import os
from collections import defaultdict

# USD per 1M tokens: (input, output, cache_write_5m, cache_read)
# cache_write is the 5-minute-TTL rate (1.25x input). 1h-TTL writes cost 2x
# input; transcripts don't reliably distinguish, so heavy 1h use under-counts.
RATES = {
    "claude-opus-4-8":   (5.00, 25.00, 6.25, 0.50),
    "claude-opus-4-7":   (5.00, 25.00, 6.25, 0.50),
    "claude-opus-4-6":   (5.00, 25.00, 6.25, 0.50),
    "claude-fable-5":    (10.00, 50.00, 12.50, 1.00),
    "claude-sonnet-4-6": (3.00, 15.00, 3.75, 0.30),
    "claude-haiku-4-5":  (1.00, 5.00, 1.25, 0.10),
}
# Default rate for unrecognized model strings (assume Opus-tier so cost is not
# understated). "<synthetic>" and other non-billed rows are skipped entirely.
DEFAULT_RATE = (5.00, 25.00, 6.25, 0.50)
NON_BILLED = {"<synthetic>", ""}


def rate_for(model):
    # Model IDs may carry a date suffix (e.g. claude-haiku-4-5-20251001);
    # match on the longest known prefix.
    for known, r in RATES.items():
        if model.startswith(known):
            return r
    return DEFAULT_RATE


def collect(projects_dir):
    """Return {(project, session): {tok totals, cost, models}}."""
    data = defaultdict(lambda: {
        "in": 0, "out": 0, "cc": 0, "cr": 0, "cost": 0.0, "models": set(),
    })
    # The same message.id repeats across streaming/retry lines with identical
    # usage; count each id once. Scoped per session so a forking resume (which
    # copies prior messages into a new session file) doesn't suppress them —
    # those are double-counted across sessions either way; see SKILL.md.
    seen_ids = defaultdict(set)
    pattern = os.path.join(projects_dir, "*", "**", "*.jsonl")
    for path in glob.glob(pattern, recursive=True):
        rel = os.path.relpath(path, projects_dir)
        parts = rel.split(os.sep)
        project = parts[0]
        # subagent logs live at <project>/<session-id>/subagents/agent-*.jsonl;
        # fold them into the parent session id (the dir name).
        session = parts[1] if "subagents" in parts else os.path.splitext(parts[-1])[0]
        key = (project, session)
        d = data[key]
        with open(path, errors="replace") as fh:
            for line in fh:
                try:
                    obj = json.loads(line)
                except (ValueError, json.JSONDecodeError):
                    continue
                msg = obj.get("message")
                if not isinstance(msg, dict):
                    continue
                usage = msg.get("usage")
                if not isinstance(usage, dict):
                    continue
                # Dedupe repeated usage rows by message id (within the session).
                mid = msg.get("id")
                if mid is not None:
                    if mid in seen_ids[key]:
                        continue
                    seen_ids[key].add(mid)
                model = msg.get("model", "")
                i = usage.get("input_tokens", 0) or 0
                out = usage.get("output_tokens", 0) or 0
                cc = usage.get("cache_creation_input_tokens", 0) or 0
                cr = usage.get("cache_read_input_tokens", 0) or 0
                d["in"] += i
                d["out"] += out
                d["cc"] += cc
                d["cr"] += cr
                if model in NON_BILLED:
                    continue
                d["models"].add(model)
                ri, ro, rw, rr = rate_for(model)
                d["cost"] += (i * ri + out * ro + cc * rw + cr * rr) / 1_000_000
    return data


def short(project):
    """Strip the long encoded-cwd prefix for display."""
    return project.replace("-home-ec2-user-environment-", "") or project


def aggregate_by_project(data):
    agg = defaultdict(lambda: {
        "in": 0, "out": 0, "cc": 0, "cr": 0, "cost": 0.0, "models": set(),
    })
    for (project, _sess), d in data.items():
        a = agg[project]
        for f in ("in", "out", "cc", "cr"):
            a[f] += d[f]
        a["cost"] += d["cost"]
        a["models"] |= d["models"]
    return {(p, ""): d for p, d in agg.items()}


def print_table(data, by_project):
    label = "PROJECT" if by_project else "SESSION"
    hdr = (f"{'PROJECT':<22}" if not by_project else "") + \
          f"{label:<14}{'INPUT':>11}{'OUTPUT':>11}{'CACHE_W':>12}" \
          f"{'CACHE_R':>13}{'TOTAL':>13}{'COST':>10}"
    print(hdr)
    print("-" * len(hdr))
    tot = {"in": 0, "out": 0, "cc": 0, "cr": 0, "t": 0, "cost": 0.0}
    rows = sorted(data.items(), key=lambda kv: -kv[1]["cost"])
    for (project, session), d in rows:
        t = d["in"] + d["out"] + d["cc"] + d["cr"]
        for k, f in (("in", "in"), ("out", "out"), ("cc", "cc"), ("cr", "cr")):
            tot[k] += d[f]
        tot["t"] += t
        tot["cost"] += d["cost"]
        prefix = "" if by_project else f"{short(project):<22}"
        name = short(project) if by_project else session[:12]
        print(f"{prefix}{name:<14}{d['in']:>11,}{d['out']:>11,}"
              f"{d['cc']:>12,}{d['cr']:>13,}{t:>13,}{'$' + format(d['cost'], '.2f'):>10}")
    print("-" * len(hdr))
    pad = 14 if by_project else 36
    print(f"{'TOTAL':<{pad}}{tot['in']:>11,}{tot['out']:>11,}{tot['cc']:>12,}"
          f"{tot['cr']:>13,}{tot['t']:>13,}{'$' + format(tot['cost'], '.2f'):>10}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--projects-dir",
                    default=os.path.expanduser("~/.claude/projects"),
                    help="root of Claude Code project transcripts")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of a table")
    ap.add_argument("--by-project", action="store_true",
                    help="aggregate per project instead of per session")
    args = ap.parse_args()

    data = collect(args.projects_dir)
    if args.by_project:
        data = aggregate_by_project(data)

    if args.json:
        out = []
        for (project, session), d in sorted(data.items(), key=lambda kv: -kv[1]["cost"]):
            t = d["in"] + d["out"] + d["cc"] + d["cr"]
            out.append({
                "project": short(project), "session": session,
                "input": d["in"], "output": d["out"],
                "cache_write": d["cc"], "cache_read": d["cr"],
                "total": t, "cost_usd": round(d["cost"], 2),
                "models": sorted(d["models"]),
            })
        print(json.dumps(out, indent=2))
    else:
        print_table(data, args.by_project)


if __name__ == "__main__":
    main()
