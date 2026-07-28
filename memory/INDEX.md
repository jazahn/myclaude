# Committed memory index

Portable, project-scoped facts for the `~/.claude` settings repo. Synced across
machines via git (unlike `projects/*/memory/`, which is machine-local). Imported
into context by `CLAUDE.md` via `@memory/INDEX.md`.

- [Bedrock proxy model switching](bedrock-proxy-model-switching.md) — how to switch models on the Harvard proxy; valid Fable/Sonnet/Opus IDs (no `-0` suffix); transient 500s; Opus fallback pin
- [ntfy notification config](ntfy-notification-config.md) — hooks source per-machine `.ntfy-config` (topic/token/click); missing file = silent no-op; new-machine setup via `.ntfy-config.example`
