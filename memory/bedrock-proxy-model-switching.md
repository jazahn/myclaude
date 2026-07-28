---
name: bedrock-proxy-model-switching
description: How to switch models on the Harvard Bedrock proxy; valid Fable/Sonnet/Opus inference-profile IDs and proxy quirks
metadata:
  type: project
---

The `~/.claude` settings route Claude Code through the Harvard Bedrock proxy
(`ANTHROPIC_BEDROCK_BASE_URL` in settings.json, `CLAUDE_CODE_USE_BEDROCK=1`).
Because settings.json is committed and synced across machines, these facts hold
on every machine (see [[project-cross-machine-setup]]).

**Switching models without editing settings.json:** the default is set by
`env.ANTHROPIC_MODEL` (now `us.anthropic.claude-fable-5`). Override per-session
with `/model us.anthropic.claude-sonnet-5`, or per-launch with
`claude --model <id>`. Precedence: `--model` flag → `/model` → env default.

**Valid inference-profile IDs on this proxy (probed 2026-07-23, all HTTP 200):**
- `us.anthropic.claude-fable-5` (default)
- `us.anthropic.claude-sonnet-5`
- `us.anthropic.claude-opus-4-8`

Use the `us.`-prefixed form. There is **no `-0` suffix** —
`us.anthropic.claude-fable-5-0` returns 404. The proxy validates IDs (a bogus
one returns 400 "invalid model identifier"), so a wrong string fails fast.

**Gotchas:**
- The proxy returns **intermittent transient 500s** ("server had an error");
  an identical retry succeeds. Claude Code auto-retries, so this is usually
  invisible, but it is a proxy/Bedrock-side flake, not a config error.
- **Fable 5 returns `thinking` content blocks by default** (extended thinking
  on); Sonnet/Opus returned plain text in the same probe.
- Fable 5 has safety classifiers (cyber/bio) that can refuse; Claude Code then
  falls back to Opus — which is why `ANTHROPIC_DEFAULT_OPUS_MODEL` is pinned to
  `us.anthropic.claude-opus-4-8` in settings.json.

**Why:** wanted Fable as the cheap default while keeping one-command switching to
Sonnet/Opus. **How to apply:** don't edit settings.json to change models day-to-day
— use `/model`. Only edit the env default to change the baseline.
