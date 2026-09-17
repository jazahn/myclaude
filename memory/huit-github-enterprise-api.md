---
name: huit-github-enterprise-api
description: gh CLI cannot authenticate to github.huit.harvard.edu (Bearer vs token scheme); use curl. Enterprise org is HUIT, and some repos are live there while the github.com copy is a stale mirror.
metadata:
  type: reference
---

Working with `github.huit.harvard.edu` (GitHub Enterprise Server 3.17):

- **`gh` does not work there with a classic PAT.** It sends
  `Authorization: Bearer <token>`, which this GHES rejects with a 401 for classic
  PATs. `curl -H "Authorization: token <token>"` against
  `https://github.huit.harvard.edu/api/v3/...` works with the same token. Don't
  conclude a token is revoked because `gh auth status` or `gh api` says so — test
  with curl before reporting it dead.
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
