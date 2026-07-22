# Spin-down comprehension quiz

After a "spin down" (or after any significant change — a merged feature, a
refactor touching multiple files, anything with security implications), offer a
short quiz to test my understanding of what happened this session. Run it AFTER
the spin-down capture steps (CLAUDE.md + memory writes) are done, or immediately
after landing a significant change if no formal spin-down was requested.

## Purpose
The quiz is a lightweight comprehension check, not an exam. It exists so I walk
away actually understanding the major changes, the security-relevant decisions,
and the parts of the code that would surprise a future reader — not just trusting
that "it works."

## Format
- 3–5 questions, no more. Keep the whole thing scannable in under a minute.
- Number the questions and ask them all at once (don't drip one at a time).
- Mostly multiple-choice or short-answer where the answer is *almost* guessable
  from common sense — the goal is recognition and reinforcement, not stumping me.
- Each question should map to something that actually happened this session.

## What to quiz on (in priority order)
1. **Security risks** — anything touching auth, secrets, permissions, input
   handling, external calls, or destructive operations. Always include at least
   one of these if the session touched them.
2. **Major changes** — the headline thing(s) built or changed, and where they
   live (which file/component).
3. **Non-obvious decisions or gotchas** — a tradeoff made, a constraint worked
   around, or behavior that would surprise someone reading the code cold.

## After I answer
- Briefly confirm correct answers and gently correct wrong or partial ones,
  pointing at the specific file/line or decision when useful.
- If I get something important wrong (especially a security item), flag it plainly
  — that's a signal the change deserves a closer look before I move on.
- Keep the tone collegial, not schoolteacher-ish. If I skip the quiz, drop it
  without pushing.
