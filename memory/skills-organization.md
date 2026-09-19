---
name: skills-organization
description: Where user-scoped skills live in this repo, the spin-down → session-quiz split (personal vs shareable), why not per-skill repos, and leftover cleanup from the 2026-09-19 refactor
metadata:
  type: project
---

**Layout.** User-scoped skills are `~/.claude/skills/<name>/SKILL.md`, committed
and synced across machines by this repo (`.gitignore` whitelists `/skills/`).
`skills/synced/` is the claude.ai sync cache and is gitignored — see
[[skill-sharing]]. Local skills shadow synced ones of the same short name.

**Decision (2026-09-17/19): spin-down is a skill, session-quiz is a separate
skill.** `spin-down` phase 3 invokes `session-quiz` via the Skill tool, with an
inline text fallback if it is missing. The split is deliberate: `spin-down` is
personal and non-shareable (hardcodes the AAIS Jira cloudId, HUIT GitHub hosts,
and `credentials.md`), while `session-quiz` is generic and is the one uploaded
to claude.ai for colleagues. Edits to the local `session-quiz` do not reach the
uploaded copy until it is re-zipped and re-uploaded.

**Decision: no per-skill git repos.** Skills are single markdown files already
synced by this repo. If colleagues ever want to install via marketplace, build
ONE `claude-plugins` bundle repo holding the generic skills (session-quiz,
possibly the cost-report skills), and leave spin-down here. Do not create one
repo per skill.

**CLAUDE.md contract.** Global `CLAUDE.md` keeps only the always-on behaviors
(watch for topic shifts, offer `session-quiz` after significant changes) and
points to the `spin-down` skill for the wrap-up procedure. The old
`spin-down-tracking.md` / `spin-down-quiz.md` imports were deleted in 6d69a61.

**Why:** Keeping the procedure in a skill means it loads only when invoked
instead of on every turn, and separating the shareable quiz from the personal
wrapper is what makes uploading it to claude.ai possible.

**How to apply:** New personal procedures go in `skills/<name>/SKILL.md` with a
one-line pointer in `CLAUDE.md`, not as `@` imports. Before sharing a skill,
check it for Harvard-specific hosts/IDs and follow [[skill-sharing]] frontmatter
rules.

**Gotcha:** commit 6d69a61 accidentally tracked two `skills/synced/` files
before the gitignore entry existed; both were untracked with `git rm --cached`
by 2026-09-19. If `git status` ever shows churn under `skills/synced/`, check
`git ls-files skills/synced` — a gitignore entry does not untrack files already
committed.
