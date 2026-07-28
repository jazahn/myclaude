---
name: ntfy-notification-config
description: ntfy hooks source per-machine ~/.claude/.ntfy-config (topic, token, click target); missing file = silent no-op
metadata:
  type: project
---

The ntfy notification hooks in `settings.json` (Stop + Notification events) are
machine-agnostic: each command starts with
`[ -f ~/.claude/.ntfy-config ] || exit 0; . ~/.claude/.ntfy-config` and reads
`NTFY_TOPIC`, `NTFY_TOKEN`, and `NTFY_CLICK` from that sourced file.

**Why:** ntfy topics are reserved (need an access token), topics are
one-per-machine, and the click deep-link (`moshi://`) is Mac-only — so all
three are per-machine values that must stay out of the committed settings.json.

**How to apply:**
- New machine setup: `cp .ntfy-config.example .ntfy-config`, fill in that
  machine's reserved topic + token (empty `NTFY_CLICK` if no terminal
  deep-link), `chmod 600`. No settings.json edits needed.
- No `.ntfy-config` present → hooks exit 0 before any network call
  (intentional "notifications not set up here" no-op).
- `.ntfy-config` is gitignored (whitelist default + explicit entry in the
  secrets section); `.ntfy-config.example` is the committed template.
- Sourcing executes the file as shell — keep it 600; same trust level as
  `.anthropic-key`.
- Token rotation = edit `.ntfy-config` only; hooks read it at send time.
