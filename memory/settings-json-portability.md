---
name: settings-json-portability
description: settings.json must stay machine-portable — $HOME (not /Users/jazahn) in hook commands, env values as strings
metadata:
  type: project
---

`settings.json` is a direct git checkout shared across Mac + Cloud9 (commit
c91d4a8, from Cloud9).

**Why:** hardcoded `/Users/jazahn/...` paths in hook commands silently break
hooks on non-Mac machines; unquoted numeric env values don't match Claude
Code's expected string type.

**How to apply:** when editing hook commands, use `"$HOME/.claude/..."`
(expands inside the double-quoted node arg on every platform); quote
`CLAUDE_CODE_*` env values as strings (`"1"`, not `1`). Related:
[[credentials-store-pattern]].
