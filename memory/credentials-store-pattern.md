---
name: credentials-store-pattern
description: Shared-credentials pattern — secret values in gitignored .credentials.env, names/usage in committed credentials.md, Read-deny rule in settings.json
metadata:
  type: project
---

Common cross-project credentials (Splunk, GitHub PATs) live in
`~/.claude/.credentials.env` (machine-local, gitignored, chmod 600). What
exists and how to use it is documented in committed `credentials.md`, imported
by `CLAUDE.md` so every session sees the key names but never the values.

**Why:** values in context get sent upstream every turn and persist in
plaintext transcripts under `projects/*.jsonl`; names-only in context avoids
both while still letting sessions use the credentials.

**How to apply:**
- Never read/echo credential values into a conversation — settings.json has a
  `permissions.deny` rule blocking `Read` on `.credentials.env` to enforce this.
- Inject by reference in the consuming shell command:
  `VAR=$(grep '^VAR=' ~/.claude/.credentials.env | cut -d= -f2-) <command>`.
- New machine: `cp .credentials.env.example .credentials.env && chmod 600` and
  fill in that machine's values.
- Non-secret config (e.g. `SPLUNK_API_URL`) belongs in `credentials.md`
  itself, not the env file.
