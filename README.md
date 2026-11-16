# myclaude

This is my personal `~/.claude` directory, version-controlled and published so
other people can see how I have Claude Code set up. It is not a product and
not a template to clone wholesale. Read it, borrow the parts that fit, and
assume everything here reflects one person's tolerance for risk, not a
recommendation.

Anything I think is useful to more than me gets moved out of here and into
the [harvard-huit/ats-plugin-marketplace](https://github.com/harvard-huit/ats-plugin-marketplace)
plugin marketplace, where it is packaged as a plugin and delivered through
claude.ai account-level plugin sync. What remains in this repo is either
personal, Harvard-specific in a way that does not generalize, or not yet
mature enough to share.

## What is in here

| Path | What it is |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Global instructions loaded into every session: working style, session hygiene ("spin down"), issue-first, and `@` imports of the files below. |
| [memory-routing.md](memory-routing.md) | Rule for where a memory goes: this repo's committed `memory/` if it is portable, machine-local `projects/` otherwise. |
| [credentials.md](credentials.md) | Documents which secrets exist and how Claude must use them (inject by reference, never print). Contains no secret values. |
| [settings.json](settings.json) | Permissions, model, hooks, enabled plugins and marketplaces. See the security section before copying it. |
| [profiles/](profiles/) | Alternate settings for `claude --settings`, currently a Bedrock-via-Harvard-gateway fallback profile. |
| [skills/](skills/) | Personal skills: `spin-down`, `issue-first`, `snow-kb-policy`, `session-token-report`, `weekly-cost-report`. |
| [memory/](memory/) | Portable project memory for this setup itself (auth profiles, gotchas, decisions). Indexed by [memory/INDEX.md](memory/INDEX.md). |
| [claude-notifications/](claude-notifications/) | Hook wrappers installed by the `dimokol.claude-notifications` VS Code extension. They forward to the extension and are inert if it is absent. |
| `*.example` | Templates for the per-machine secret files that are deliberately not committed. |

## How the sharing works

The [.gitignore](.gitignore) uses a whitelist: everything under `~/.claude`
is ignored by default and only the files above are opted in. That is the
single most important design choice here, because a stock `~/.claude`
directory contains API keys, OAuth tokens, full conversation transcripts,
shell snapshots and plugin caches. Opting files in is safer than trying to
enumerate everything that should stay out.

Per-machine state lives in files that are ignored and have a committed
`.example` twin:

| Committed template | Local file | Holds |
|---|---|---|
| `.credentials.env.example` | `.credentials.env` | Third-party API keys and PATs, read by skills at run time. |
| `.ntfy-config.example` | `.ntfy-config` | ntfy.sh topic and token for push notifications. Missing file means the hooks are a silent no-op. |
| `.anthropic-key.example` | `.anthropic-key` | API key for the Bedrock fallback profile's `apiKeyHelper`. |

Memory is split the same way. Facts that hold on any machine go in the
committed `memory/` directory. Facts tied to one host, and all conversation
transcripts, stay in the ignored `projects/` tree.

## Security implications of publishing this

The repository is public. Here is what that does and does not expose, so you
can decide what you are comfortable with for your own setup.

**What is not here.** No API keys, tokens, passwords or conversation
transcripts are committed. The whitelist gitignore plus belt-and-suspenders
patterns for `*.key`, `.env*`, `*.jsonl`, `backups/` and `settings.local.json`
are there to keep it that way. I review `git status` before every commit.

**What is here that you might not want in your own public repo:**

- **Internal hostnames and URLs.** `credentials.md`, `profiles/` and several
  memory files name Harvard gateway hosts, an Apigee proxy, a GitHub
  Enterprise host and plugin marketplace repos. None of these are reachable
  without institutional auth, but they are a map of what exists.
- **Names of secrets.** `credentials.md` lists every credential I hold, what
  it is for and when it expires. That is intentional: Claude needs to know
  what is available without seeing the values. It is also a target list.
- **An org identifier.** `settings.json` carries `forceLoginOrgUUID`. It is
  not a credential, but it is a stable identifier for my organization.
- **Memory notes.** The `memory/` files record gotchas, dead-end
  investigations and who has which permission on which system. Nothing
  sensitive by policy, but it is operational detail about a real environment
  that I would not want to be surprised by. Read yours before you publish.
- **Third-party notification egress.** The `Stop` and `Notification` hooks
  post to ntfy.sh. The payload is the project directory's basename and the
  notification text, so the names of the repos I work in leave my machine.
  The hooks are a no-op without a local `.ntfy-config`.

**The real guard is behavioral, not technical.** `credentials.md` tells
Claude never to read or print secret values and to inject them by reference
in the same shell command that consumes them. The `Read` deny rule for
`.credentials.env` backs that up for the `Read` tool only. Because `Bash` is
fully allowed (next section), a `cat` of that file is not stopped by a
permission prompt. I accept that; you may not.

## Things I do that Claude itself does not recommend

I asked Claude to list the parts of this setup it would push back on. These
are deliberate trade-offs I have made for speed, in an environment where I
trust the model, the repos I work in and the network I am on. They are
listed so nobody copies them by accident.

- **`Bash(*)` in the allow list with `defaultMode: auto`.** Every shell
  command runs without a prompt. This is the single largest risk in the
  file: a prompt-injected instruction in a fetched web page, a README or a
  ServiceNow ticket can run arbitrary commands as me. The recommended
  posture is an allowlist of read-only commands and a prompt for the rest.
- **`WebFetch(*)`.** Any URL can be fetched without confirmation, which is
  the usual delivery route for the injection above.
- **`Edit(~/.claude/projects/**)`.** Claude can rewrite its own machine-local
  memory and anything else under the transcript tree without asking.
- **Broad MCP wildcards.** Entire Atlassian, Microsoft 365 and ServiceNow
  tool families are pre-approved, including write operations on Jira and
  Confluence. Prompts on writes would be the safer default.
- **Hardcoded `/Users/jazahn/...` paths in hook commands.** My own memory
  note says to use `$HOME`; `settings.json` still does not. The notification
  hooks therefore silently fail on any other machine.
- **Marketplace pinned to a `dev` branch.** `ats-plugin-marketplace` is
  consumed from `ref: dev`, so I pick up unreviewed plugin changes
  automatically.
- **`CLAUDE_CODE_SKIP_BEDROCK_AUTH=1` in the fallback profile.** Auth is
  delegated to a Harvard gateway by API key instead of AWS credentials.
  That is how the gateway works, but it means a leaked `.anthropic-key` is a
  full credential for the proxy.
- **Attribution header disabled.** `CLAUDE_CODE_ATTRIBUTION_HEADER=0` turns
  off the request header that identifies Claude Code traffic to Anthropic.

## Using any of this yourself

Do not clone this into your own `~/.claude`. Instead:

1. Copy the [.gitignore](.gitignore) whitelist and adapt the opt-in list to
   what you actually want to share.
2. Copy the `.example` pattern for anything secret or machine-specific, and
   keep the documentation of *what* exists in a committed file like
   `credentials.md`.
3. Take skills one directory at a time. Each `skills/<name>/SKILL.md` is
   self-contained, but several hardcode Harvard hosts or IDs; check before
   reusing.
4. Write your own `settings.json` permissions. Start from prompts and loosen
   deliberately, rather than starting from mine and tightening.

For the pieces meant to be shared, go to
[harvard-huit/ats-plugin-marketplace](https://github.com/harvard-huit/ats-plugin-marketplace)
and enable the plugins there instead.
