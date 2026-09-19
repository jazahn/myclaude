---
name: spin-down
description: Wrap up a long-running session so a fresh one can take over cleanly. Captures durable facts to CLAUDE.md and memory, suggests GitHub/Jira issue updates, then runs a short comprehension quiz. Use when the user says "spin down", "wrap up", "let's close this out", or clearly signals a thread is finished. For a quiz alone, use the session-quiz skill instead.
---

# Spin down

Three phases, in order. Do not skip ahead; the capture phase is the reason the
skill exists. Never post to a tracker or edit an issue without an explicit
selection in phase 2.

## Phase 1 — Capture

1. **Repo-level facts → project `CLAUDE.md`.** Build/test/run commands,
   architecture, conventions discovered this session. Only what a fresh session
   could not derive from the code or git history.
2. **Decisions, preferences, gotchas, unfinished-work context → memory.**
   Follow `~/.claude/memory-routing.md` to pick exactly one home:
   - portable + project-scoped + version-controlled project → the project's
     committed `.claude/memory/` (with `INDEX.md` entry, and confirm the project
     `CLAUDE.md` imports it);
   - otherwise → machine-local `~/.claude/projects/<slug>/memory/` (with
     `MEMORY.md` entry).
   Use the standard frontmatter format. Convert relative dates to absolute.
   Update existing files rather than duplicating; delete ones proven wrong.
3. **Confirm what was saved** in a short list so the user can start a new
   session knowing the important context survives.

Write a 3–6 sentence summary of the session's work at this point; phases 2
and 3 reuse it.

## Phase 2 — Issue tracking (GitHub + Jira/AAIS)

Suggest, never perform unprompted. The two trackers have different audiences:

- **GitHub issues** (personal org): the *technical* record — root cause, files
  touched, commands, gotchas, follow-ups.
- **Jira AAIS** (visibility for management): the *high-level* record — what
  was accomplished and why it matters, plain language, no code detail. Link to
  the GitHub issue/PR for depth.

### Skip when
- The work is plainly not project work (personal settings, scratch
  experiments) — skip silently.
- A tracker is unavailable: no git repo → skip GitHub; Atlassian MCP not
  authenticated → say "Jira lookup skipped" in one line. Never stall on this
  phase; do whichever half is available.

### GitHub lookup (inline, cheap)
1. Check branch names and recent commit messages for `#\d+` refs; if found,
   `gh issue view <n>` to confirm.
2. Otherwise `gh issue list --assignee @me --state open --limit 25` in the
   working repo and match semantically against the session summary.
3. For repos on github.huit.harvard.edu, set `GH_HOST`; if auth fails, inject
   the right PAT by reference per `~/.claude/credentials.md` (`GITHUB_PAT` for
   github.com, `GITHUB_HUIT_PAT` for HUIT enterprise). Never print the token.

### Jira lookup (one subagent, to keep raw MCP JSON out of context)
Give the subagent the session summary and any `AAIS-\d+` keys seen in
branches/commits. Site `at-harvard.atlassian.net`, cloudId
`250e6bb8-19e0-4716-9635-67c711b7f031` (pass directly; skip
`getAccessibleAtlassianResources`). The subagent should:
1. If given a key, `getJiraIssue` it and confirm it matches.
2. Otherwise JQL:
   `project = AAIS AND (assignee = currentUser() OR watcher = currentUser()) AND statusCategory != Done ORDER BY updated DESC`
   (top ~25; fields key/summary/type/status/parent) and match semantically —
   do NOT rely on `text ~` keyword search.
3. If nothing matches, broaden once: Rovo `search` (or JQL without the
   assignee/watcher clause) scoped to AAIS, looking for a related
   epic/story/task/subtask at any level.
4. Return ONLY a compact verdict: matched key(s) + summary + type + status +
   why it matches (or "no match"), plus the related epic if found.

Run the GitHub lookup while the Jira subagent works — they are independent.

### Present the result
One `AskUserQuestion`, `multiSelect: true`, options shaped by the verdicts,
capped at the 4 most relevant:
- **Comment on GitHub #N** — technical draft as the description/preview.
- **Create new GitHub issue** — drafted title + technical body.
- **Comment on AAIS-NNN** — high-level draft ending with a link to the GitHub
  issue/PR.
- **Create new AAIS story/task** (under the related epic if found) — drafted
  summary + high-level description, linking to GitHub.

With multiSelect the user can pick nothing, so add no filler "no action"
option. If neither lookup found anything and the work isn't ticket-worthy,
report "no related issues found" in one line — no question needed.

### Rules
- Write actions (`gh issue create/comment`, `addCommentToJiraIssue`,
  `createJiraIssue`) stay behind the normal permission prompt; do not ask to
  allowlist them. Read-only lookups may be allowlisted freely.
- Keep it lightweight: a couple of `gh` calls inline, one subagent with 1–3
  MCP calls.

## Phase 3 — Comprehension quiz

Invoke the `session-quiz` skill (via the Skill tool). It owns the question
selection, format, and grading. If that skill is not available in this
environment, fall back to: 3–4 multiple-choice questions in one
`AskUserQuestion` call, prioritizing security-relevant decisions, then the
headline change, then non-obvious gotchas; grade briefly in text afterward.
