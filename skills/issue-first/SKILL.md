---
name: issue-first
description: Check GitHub for an issue matching a work item before starting on it, and offer to create one if none exists. Use at the start of any new work item in a repo with a github.com or github.huit.harvard.edu remote (a request that will change files, not a question or a read-only task), and again when the conversation shifts mid-session to a bug or side task that is not part of the item already being worked on. Per-project on/off is recorded in CLAUDE.local.md; when that file has no setting, the skill asks once. Also use when the user asks "is there an issue for this", "find the issue", "make an issue for this", or invokes /issue-first.
---

# Issue first

Before new work starts, find the GitHub issue it belongs to, or offer to open
one. Then get on with the work. The check is a short detour, never a gate:
one or two lines in your reply, one question at most, and the work proceeds
either way.

## What counts as a new work item

- A request that will change files in the repo: a feature, a refactor, a fix,
  a config or docs change with substance.
- A **mid-session shift**: a bug the user reports, or a side task they raise,
  that is not directly part of the item already being worked on. "Also, the
  status skill hangs when gcloud is logged out" during a push-skill task is
  a new item. "The push skill also needs to handle the 404 case" is the
  same item.

Not a work item: a question, exploring or explaining code, a one-line fix
to the thing you are already doing, scratch experiments, or anything in a
repo whose remote is not GitHub. In those cases say nothing about issues.

Check once per item. Keep a mental list of items already matched or
declined in this session and do not re-ask for them.

## Step 0: project setting

Resolve the repo root with `git rev-parse --show-toplevel`. Read
`CLAUDE.local.md` there (it is per-machine and never committed) and look for
a line matching `issue-first: on` or `issue-first: off`.

- **`off`**: do nothing and say nothing. Proceed with the work.
- **`on`**: go to step 1.
- **No setting, or no file**: ask before doing anything else. Use
  AskUserQuestion when the session is interactive:

  > This repo has no issue-first setting. Check GitHub issues before new work here?
  > - Use it here (recorded in CLAUDE.local.md, won't ask again)
  > - Ignore for this project (recorded, won't ask again)
  > - Just this once (not recorded)

  Record the answer with a single line in `CLAUDE.local.md`, appending to
  the file if it exists and creating it if not:

  ```
  # Claude Code local notes for this checkout (not committed)
  issue-first: on
  ```

  Then make sure git ignores it without touching the shared tree:

  ```sh
  git check-ignore -q CLAUDE.local.md || echo CLAUDE.local.md >> "$(git rev-parse --git-dir)/info/exclude"
  ```

  "Use it here" and "just this once" continue to step 1; "ignore" stops.
  In a non-interactive session with no setting, skip the check, note in one
  line that issue-first is unconfigured for this repo, and proceed.

Never write the setting into `CLAUDE.md`: that file is shared with the team,
and this is a personal preference.

## Step 1: identify the repo and the tools

`git remote get-url origin` gives host and `owner/repo`.

| Host | MCP server (prefer when connected) | CLI fallback |
|---|---|---|
| github.com | `github` (`mcp__plugin_huit-github_github__*`) | `gh -R owner/repo ...` |
| github.huit.harvard.edu | `github-huit` (`mcp__plugin_huit-github_github-huit__*`) | `GH_HOST=github.huit.harvard.edu gh -R owner/repo ...` |
| anything else | skip silently | |

If neither the MCP server nor a `gh` login for that host is available, say
so in one line, point at `/huit-github:github-setup`, and proceed with the
work without the check. Never inject a PAT for this; it is a convenience
check, not worth a secret in the transcript.

Some HUIT repos are live on GHES with a stale github.com mirror or the
reverse. Check the host the remote actually points at, not the other copy.

## Step 2: search

Do the cheap checks first, and keep output small (`minimal_output`, limits
of 10 to 20).

1. **Branch and recent commits.** If the current branch name or the last
   few commit subjects carry `#N` and that issue matches the request, it is
   the item. Confirm with `issue_read` or `gh issue view N`.
2. **Keyword search, open issues.** Two to four distinctive words from the
   request, one or two phrasings:
   `search_issues` with `repo:owner/repo is:issue is:open <words>`, or
   `gh issue list --state open --search "<words>" --limit 10`.
3. **Semantic pass.** If keyword search finds nothing, list the most recent
   open issues (limit 20, titles only) and match by meaning. Many issues are
   titled differently from how the request was phrased.
4. **Closed issues, only when 1 to 3 found nothing** and the request sounds
   like a regression or a reopen ("this broke again", "the fix didn't
   take"). Search `is:closed`; a close match is worth mentioning so the new
   issue can reference it.

Read-only throughout. Nothing is created, edited, or commented on in this
step.

## Step 3: report, then work

**Match found.** One line, then start the work:

> Tracking this as #12 "add the service-now mcp".

Carry the number forward: use it in a new branch name if you create one
(`12-servicenow-mcp` or the repo's own convention), and reference it in
commit messages. `Refs #N` while the work is partial; `Closes #N` only in
the commit or PR that finishes it.

**No match.** Draft the issue and ask once:

> No open issue matches. Create one?
> **Title:** <imperative, under 70 chars>
> **Body:** what is being asked, why (one or two lines), and what done
> looks like (two or three bullets). Reference any related closed issue.

Options: create, skip. Create with `issue_write` (method `create`) or
`gh issue create`. Use only labels that already exist on the repo (check
with `get_label` or `gh label list` if you want one); never invent labels,
milestones, or assignees. After creating, report the number and proceed as
in the match case. On skip, proceed with no further mention.

In a non-interactive session, state that no issue matched and proceed; do
not create one without an explicit yes.

**Several plausible matches.** List them (number and title, up to five) in
the same question and let the user pick or choose "none, create new".

## Rules

- One question per item at most. If step 0 already asked (the first time in
  a repo), fold the "create one?" question into the following turn rather
  than asking twice in a row.
- Every issue mention carries its title: `#12 "add the service-now mcp"`,
  never a bare `#12`. This includes the match line, the "several matches"
  list, and any related closed issue you cite. If a branch or commit gave
  you only a number, fetch the title before reporting it.
- Never create, reopen, close, or comment without an explicit yes in this
  session.
- Never edit `CLAUDE.md`, and never commit `CLAUDE.local.md`.
- Do not repeat the check for the same item after a compaction; if the
  conversation summary says an item is tracked as #N, trust it.
- This skill is personal by design (decided 2026-10-31): it is a process
  preference, not a GitHub capability, so it does not belong in
  `huit-github`. If it ever ships in the marketplace it becomes its own
  plugin, the trigger paragraph in `~/.claude/CLAUDE.md` becomes a
  SessionStart hook that stays silent when the remote is not GitHub or
  `CLAUDE.local.md` says `off`, and this file stays the procedure.
