#!/usr/bin/env python3
"""Per-project Claude Code cost broken out by week.

Walks ~/.claude/projects/**/*.jsonl (main session transcripts plus subagent
logs), prices each usage row by its model, and buckets the dollar cost into the
ISO week of the row's timestamp. Prints a table with one row per project, one
column per week (label = the Monday of that ISO week, MM-DD), and a final TOTAL
column. Subagent transcripts are folded into their parent project.

Usage:
    python3 weekly_cost_report.py [--projects-dir DIR] [--json] [--weeks N]

Pricing lives in the RATES table below (USD per 1M tokens) and is kept in sync
with the session-token-report skill. Update it when Anthropic changes prices.
"""
import argparse
import datetime as dt
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
DEFAULT_RATE = (5.00, 25.00, 6.25, 0.50)
NON_BILLED = {"<synthetic>", ""}


def rate_for(model):
    # Model IDs may carry a date suffix (e.g. claude-haiku-4-5-20251001);
    # match on the longest known prefix.
    for known, r in RATES.items():
        if model.startswith(known):
            return r
    return DEFAULT_RATE


def week_key(timestamp):
    """Return (iso_year, iso_week, monday_date) for an ISO-8601 timestamp."""
    # Timestamps look like 2026-06-23T18:31:21.507Z; take the date part.
    date = dt.date.fromisoformat(timestamp[:10])
    iso_year, iso_week, _ = date.isocalendar()
    monday = date - dt.timedelta(days=date.isoweekday() - 1)
    return (iso_year, iso_week), monday


def collect(projects_dir):
    """Return ({project: {week_key: cost}}, {week_key: monday_date})."""
    # project -> week_key -> cost
    data = defaultdict(lambda: defaultdict(float))
    week_dates = {}
    # The same message.id repeats across streaming/retry lines with identical
    # usage; count each id once, scoped per session (see session-token-report).
    seen_ids = defaultdict(set)
    pattern = os.path.join(projects_dir, "*", "**", "*.jsonl")
    for path in glob.glob(pattern, recursive=True):
        rel = os.path.relpath(path, projects_dir)
        parts = rel.split(os.sep)
        project = parts[0]
        # subagent logs live at <project>/<session-id>/subagents/agent-*.jsonl;
        # fold them into the parent session id (the dir name).
        session = parts[1] if "subagents" in parts else os.path.splitext(parts[-1])[0]
        skey = (project, session)
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
                mid = msg.get("id")
                if mid is not None:
                    if mid in seen_ids[skey]:
                        continue
                    seen_ids[skey].add(mid)
                model = msg.get("model", "")
                if model in NON_BILLED:
                    continue
                ts = obj.get("timestamp")
                if not ts:
                    continue
                i = usage.get("input_tokens", 0) or 0
                out = usage.get("output_tokens", 0) or 0
                cc = usage.get("cache_creation_input_tokens", 0) or 0
                cr = usage.get("cache_read_input_tokens", 0) or 0
                ri, ro, rw, rr = rate_for(model)
                cost = (i * ri + out * ro + cc * rw + cr * rr) / 1_000_000
                wk, monday = week_key(ts)
                week_dates[wk] = monday
                data[project][wk] += cost
    return data, week_dates


def short(project):
    """Strip the long encoded-cwd prefix for display."""
    return project.replace("-home-ec2-user-environment-", "") or project


def print_table(data, week_dates, weeks_limit):
    weeks = sorted(week_dates)
    if weeks_limit:
        weeks = weeks[-weeks_limit:]
    labels = [week_dates[wk].strftime("%m-%d") for wk in weeks]

    name_w = max([len("PROJECT")] + [len(short(p)) for p in data]) + 1
    col_w = 9  # e.g. "$1234.56"
    hdr = f"{'PROJECT':<{name_w}}" + "".join(f"{l:>{col_w}}" for l in labels) \
        + f"{'TOTAL':>{col_w}}"
    print(hdr)
    print("-" * len(hdr))

    col_tot = defaultdict(float)
    grand = 0.0
    # rows sorted by project total cost descending
    rows = sorted(data.items(), key=lambda kv: -sum(kv[1].values()))
    for project, wkmap in rows:
        cells = []
        row_tot = 0.0
        for wk in weeks:
            c = wkmap.get(wk, 0.0)
            col_tot[wk] += c
            row_tot += c
            cells.append(("$" + format(c, ".2f")) if c else "-")
        grand += row_tot
        line = f"{short(project):<{name_w}}" \
            + "".join(f"{c:>{col_w}}" for c in cells) \
            + f"{'$' + format(row_tot, '.2f'):>{col_w}}"
        print(line)
    print("-" * len(hdr))
    tot_cells = [("$" + format(col_tot[wk], ".2f")) for wk in weeks]
    print(f"{'TOTAL':<{name_w}}" + "".join(f"{c:>{col_w}}" for c in tot_cells)
          + f"{'$' + format(grand, '.2f'):>{col_w}}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--projects-dir",
                    default=os.path.expanduser("~/.claude/projects"),
                    help="root of Claude Code project transcripts")
    ap.add_argument("--json", action="store_true",
                    help="emit JSON instead of a table")
    ap.add_argument("--weeks", type=int, default=0,
                    help="show only the most recent N weeks (0 = all)")
    args = ap.parse_args()

    data, week_dates = collect(args.projects_dir)

    if args.json:
        weeks = sorted(week_dates)
        if args.weeks:
            weeks = weeks[-args.weeks:]
        out = []
        for project, wkmap in sorted(data.items(),
                                     key=lambda kv: -sum(kv[1].values())):
            row = {
                "project": short(project),
                "weeks": {week_dates[wk].isoformat(): round(wkmap.get(wk, 0.0), 2)
                          for wk in weeks},
                "total_usd": round(sum(wkmap.get(wk, 0.0) for wk in weeks), 2),
            }
            out.append(row)
        print(json.dumps(out, indent=2))
    else:
        print_table(data, week_dates, args.weeks)


if __name__ == "__main__":
    main()
