# Committed memory index

Portable, project-scoped facts for the `~/.claude` settings repo. Synced across
machines via git (unlike `projects/*/memory/`, which is machine-local). Imported
into context by `CLAUDE.md` via `@memory/INDEX.md`.

- [Auth profiles](auth-profiles.md) — subscription primary, Bedrock proxy fallback via `claude-bedrock` alias + `profiles/bedrock-proxy.json`; apiKeyHelper silent-override + forceLoginOrgUUID gotchas; Cloud9 headless login; Cloud9 setup unfinished
- [Bedrock proxy model switching](bedrock-proxy-model-switching.md) — how to switch models on the Harvard proxy (now the `claude-bedrock` fallback profile); valid Fable/Sonnet/Opus IDs (no `-0` suffix); transient 500s; Opus fallback pin
- [ntfy notification config](ntfy-notification-config.md) — hooks source per-machine `.ntfy-config` (topic/token/click); missing file = silent no-op; new-machine setup via `.ntfy-config.example`
- [Credentials store pattern](credentials-store-pattern.md) — secrets in gitignored `.credentials.env` (chmod 600), names/usage in committed `credentials.md`, inject-by-reference only, Read-deny rule enforces
- [settings.json portability](settings-json-portability.md) — use `$HOME` not `/Users/jazahn` in hook commands; env values as strings
- [HUIT GitHub Enterprise API](huit-github-enterprise-api.md) — `gh` OAuth login works on github.huit.harvard.edu (Bearer 401 was classic-PAT only; both stored PATs dead 2026-09-19). Org is `HUIT`; 404-on-write means missing `repo` scope; some repos are live there while github.com is a stale mirror
- [Skill sharing](skill-sharing.md) — claude.ai skills sync into `skills/synced/`; org upload = zip with SKILL.md (Owners only); portable frontmatter is ONLY name/description/license/compatibility/metadata/allowed-tools, anything else hard-fails upload
- [Skills organization](skills-organization.md) — personal skills live in `skills/<name>/SKILL.md`; shareable ones live in the `harvard-huit/huit-agent-plugins` marketplace and arrive via claude.ai account-level plugin sync (`quiz:session` replaced the local `session-quiz` on 2026-09-26); sync is off under the Bedrock profile; CLAUDE.md keeps only always-on behaviors
- [Jira ADF task lists](jira-adf-task-lists.md) — editing descriptions via MCP markdown breaks checkboxes into literal `[x]`; use ADF taskList/taskItem nodes
