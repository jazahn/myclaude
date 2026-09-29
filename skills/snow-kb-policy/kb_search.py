#!/usr/bin/env python3
"""Search Harvard ServiceNow knowledge-base articles through the ats-snow-proxy Apigee proxy.

Read-only. Talks to GET /table/kb_knowledge (and /stats, /table/kb_knowledge_base for
discovery). Designed so the query logic can be lifted into an MCP tool later.

Config (env var overrides file):
  SNOW_PROXY_APIKEY      consumer key (default: read from ~/.claude/.credentials.env)
  SNOW_PROXY_APIKEY_DEV  consumer key for --env dev
  SNOW_PROXY_URL         proxy base URL (default: prod)
  SNOW_KB_SECURITY_KBS   default KB scope, comma-separated knowledge-base titles
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

CRED_FILE = os.environ.get("SNOW_CRED_FILE", os.path.expanduser("~/.claude/.credentials.env"))
URLS = {
    "prod": "https://go.prod.apis.huit.harvard.edu/ats-snow-proxy",
    "stage": "https://go.stage.apis.huit.harvard.edu/ats-snow-proxy",
    "dev": "https://go.dev.apis.huit.harvard.edu/ats-snow-proxy",
}
# Discovered with --list-kbs (2026-09-29): there is no separate security KB; policy content lives in the
# "Harvard University IT" KB, mostly under the "Information Security" category (28 articles) and
# "HarvardKey". Override with SNOW_KB_SECURITY_KBS or --kb.
DEFAULT_KBS = ["Harvard University IT"]
BASE_FIELDS = [
    "sys_id", "number", "short_description", "meta_description", "u_direct_url",
    "kb_knowledge_base", "kb_category", "workflow_state", "published", "valid_to",
    "sys_updated_on",
]


def read_cred(name):
    """Return a value from the credentials file without echoing anything else."""
    if os.environ.get(name):
        return os.environ[name]
    try:
        with open(CRED_FILE) as fh:
            for line in fh:
                if line.startswith(name + "="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return ""


def flat(v):
    """Reference fields arrive as {display_value, link} when sysparm_display_value=true."""
    return v.get("display_value", "") if isinstance(v, dict) else v


def strip_html(s, max_chars):
    if not s:
        return ""
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>|</h\d>|</tr>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\xa0]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s).strip()
    if len(s) > max_chars:
        s = s[:max_chars].rstrip() + f" …[truncated, {len(s)} chars total]"
    return s


def get(base, key, path, params, raw=False):
    url = f"{base}{path}?{urllib.parse.urlencode(params, safe='^=,:')}"
    req = urllib.request.Request(url, headers={"x-api-key": key, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:600]
        hint = ""
        if e.code == 401:
            hint = " (bad/missing x-api-key, or the API product doesn't authorize this path)"
        elif e.code == 403:
            hint = " (ServiceNow ACL denied the read for the proxy's service account)"
        sys.exit(f"HTTP {e.code} from {path}{hint}\n{body}")
    except urllib.error.URLError as e:
        sys.exit(f"Request failed: {e.reason}")
    if raw:
        print(body)
        sys.exit(0)
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        sys.exit(f"Non-JSON response from {path}:\n{body[:600]}")


def env_kbs():
    return [k for k in os.environ.get("SNOW_KB_SECURITY_KBS", "").split(",") if k.strip()]


def kb_scope_query(kbs):
    if not kbs:
        return ""
    parts = [f"kb_knowledge_base.title={k.strip()}" for k in kbs if k.strip()]
    return "^" + "^OR".join(parts)


def build_query(args, kbs):
    q = ["workflow_state=published", "active=true",
         f"valid_to>={date.today().isoformat()}^ORvalid_toISEMPTY"]
    q_str = "^".join(q) + kb_scope_query(kbs)
    if args.category:
        q_str += "^" + "^OR".join(f"kb_category.label={c.strip()}" for c in args.category)
    if args.since:
        q_str += f"^sys_updated_on>={args.since}"
    terms = " ".join(args.terms).strip()
    if terms:
        if not args.like:
            q_str += f"^123TEXTQUERY321={terms}"
        else:
            for w in terms.split():
                q_str += (f"^short_descriptionLIKE{w}^ORmeta_descriptionLIKE{w}"
                          f"^ORtextLIKE{w}^ORkb_categoryLIKE{w}")
    if not (terms and not args.like):  # full-text results are relevance-ranked; don't re-sort
        q_str += "^ORDERBYDESCpublished"
    return q_str


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("terms", nargs="*", help="search words (ANDed; each matched in title/summary/body/category)")
    p.add_argument("--kb", action="append", help="knowledge-base title to scope to (repeatable). Default: SNOW_KB_SECURITY_KBS")
    p.add_argument("--all-kbs", action="store_true", help="ignore the default KB scope")
    p.add_argument("--list-kbs", action="store_true", help="list knowledge bases with published-article counts")
    p.add_argument("--list-categories", action="store_true", help="list categories (within KB scope, filtered by terms) with article counts")
    p.add_argument("--id", help="fetch one article by KB number (KB00…) or sys_id, with body")
    p.add_argument("--full", action="store_true", help="include the article body (HTML stripped)")
    p.add_argument("--like", action="store_true", help="AND-match each word in title/summary/body/category instead of ServiceNow full-text search (default)")
    p.add_argument("--category", action="append", help="kb_category label to scope to (repeatable), e.g. 'Information Security'")
    p.add_argument("--since", help="only articles updated on/after YYYY-MM-DD")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--max-chars", type=int, default=6000, help="truncate stripped body to this many chars")
    p.add_argument("--env", choices=URLS, default=None, help="prod (default), stage, or dev (stale test clone)")
    p.add_argument("--raw", action="store_true", help="print the raw proxy response")
    p.add_argument("--show-query", action="store_true", help="print the sysparm_query to stderr")
    args = p.parse_args()

    env = args.env or "prod"
    base = os.environ.get("SNOW_PROXY_URL") or URLS[env]
    key_var = "SNOW_PROXY_APIKEY_DEV" if env == "dev" else "SNOW_PROXY_APIKEY"
    key = read_cred(key_var) or (read_cred("SNOW_PROXY_APIKEY") if env == "dev" else "")
    if not key:
        sys.exit(f"{key_var} is not set. Add it to {CRED_FILE} (see ~/.claude/credentials.md) or export it.")

    if args.list_kbs:
        data = get(base, key, "/stats/kb_knowledge", {
            "sysparm_query": "workflow_state=published^active=true",
            "sysparm_count": "true",
            "sysparm_group_by": "kb_knowledge_base",
            "sysparm_display_value": "true",
        }, raw=args.raw)
        rows = []
        for r in data.get("result", []):
            gb = r.get("groupby_fields", [{}])[0]
            rows.append({"knowledge_base": gb.get("value", ""), "published_articles": int(r["stats"]["count"])})
        rows.sort(key=lambda r: -r["published_articles"])
        print(json.dumps(rows, indent=1))
        return

    if args.list_categories:
        kbs = [] if args.all_kbs else (args.kb or env_kbs() or DEFAULT_KBS)
        data = get(base, key, "/stats/kb_knowledge", {
            "sysparm_query": build_query(args, kbs),
            "sysparm_count": "true",
            "sysparm_group_by": "kb_knowledge_base,kb_category",
            "sysparm_display_value": "true",
        }, raw=args.raw)
        rows = []
        for r in data.get("result", []):
            gb = {g["field"]: g.get("value", "") for g in r.get("groupby_fields", [])}
            rows.append({"knowledge_base": gb.get("kb_knowledge_base", ""), "category": gb.get("kb_category", ""),
                         "articles": int(r["stats"]["count"])})
        rows.sort(key=lambda r: -r["articles"])
        print(json.dumps(rows, indent=1))
        return

    fields = list(BASE_FIELDS)
    if args.full or args.id:
        fields.append("text")

    if args.id:
        ident = args.id.strip()
        q = f"sys_id={ident}" if re.fullmatch(r"[0-9a-f]{32}", ident) else f"number={ident}"
        params = {"sysparm_query": q, "sysparm_limit": 1}
    else:
        kbs = [] if args.all_kbs else (args.kb or env_kbs() or DEFAULT_KBS)
        q = build_query(args, kbs)
        params = {"sysparm_query": q, "sysparm_limit": args.limit}
    if args.show_query:
        print(f"sysparm_query={q}", file=sys.stderr)
    params.update({"sysparm_fields": ",".join(fields), "sysparm_display_value": "true"})

    data = get(base, key, "/table/kb_knowledge", params, raw=args.raw)
    out = []
    for r in data.get("result", []):
        item = {k: flat(r.get(k, "")) for k in BASE_FIELDS}
        if args.id and not item["number"] and not re.fullmatch(r"[0-9a-f]{32}", args.id.strip()):
            item["number"] = args.id.strip()  # number is ACL-hidden on some records; we know what we asked for
        if "text" in r:
            item["text"] = strip_html(r.get("text", ""), args.max_chars)
            if not item["text"]:
                item["text_note"] = "body empty or not readable via the proxy account; open u_direct_url"
        out.append(item)
    print(json.dumps({"env": env, "count": len(out), "query": q, "results": out}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
