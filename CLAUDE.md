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

**When I say "spin down"** (or clearly signal I'm wrapping up a thread):
1. Capture durable, repo-level facts (build/test/run commands, architecture,
   conventions discovered) into the relevant project `CLAUDE.md`.
2. Capture decisions, preferences, gotchas, and unfinished-work context into project
   memory files (with `MEMORY.md` index entries).
3. Confirm what was saved so I can safely start a new session — the fresh session
   inherits everything important via CLAUDE.md + memory, but sheds the expensive,
   irrelevant history.


## Workflow Orchestration

### 1. Plan Mode Default
- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately - don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity

### 2. Subagent Strategy
- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop
- After ANY correction from the user: update `tasks/lessons.md` with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done
- Never mark a task complete without proving it works
- Diff your behavior between main and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)
- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes - don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing
- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests - then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

### 7. Task Management
1. **Plan First**: Write plan to `tasks/todo.md` with checkable items
2. **Verify Plan**: Check in before starting implementation
3. **Track Progress**: Mark items complete as you go
4. **Explain Changes**: High-level summary at each step
5. **Document Results**: Add review section to `tasks/todo.md`
6. **Capture Lessons**: Update `tasks/lessons.md` after corrections

### Core Principles
- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

@~/.claude/memory-routing.md
