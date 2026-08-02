# Spin-down issue tracking (GitHub + Jira/AAIS)

After the spin-down capture steps (CLAUDE.md + memory writes) and BEFORE the
comprehension quiz, check whether the session's work relates to tracked issues,
and suggest — never perform unprompted — updates in one or both trackers.

The two trackers serve different audiences; draft content accordingly:
- **GitHub issues** (my personal organization): the *technical* record — root
  cause, files touched, commands, gotchas, follow-up work. Detail lives here.
- **Jira AAIS** (visibility for my bosses): the *high-level* record — what was
  accomplished and why it matters, in plain language a manager can skim. No
  code-level detail; link to the GitHub issue/PR for anyone who wants depth.

## When to skip
- The session's work is plainly not project work (personal settings tweaks,
  scratch experiments) — skip silently.
- A tracker is unavailable (no git repo → skip GitHub; Atlassian MCP not
  authenticated → say "Jira lookup skipped" in one line). Never stall the
  spin-down on this step; do whichever half is available.

## GitHub lookup (inline — cheap, no subagent needed)
1. Check branch names and recent commit messages for `#\d+` refs; if found,
   `gh issue view <n>` to confirm.
2. Otherwise `gh issue list --assignee @me --state open` in the working repo
   (add `--limit 25`) and match semantically against the session's work.
3. For repos on github.huit.harvard.edu, set `GH_HOST`; if auth fails, inject
   the right PAT by reference per credentials.md (`GITHUB_PAT` for github.com,
   `GITHUB_HUIT_PAT` for HUIT enterprise) — never print the token.

## Jira lookup (subagent, to keep raw MCP JSON out of this context)
Give one subagent: a 3–6 sentence summary of the session's work (reuse the
spin-down capture summary) and any `AAIS-\d+` keys spotted in branches/commits.

Site: `at-harvard.atlassian.net`, cloudId `250e6bb8-19e0-4716-9635-67c711b7f031`
(pass directly; skip the `getAccessibleAtlassianResources` call).

The subagent should:
1. If given an issue key, fetch it (`getJiraIssue`) and confirm it matches.
2. Otherwise run JQL:
   `project = AAIS AND (assignee = currentUser() OR watcher = currentUser()) AND statusCategory != Done ORDER BY updated DESC`
   (top ~25, fields: key/summary/type/status/parent) and match semantically —
   do NOT rely on `text ~` keyword search for matching.
3. If nothing matches, broaden once: Rovo `search` (or JQL without the
   assignee/watcher clause) scoped to AAIS, looking for a related
   epic/story/task/subtask at any level.
4. Return ONLY a compact verdict: matched key(s) + summary + type + status +
   why it matches (or "no match"), plus the related epic if one was found.

Run the GitHub lookup while the Jira subagent works — they're independent.

## How to present the result
One `AskUserQuestion` call, `multiSelect: true` (GitHub and Jira actions are
not mutually exclusive), options shaped by the verdicts:
- **Comment on GitHub #N** — technical draft as the option description/preview.
- **Create new GitHub issue** — drafted title + technical body.
- **Comment on AAIS-NNN** — high-level draft, ending with a link to the GitHub
  issue/PR.
- **Create new AAIS story/task** (under the related epic if found) — drafted
  summary + high-level description, linking to GitHub.
Always leave "no action" achievable — with multiSelect the user can select
nothing, so don't add a filler option; cap at the 4 most relevant actions.

If neither lookup found anything and the work isn't ticket-worthy, just report
"no related issues found" in one line — no question needed.

## Rules
- Never post, create, or edit anything without my explicit selection above.
  Write actions (`gh issue create/comment`, `addCommentToJiraIssue`,
  `createJiraIssue`) stay behind the normal permission prompt — do not ask to
  allowlist them.
- Read-only lookups (gh list/view, Jira search/get) may be allowlisted freely.
- Keep the whole step lightweight: a couple of gh calls inline, one subagent
  with 1–3 MCP calls.
