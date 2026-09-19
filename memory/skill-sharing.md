---
name: skill-sharing
description: How to share a Claude Code skill with others (claude.ai upload, plugins, project dir) and the frontmatter rules that make a SKILL.md portable across surfaces
metadata:
  type: project
---

Verified 2026-09-18 against code.claude.com/docs/en/skills and the
support.claude.com "Provision and manage skills for your organization" article.

**claude.ai skills sync into Claude Code.** At session start Claude Code
downloads the account's claude.ai skills into `~/.claude/skills/synced/<bucket>/`
(manifest.json lists them with a `source` field). This covers skills the user
created/uploaded personally, skills the org provisioned, and Anthropic built-ins.
They surface as `anthropic-skills:<name>`; a local skill with the same short
name wins for `/<name>`.

**Sharing routes**
- *claude.ai upload* (Team/Enterprise): Organization settings → Skills → +Add,
  upload a `.zip` whose root folder contains `SKILL.md`. Only org Owners can
  provision org-wide. Members can upload to their personal skills list and share
  with specific colleagues if the admin toggles ("skill creation", "skill
  sharing") are on. Group-based provisioning needs Enterprise.
- *Project `.claude/skills/<name>/`* committed to a repo: Claude Code only,
  versioned with the code.
- *Plugin + marketplace* (`.claude-plugin/plugin.json`, `marketplace.json` in a
  git repo): for bundles of skills/agents/hooks; can be pre-enabled org-wide via
  managed settings `extraKnownMarketplaces` + `enabledPlugins`. Managed settings
  cannot push raw skills, only plugins.
- *Skills API* (`/v1/skills`): API workloads only, not visible in claude.ai/Code.

**Who sees it in Claude Code, and when.** Org-provisioned (Owner upload): enabled
by default for everyone, syncs with no user action. Shared with specific
colleagues: shows grayed out under "Shared with you" in their claude.ai skills
list and does NOT sync until they toggle it on. Sync runs at session start and
rechecks ~every 10 min, updating a running session without restart. Sync is
skipped for API-key / `apiKeyHelper` / `ANTHROPIC_AUTH_TOKEN` / Bedrock sessions
(so the `claude-bedrock` fallback profile never sees synced skills), bare/safe
mode, and `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`. `CLAUDE_CODE_SYNC_SKILLS=1`
makes non-interactive runs wait for the download. An uploaded skill appears in
manifest.json with `source: "plugin"` plus a `backingPluginId`. A local skill
with the same short name shadows the synced one for `/<name>`.

**Portable frontmatter (hard rule).** claude.ai upload, the Skills API, and
`package_skill.py` accept ONLY `name`, `description`, `license`,
`compatibility`, `metadata`, `allowed-tools`. Anything else (`argument-hint`,
`disable-model-invocation`, `user-invocable`, `context`, `model`) fails the
upload with a hard error rather than being ignored. `name`: kebab-case, ≤64
chars, must not contain "anthropic" or "claude". `description`: ≤1024 chars, no
angle brackets. Exactly one SKILL.md per zip.

**Why:** The first shareable skill (`session-quiz`) originally carried
`argument-hint`, which would have failed upload.

**How to apply:** Before packaging a skill for sharing, strip Claude Code-only
fields and move argument guidance into the description body. Rebuild the zip with
`cd ~/.claude/skills && zip -r ~/Downloads/<name>.zip <name>`.

Related: [[auth-profiles]] (which claude.ai account the sync follows).
