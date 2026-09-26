---
name: huit-github-enterprise-api
description: github.huit.harvard.edu access — gh OAuth device-flow login works (verified 2026-09-19); the Bearer 401 only hits classic PATs, and both stored PATs were dead as of 2026-09-19. Org is HUIT; some repos are live there while the github.com copy is a stale mirror.
metadata:
  type: reference
---

Working with `github.huit.harvard.edu` (GitHub Enterprise Server, 3.19 per its
API docs URL as of 2026-09-19):

- **Use `gh` with an OAuth login, not a PAT.** `gh auth login --hostname
  github.huit.harvard.edu --web` works, and afterwards `gh api --hostname
  github.huit.harvard.edu ...` and `GH_HOST=github.huit.harvard.edu gh release
  download ...` both work (verified 2026-09-19, gh 2.96.0). Reuse the token
  elsewhere with `gh auth token --hostname github.huit.harvard.edu`.
- **Classic PATs are the ones that hit the Bearer 401.** `gh` sends
  `Authorization: Bearer <token>`, which this GHES rejects for classic PATs;
  `curl -H "Authorization: token <token>"` accepted them. Moot now: on
  2026-09-19 both `GITHUB_HUIT_PAT` and `GITHUB_PAT` in `.credentials.env`
  returned `401 Bad credentials` even via curl, so they are revoked or expired.
  Prefer the `gh` keyring token; only regenerate a PAT if something needs one.
- **A 404 on write means scope, not absence.** GitHub returns 404 rather than 403
  for unauthorized writes, so `POST .../issues` 404s on a read-only token even
  when `GET` on the same repo returns 200 with `"permissions": {"admin": true}`.
  Check `x-oauth-scopes` in the response headers; issue creation needs `repo`.
- **The org is `HUIT`, not `harvard-huit`.** `harvard-huit` is the github.com org.
  On the enterprise instance `HUIT/aais-ecs-infrastructure`,
  `HUIT/aais-services-config`, etc.
- **Some repos are live on enterprise while the github.com copy is a stale
  mirror.** `aais-ecs-infrastructure` was pushed 2026-07-27 on enterprise vs
  2026-04-28 on github.com — yet migrated workflows reference a
  `harvard-huit/aais-ecs-infrastructure@github.com-actions` branch on the stale
  mirror. Check `pushed_at` on both before assuming which is canonical.
- **Cross-instance references do not auto-link.** A `owner/repo#N` shorthand only
  resolves within one instance; use full URLs both directions, and expect no
  backlink notification between them.

Tokens: `GITHUB_HUIT_PAT` per [[credentials-store-pattern]] (a copy also lives in
some project `.env` files — they can drift; check both). `GITHUB_PAT` is the
github.com one.
