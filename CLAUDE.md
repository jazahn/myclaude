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
related follow-ups — only at genuine boundaries.

**When I say "spin down"** (or clearly signal I'm wrapping up a thread), invoke
the `spin-down` skill. It captures durable facts to CLAUDE.md + memory, suggests
GitHub/Jira updates, and runs a short comprehension quiz.

**After any significant change** landed without a formal spin-down (a merged
feature, a multi-file refactor, anything with security implications), offer the
quiz on its own: invoke the `session-quiz` skill.


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

@~/.claude/memory-routing.md
@~/.claude/memory/INDEX.md
@~/.claude/credentials.md
