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
- Administer the quiz with the `AskUserQuestion` tool so I get the radio-select
  UI, not plain text I have to type answers to. Pass all questions in a single
  `AskUserQuestion` call (it accepts up to 4) so I answer them together.
- Because that tool caps at 4 questions and 4 options each, keep it to 3–4
  multiple-choice questions with 2–4 options apiece. Make one option clearly
  correct; the rest plausible-but-wrong (not throwaway) so a guess is informed,
  not automatic. The whole thing should be scannable in under a minute.
- Each question should map to something that actually happened this session.
- "Other" is added automatically by the tool, so I can always free-type if none
  of the options fit — no need to add your own catch-all option.

## What to quiz on (in priority order)
1. **Security risks** — anything touching auth, secrets, permissions, input
   handling, external calls, or destructive operations. Always include at least
   one of these if the session touched them.
2. **Major changes** — the headline thing(s) built or changed, and where they
   live (which file/component).
3. **Non-obvious decisions or gotchas** — a tradeoff made, a constraint worked
   around, or behavior that would surprise someone reading the code cold.

## After I answer
- Once the tool returns my selections, grade them in a normal text reply:
  briefly confirm correct answers and gently correct wrong or partial ones,
  pointing at the specific file/line or decision when useful.
- If I get something important wrong (especially a security item), flag it plainly
  — that's a signal the change deserves a closer look before I move on.
- Keep the tone collegial, not schoolteacher-ish. If I skip the quiz, drop it
  without pushing.
