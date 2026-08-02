---
name: auth-profiles
description: Subscription-primary auth with Bedrock-proxy fallback via `claude-bedrock` alias + profiles/bedrock-proxy.json; apiKeyHelper/org-pin gotchas; Cloud9 headless login
metadata:
  type: project
---

Claude Code auth (since 2026-08-02): the **org Claude subscription is primary**
(plain `claude`, `/login` with jcleveng@fas.harvard.edu), and the **Harvard
Bedrock proxy is the fallback**, kept in `~/.claude/profiles/bedrock-proxy.json`
and activated with `claude-bedrock` (alias for
`claude --settings ~/.claude/profiles/bedrock-proxy.json`). The `--settings`
flag merges over the base settings for that session only. The profile holds the
whole proxy setup: `apiKeyHelper`, `ANTHROPIC_BEDROCK_BASE_URL`,
`CLAUDE_CODE_USE_BEDROCK/SKIP_BEDROCK_AUTH`, and the `us.anthropic.*` model pins
(see [[bedrock-proxy-model-switching]]). No secrets in the profile — the key
stays in gitignored `.anthropic-key` per [[credentials-store-pattern]];
`profiles/` is whitelisted in .gitignore so it syncs.

**Why:** subscription for normal use; proxy survives as a one-command backup
against unstated subscription limits.

**How to apply / gotchas:**
- `apiKeyHelper` or auth env vars anywhere in base settings.json silently
  override subscription login — auth-precedence order is Bedrock env >
  AUTH_TOKEN > API_KEY > apiKeyHelper > OAuth. Keep them ONLY in the profile.
  Verify active auth with `/status` (subscription shows a `Login:` row).
- `forceLoginOrgUUID` in settings.json (`2d2a3730-1239-4ee7-a034-51714e9e5e3d`)
  pins `/login` to the Harvard org. If logins ever bounce in a loop, this line
  is the suspect — delete it, re-verify the UUID.
- Editing auth keys in settings.json **hot-reloads into running sessions** and
  forces re-login churn; do such edits between sessions.
- **Cloud9 (headless) login works without a local browser:** `claude` prints
  the OAuth URL — open it on the laptop, paste the code back. For no-paste
  automation, `claude setup-token` on the Mac mints a 1-year token for
  `CLAUDE_CODE_OAUTH_TOKEN` (model requests only; no Remote Control/claude.ai
  MCP; secret → `.credentials.env`). Don't copy `.credentials.json` between
  machines.
- **Unfinished (Cloud9):** the alias lives in the Mac-local `~/.zshrc` (not in
  the repo); on Cloud9 add it to `~/.bashrc` by hand, and do the first `/login`
  there. See [[project-cross-machine-setup]].
