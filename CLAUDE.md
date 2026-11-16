# Working preferences

## Session hygiene / spin-down

I tend to keep a single session running for a long time, often carrying unrelated
tasks forward in the same context. This is costly: every turn re-reads the entire
accumulated context, so unrelated past work inflates the per-turn token cost (and
eventually triggers compaction, which loses fidelity).

**Watch for topic changes.** When the conversation shifts to a task that is
substantially unrelated to the recent work — different goal, different files, a
question disconnected from the last stretch — gently remind me, in one line, that I
can "spin down" and start a fresh session. Keep it brief and non-naggy; mention it
once per topic shift, not every message. Don't interrupt mid-task or for closely
related follow-ups — only at genuine boundaries. "Recent work" means earlier
turns in *this* conversation only — never the project's git history, CLAUDE.md,
or memory notes. The first message of a session is never a topic shift, so never
suggest spinning down on turn one.

**When I say "spin down"** (or clearly signal I'm wrapping up a thread), invoke
the `spin-down` skill. It captures durable facts to CLAUDE.md + memory, suggests
GitHub/Jira updates, and runs a short comprehension quiz.

**After any significant change** landed without a formal spin-down (a merged
feature, a multi-file refactor, anything with security implications), offer the
quiz on its own: invoke the `quiz:session` skill (from the HUIT `quiz` plugin,
synced from claude.ai).


## Working style

- **Plan first when the approach is genuinely ambiguous** — architectural
  decisions, multiple viable designs, or unclear requirements. For tasks with an
  obvious path, just do the work. If something goes sideways mid-task, stop and
  re-plan rather than pushing through.
- **Delegate when work fans out** across independent items (many files to read,
  parallel research threads, independent analyses) — use subagents so the main
  context stays clean. Work directly for single-file reads and sequential edits.
- **After a correction from me**, save the pattern as a `feedback` memory
  (per my memory routing rules) so the same mistake doesn't recur across sessions.
- **Bug reports are work orders**: given logs, errors, or failing tests, fix the
  root cause and prove it works (run the tests, show the output) — don't ask me
  to shepherd it.
- **Tracker items are always id + title.** I don't remember what issue is
  which by id alone. Any time you mention a Jira issue, GitHub issue/PR, or
  Trello card — in prose, in a question option, in a commit message draft, in
  a spin-down summary — write it as `AAIS-123 "Summary text"`, `#45 "Issue
  title"`, or `"Card name"` (card title is the id). If you only have the id,
  look the title up first (`getJiraIssue`, `gh issue view`, `issue_read`);
  never emit a bare id.

## Issue first, card first

Before starting a **new work item** in a repo with a GitHub remote, invoke the
`issue-first` skill: it looks for a matching GitHub issue and offers to create
one if there is none. A new work item is a request that will change files, and
also a mid-session shift to a bug or side task that is not part of the item
already in progress (a question or a read-only task is not one). The skill
reads the per-project setting from `CLAUDE.local.md` (`issue-first: on|off`);
if there is none, it asks once whether to use or ignore it for that project
and records the answer there. `off` means skip silently. Check once per item,
not once per message.

The `trello` plugin's `card-first` skill (`/trello:card-first`) is the same
check against my Trello board, and it applies in any directory, not only git
repos. Its trigger comes from the plugin's own `SessionStart` hook, which
reads `card-first: on|off` from `CLAUDE.local.md`, so nothing here needs to
fire it. When both apply to one item, run both searches first and ask **one**
combined question (issue and card together); the card's description carries
the issue URL. When a work item linked to a card lands or wraps up (including
in `spin-down`), the card update the skill proposes counts as one of the
tracker updates to suggest, next to GitHub and Jira.

@~/.claude/memory-routing.md
@~/.claude/memory/INDEX.md
@~/.claude/credentials.md
