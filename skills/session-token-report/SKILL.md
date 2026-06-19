---
name: session-token-report
description: Tally Claude Code session token usage (input/output/cache-write/cache-read) and estimate cost from local transcripts. Use when the user asks how many tokens their sessions used, wants a per-session or per-project token/cost breakdown, asks "how much have I spent", or wants a readout of session usage on this machine.
tools: Bash
---

# Session Token Report

Builds a table of token usage and estimated cost across all Claude Code
sessions stored on this machine, reading the local JSONL transcripts under
`~/.claude/projects/`. No web research or API calls needed — pricing is baked
into the bundled script.

## How to run

Run the bundled script with Bash:

```bash
python3 ~/.claude/skills/session-token-report/token_report.py
```

It prints a per-session table with columns: **INPUT, OUTPUT, CACHE_W
(cache write), CACHE_R (cache read), TOTAL, COST**, sorted by cost descending,
with a TOTAL row. Then relay the table to the user (reformat as a Markdown
table when that reads better in the client).

Flags:
- `--by-project` — aggregate per project instead of per session.
- `--json` — emit JSON (per-row token columns, `cost_usd`, and the `models`
  detected) for further processing.
- `--projects-dir DIR` — point at a different transcripts root (default
  `~/.claude/projects`).

## How it works (so you can explain or adjust it)

- **Sources.** Every `*.jsonl` under `~/.claude/projects/**`. Each project dir
  name is the encoded working directory; each top-level `.jsonl` is one
  session. Subagent logs live at `<project>/<session-id>/subagents/agent-*.jsonl`
  and are **folded into their parent session's totals**.
- **Token types.** Each assistant message carries a `message.usage` object with
  `input_tokens`, `output_tokens`, `cache_creation_input_tokens` (cache write),
  and `cache_read_input_tokens` (cache read). The script sums all four per
  session. TOTAL is their sum.
- **Dedupe by `message.id`.** The same usage row repeats across streaming/retry
  lines with identical values — naive summation roughly doubles the totals. The
  script counts each `message.id` once per session. (Rows with no id are counted
  individually.) This dedupe is essential; without it both tokens and cost are
  heavily inflated.
- **Cost.** Each usage row is priced by its `message.model` at that model's
  per-token rate, then summed. Rows with model `<synthetic>` (harness-generated,
  not real API calls) are counted in tokens but **not billed**.

## Pricing (USD per 1M tokens)

Baked into the `RATES` table in `token_report.py`. **These are list API prices**
— subscription/Max plans or volume discounts will differ. Cache-write uses the
5-minute-TTL rate (1.25× input); 1-hour-TTL writes cost 2× input, which the
transcripts don't reliably distinguish.

| Model | Input | Output | Cache write | Cache read |
|---|--:|--:|--:|--:|
| Opus 4.6 / 4.7 / 4.8 | $5.00 | $25.00 | $6.25 | $0.50 |
| Fable 5 | $10.00 | $50.00 | $12.50 | $1.00 |
| Sonnet 4.6 | $3.00 | $15.00 | $3.75 | $0.30 |
| Haiku 4.5 | $1.00 | $5.00 | $1.25 | $0.10 |

Unrecognized model IDs default to Opus-tier rates (so cost is not understated).
Model IDs match by prefix, so dated suffixes (e.g. `claude-haiku-4-5-20251001`)
resolve correctly.

**To update rates:** edit the `RATES` dict in `token_report.py`. Current source
of truth for pricing is the `claude-api` skill (`shared/models.md` pricing
table) or https://platform.claude.com/docs/en/pricing.

## Notes to surface to the user

- **Cache reads dominate volume but not cost** (priced at ~0.1× input), so the
  dollar total is far below what raw token counts suggest.
- **The live session counts itself.** Transcripts are written in real time, so
  the currently-active session appears and grows as you work.
- **Forking-resume double-count (known limitation, not handled).** A forking
  resume creates a new session file with a new id but copies the prior messages
  in. Dedupe is scoped per session, so those copied rows are counted in *both*
  sessions. Plain `--continue`/`--resume` appends to the same file (safe); only
  a fork that spawns a new id can double-count. If totals look too high for a
  project with resumed sessions, this is the likely cause.
