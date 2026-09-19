---
name: session-quiz
description: Short multiple-choice comprehension check on what happened in the current session, so important things that scrolled past (security-relevant changes, decisions Claude made on the user's behalf, gotchas, unfinished work) don't get lost. Use when the user asks to be quizzed, says "quiz me", "did I miss anything", "what should I know from this session", or wants to check their understanding before wrapping up. Also offer it unprompted right after a significant change lands (a merged feature, a multi-file refactor, anything touching auth, secrets, permissions, or external systems). An optional argument narrows the focus, e.g. `security` or `decisions`.
---

# Session quiz

Long sessions accumulate things the user never actually read: tool output that
scrolled by, permission prompts approved on autopilot, judgment calls Claude
made without asking, work done by subagents. The quiz is a lightweight way to
surface those before the session ends, framed as a check the user can pass in
under a minute rather than an exam. Pass or fail matters less than the user
finding out *what* they didn't know.

If an argument was given (e.g. `security`), bias question selection toward
that category but still include anything critical from other categories.

## Step 1: Find what whizzed by

Scan the whole session, including any compaction summary, and collect
candidates. Prefer things the user is least likely to have noticed:

- **Long tool results** the user almost certainly skimmed: test output, diffs,
  logs, API responses. What conclusion was drawn from them?
- **Judgment calls Claude made silently**: an assumption chosen over asking, a
  scope interpretation, a default picked among alternatives, a fix applied to a
  different place than the user pointed at.
- **Work done out of sight**: subagent results, background tasks, anything
  summarized rather than shown.
- **Things approved quickly**: commands run behind a permission prompt,
  especially ones that changed state (installs, config edits, deletes,
  network calls, git operations).
- **Things skipped, deferred, or left half-done**, and why.

Then rank candidates by how much it would cost the user to be wrong about them:

1. **Security and safety**: auth, secrets, permissions, input handling,
   external calls, data exposure, destructive or irreversible operations.
   If the session touched any of these, at least one question covers it.
2. **The headline change**: what was built or changed and where it lives.
3. **Non-obvious decisions and gotchas**: tradeoffs, constraints worked
   around, behavior that would surprise a cold reader in a month.
4. **Loose ends**: what is not finished, what still needs verification.

If nothing in the session rises to this bar (a short Q&A, a trivial edit), say
so in one line and stop. Do not manufacture questions to fill a quota.

## Step 2: Write the questions

- 3 or 4 questions. Each maps to a specific thing that actually happened in
  this session, not to general knowledge.
- Multiple choice, 2 to 4 options. Exactly one is correct. The wrong options
  are the beliefs a skimmer would plausibly have formed, so a guess is
  informed rather than automatic. Avoid trivia (exact line numbers, variable
  names) in favor of consequences (what would break, who can now access what,
  what still needs doing).
- Keep each question and its options scannable. One sentence per option.
- Do not add a catch-all like "none of the above" or "not sure"; the user can
  always answer freely in their own words.

## Step 3: Ask

Use whatever the environment offers for structured questions:

- **Claude Code**: one `AskUserQuestion` call carrying every question (the tool
  holds up to 4), so the user answers them together in the select UI. Use a
  short header per question (e.g. `Security`, `Change`, `Gotcha`).
- **Anywhere else** (claude.ai, no structured-question tool): post the
  questions as a numbered list with lettered options in one message and wait
  for the user's reply before grading.

## Step 4: Grade

Reply in normal text, briefly:

- Confirm correct answers in a few words each.
- For wrong or partial answers, give the right answer and point to where the
  evidence lives (file and function, the tool result, the decision point in
  the conversation) so the user can go look.
- If a wrong answer is about a security or safety item, say plainly that the
  change deserves a closer look before moving on. That is the one place the
  quiz should push a little.
- Collegial tone. If the user skips or dismisses the quiz, drop it without
  comment.

## Example

Session: added an API client that reads a token from an environment variable,
retried on 5xx, and Claude chose to log the full response body on failure.

Good question: "When a request to the upstream API fails, what ends up in the
logs?" with options: the status code only / the full response body, which may
include the token echo / nothing, failures are silent / a redacted summary.
The correct answer surfaces a decision the user probably didn't see and has a
real consequence.

Weak question: "What HTTP library was used?" The answer has no consequence and
the user can find it in one grep.
