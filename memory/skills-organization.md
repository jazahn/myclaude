---
name: skills-organization
description: Where personal skills live in this repo vs shareable ones in the HUIT plugin marketplace; how claude.ai account-level plugin sync delivers them; the 2026-09-26 session-quiz → quiz:session migration; sync-off gotcha under the Bedrock profile
metadata:
  type: project
---

**Layout.** Personal, user-scoped skills are `~/.claude/skills/<name>/SKILL.md`,
committed and synced across machines by this repo (`.gitignore` whitelists
`/skills/`). `skills/synced/` and `skills/.trash/` are the claude.ai skill-sync
cache and its removal trash, both gitignored — see [[skill-sharing]]. Synced
*plugins* land in `plugins/synced/<account-id>/<plugin>/` (also gitignored).

**Decision (2026-09-17/19, revised 2026-09-26): spin-down is personal, the
quiz is shareable and lives in a plugin.** `spin-down` stays here because it
hardcodes the AAIS Jira cloudId, HUIT GitHub hosts, and `credentials.md`. The
generic quiz moved out of this repo entirely: the local `skills/session-quiz`
was deleted on 2026-09-26 and replaced by the `quiz` plugin
(`/quiz:session`, `/quiz:project`) in the `harvard-huit/ats-plugin-marketplace`
marketplace on github.com. `spin-down` phase 3 and global `CLAUDE.md` both
invoke `quiz:session`, with an inline text fallback if it is absent.

**How the plugin reaches this machine.** Not by `claude plugin install`. The
marketplace and plugin are enabled at the account level on claude.ai (web →
Plugins), and Claude Code syncs them down in the background after the first
message of an interactive session signed in with the claude.ai subscription
(random delay, up to ~10 min; a new session is needed to load them). `claude
plugin list` shows it as `quiz@synced`. The account-level marketplace entry
was corrected from the repo's old name `huit-claude-plugins` to
`huit-agent-plugins` on 2026-09-26; the re-sync landed the plugin under
`plugins/synced/<bucket>/quiz~g2/` (the `~gN` suffix is a sync generation).
`huit-aws` is now also enabled at the account level, so its manual
`claude plugin install` copy in `plugins/cache/` is redundant.

**Gotcha: sync is off under the Bedrock profile.** Sessions started via the
`claude-bedrock` alias (`CLAUDE_CODE_USE_BEDROCK=1`) are not signed in with
claude.ai, so synced plugins and skills never load there. `quiz:session` will
be missing in those sessions; the spin-down fallback covers it. See
[[auth-profiles]].

**Done (2026-09-29): `apigee-pull` / `apigee-push` replaced by the `huit-apigee`
plugin.** The plugin (synced from claude.ai, `ats-plugin-marketplace` repo, named `huit-agent-plugins` until 2026-09-30) ships
`huit-apigee:pull`, `huit-apigee:push` and `huit-apigee:status` skills plus a
bundled gotchas reference and `.apigee.json` per-repo config. The global
`~/.claude/commands/apigee-*.md` copies were deleted the same day. The drifted
copy in `aais-maestro-api/.claude/commands/` should also be deleted when that
repo is next touched. Design history is in harvard-huit/ats-plugin-marketplace
issue #5. New sessions pick the skills up; a session started before the sync
still lists the old command names until restarted.

**Decision: no per-skill git repos.** Shareable skills go into the single
`ats-plugin-marketplace` marketplace repo as plugins (this replaced the earlier
"one bundle repo if ever needed" idea and the zip-upload flow in
[[skill-sharing]]). Do not create one repo per skill.

**CLAUDE.md contract.** Global `CLAUDE.md` keeps only the always-on behaviors
(watch for topic shifts, offer `quiz:session` after significant changes) and
points to the `spin-down` skill for the wrap-up procedure. The old
`spin-down-tracking.md` / `spin-down-quiz.md` imports were deleted in 6d69a61.

**Why:** Keeping the procedure in a skill means it loads only when invoked
instead of on every turn. Moving the generic quiz to a marketplace plugin
means colleagues get it (and updates) from one source instead of re-zipped
uploads, and there is no stale local copy to drift.

**How to apply:** New personal procedures go in `skills/<name>/SKILL.md` with a
one-line pointer in `CLAUDE.md`, not as `@` imports. New shareable skills go
in the `ats-plugin-marketplace` repo as a plugin, after checking for
Harvard-specific hosts/IDs. Reference plugin skills by their namespaced name
(`quiz:session`), never the bare skill name.

**Gotcha:** commit 6d69a61 accidentally tracked two `skills/synced/` files
before the gitignore entry existed; both were untracked with `git rm --cached`
by 2026-09-19. If `git status` ever shows churn under `skills/synced/`, check
`git ls-files skills/synced` — a gitignore entry does not untrack files already
committed.
