---
name: weekly-cost-report
description: Per-project Claude Code cost broken out by week, with a total column. Use when the user wants a weekly cost breakdown, asks "how much per project per week", wants to see spend trends over time, or wants a per-project cost-over-weeks table from local transcripts.
tools: Bash
---

# Weekly Cost Report

Builds a table of estimated Claude Code cost with one row per project, one
column per ISO week, and a final TOTAL column. Reads the local JSONL
transcripts under `~/.claude/projects/`. No web research or API calls — pricing
is baked into the bundled script.

For per-session token *counts* (input/output/cache), use the sibling
`session-token-report` skill instead. This skill is cost-over-time only.

## How to run

```bash
python3 ~/.claude/skills/weekly-cost-report/weekly_cost_report.py
```

Week columns are labeled by the Monday of that ISO week (MM-DD). Empty
project/week cells render as `-`. Rows are sorted by project total descending.
Relay the table to the user (reformat as a Markdown table when that reads
better in the client).

Flags:
- `--weeks N` — show only the most recent N weeks (columns); the TOTAL column
  then reflects only those weeks. Use this when the full history is too wide.
- `--json` — emit JSON: each project with a `weeks` map (Monday-date → cost)
  and a `total_usd`.
- `--projects-dir DIR` — point at a different transcripts root (default
  `~/.claude/projects`).

## How it works (so you can explain or adjust it)

- **Sources & dedupe.** Same as `session-token-report`: every `*.jsonl` under
  `~/.claude/projects/**`, subagent logs folded into their parent session, and
  each `message.id` counted once per session to avoid streaming/retry
  double-counting.
- **Per-row cost.** Each usage row is priced by its `message.model` at that
  model's per-token rate. `<synthetic>` and other non-billed rows are skipped.
- **Week bucketing.** Each row's cost lands in the ISO week of its
  `timestamp` field (a line-level ISO-8601 string like
  `2026-06-23T18:31:21.507Z`). Rows with no timestamp are skipped. ISO weeks
  start Monday; the column label is that Monday's date.
- **Aggregation.** Costs are summed per (project, week). The TOTAL column is
  the project's sum across the shown weeks; the TOTAL row sums each week's
  column.

## Pricing (USD per 1M tokens)

Baked into the `RATES` table in `weekly_cost_report.py`, kept in sync with the
`session-token-report` skill. **These are list API prices** — subscription/Max
plans or volume discounts will differ. Cache-write uses the 5-minute-TTL rate
(1.25× input).

| Model | Input | Output | Cache write | Cache read |
|---|--:|--:|--:|--:|
| Opus 4.6 / 4.7 / 4.8 | 5.00 | 25.00 | 6.25 | 0.50 |
| Fable 5 | 10.00 | 50.00 | 12.50 | 1.00 |
| Sonnet 4.6 | 3.00 | 15.00 | 3.75 | 0.30 |
| Haiku 4.5 | 1.00 | 5.00 | 1.25 | 0.10 |

Unrecognized model IDs default to Opus-tier rates. **To update rates:** edit the
`RATES` dict in `weekly_cost_report.py` (and the `session-token-report` copy).

## Notes to surface to the user

- **Costs are bucketed by wall-clock week, not by session.** A single
  long-running session that spans a week boundary has its cost split across the
  two week columns by row timestamp.
- **The live session counts itself**, and the current (partial) week's column
  will keep growing as you work.
- **Forking-resume double-count** (a fork that copies prior messages into a new
  session id) inflates totals; see `session-token-report` SKILL.md.
