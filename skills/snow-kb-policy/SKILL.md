---
name: snow-kb-policy
description: Look up current Harvard/HUIT IT security policies, standards and guidance in the ServiceNow knowledge base (via the ats-snow-proxy Apigee API) and cite them. Use whenever a question or task touches Harvard security policy — "what's the policy on…", "is X allowed at Harvard", "what does HUIT require for…", data classification levels, credential/password/1Password handling, HarvardKey/MFA, encryption, vulnerability management (UWVM, Nessus, Wiz), CrowdStrike, secure system configuration, device disposal, travel — or before advising on auth, secrets, or data handling in a Harvard context. Also use when the user asks to check, search, or list ServiceNow KB articles.
tools: Bash
---

# ServiceNow KB — security policy lookup

Searches published, in-date `kb_knowledge` articles through the `ats-snow-proxy` Apigee proxy
(read-only; the proxy authenticates to ServiceNow itself). Default scope is the
**Harvard University IT** knowledge base, which is where security policy content lives —
mostly under the **Information Security** category (also **HarvardKey** for MFA/login topics).
There is no separate "security" KB.

## How to run

```bash
python3 ~/.claude/skills/snow-kb-policy/kb_search.py "<search terms>"                   # full-text search, top 10
python3 ~/.claude/skills/snow-kb-policy/kb_search.py --full --limit 3 "<terms>"          # include article bodies (HTML stripped)
python3 ~/.claude/skills/snow-kb-policy/kb_search.py --id KB0013127                      # one article with body
python3 ~/.claude/skills/snow-kb-policy/kb_search.py --category "Information Security" --limit 60   # browse the whole category
python3 ~/.claude/skills/snow-kb-policy/kb_search.py --list-kbs                          # knowledge bases + counts
python3 ~/.claude/skills/snow-kb-policy/kb_search.py --list-categories "<terms>"         # where matching articles live
```

Useful flags: `--like` (AND-match each word instead of full-text; use when full-text returns
nothing), `--all-kbs`, `--kb <title>`, `--since YYYY-MM-DD`, `--max-chars N`, `--show-query`,
`--env dev` (the harvardtest clone — stale, and its `u_direct_url`s point at the test instance).

Output is JSON: `{env, count, query, results:[{number, short_description, meta_description,
u_direct_url, kb_knowledge_base, kb_category, published, valid_to, sys_updated_on, text?}]}`.

## Workflow

1. Search once with the user's topic in plain words (2–4 terms). If the top hits look off,
   try `--category "Information Security"` with the terms, or `--like`.
2. Pick the 1–3 most relevant articles and fetch bodies with `--full` (or `--id`) before
   answering. Answer from the body, not from memory.
3. In the answer, cite each article as **KB number – title** with its `u_direct_url`, and give
   the `published` date so staleness is visible. If `text` is empty or carries `text_note`,
   say the body wasn't readable and point at the link.
4. If nothing relevant comes back, say so. Do not invent policy. University-wide policy text
   also lives outside ServiceNow (policy.security.harvard.edu); mention that when the KB has
   only how-to guidance for the topic.

## Config and secrets

- Key: `SNOW_PROXY_APIKEY` in `~/.claude/.credentials.env` (prod consumer key for
  ats-snow-proxy; `SNOW_PROXY_APIKEY_DEV` for `--env dev`). The script reads it itself. Never
  print the key, never pass it on the command line, never write it anywhere else.
- If the script exits with "SNOW_PROXY_APIKEY is not set", tell the user to add it to
  `~/.claude/.credentials.env` (documented in `~/.claude/credentials.md`) and stop.
- `SNOW_PROXY_URL` overrides the base URL; `SNOW_KB_SECURITY_KBS` overrides the default KB scope.

## Notes for maintainers

- Proxy source: `~/workshop/ats-snow-proxy` (CLAUDE.md there documents the proxy). The spec's
  field notes apply: `meta_description` is the real summary, `u_direct_url` is the public link,
  `number` may be ACL-hidden on some records.
- All query logic is in `kb_search.py` so it can be lifted into an MCP tool if an official
  ServiceNow MCP server appears; only this file's "How to run" section would change.
