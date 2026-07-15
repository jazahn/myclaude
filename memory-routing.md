# Memory routing (cross-machine)

I work on the same projects from multiple machines. Machine-local memory
(`~/.claude/projects/<slug>/memory/`) does NOT travel between them (the
`projects/` dir is machine-local and, in the settings repo, gitignored), so
before saving any memory, route it to exactly ONE home — never both:

**Write to the project's committed `.claude/memory/` when ALL hold:**
- the fact is durable and project-scoped (a decision, gotcha, convention, or
  unfinished-work context — the same things the spin-down protocol captures), AND
- it is true regardless of which machine I'm on (no host-specific paths, tokens,
  ntfy topics, or OS details), AND
- the project is version-controlled (so the committed file actually syncs).

  Use the same file format as machine-local memory (frontmatter + body). Keep a
  `.claude/memory/INDEX.md` mirroring the MEMORY.md convention. Ensure the project
  `CLAUDE.md` imports it (`@.claude/memory/INDEX.md`) so it loads into context —
  a committed memory that nothing imports will not be recalled.

**Keep in machine-local `~/.claude` memory otherwise:** host-specific facts
(paths, topics, tokens, per-machine setup), anything for a non-git project, and
transient conversation context.

If a fact is portable but the project isn't version-controlled, save it
machine-local and mention once that committing the project would make it portable.
