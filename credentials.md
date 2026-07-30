# Available credentials

Secret values live in `~/.claude/.credentials.env` (machine-local, gitignored,
chmod 600) — set up on a new machine from `.credentials.env.example`. This file
documents only what exists and how to use it.

## Usage rules (for Claude)

- **Never read, cat, echo, or print** `.credentials.env` or any credential
  value into the conversation. A `Read`-deny rule in settings.json enforces this.
- **Inject by reference** in the same shell command that consumes the value, so
  the secret never enters context or the transcript:

  ```sh
  GITHUB_PAT=$(grep '^GITHUB_PAT=' ~/.claude/.credentials.env | cut -d= -f2-) some-command
  ```

  or for a command that reads env vars directly:

  ```sh
  export $(grep -v '^#' ~/.claude/.credentials.env | xargs) && some-command
  ```

- If a key is missing or empty, say so and point me at `.credentials.env` —
  don't guess or substitute.

## Keys

| Key | For | Notes |
|---|---|---|
| `SPLUNK_API_KEY` | HUIT ATS Splunk API (FAS service account) | Use with `SPLUNK_API_URL` below |
| `GITHUB_PAT` | github.com — harvard-huit and other SSO-protected orgs | expires 2027-07-01 |
| `GITHUB_HUIT_PAT` | github.huit.harvard.edu — HUIT org repos | expires 2027-01-01 |

## Non-secret config

```
SPLUNK_API_URL=https://go.prod.apis.huit.harvard.edu/ats/splunk/v1/FAS_service_account
```
