---
name: jira-adf-task-lists
description: Editing Jira descriptions via Atlassian MCP with markdown breaks interactive checkboxes — use ADF taskList nodes
metadata:
  type: feedback
---

Editing a Jira issue description through the Atlassian MCP (`editJiraIssue`) with
`contentFormat: "markdown"` converts interactive task-list checkboxes into literal
escaped text (`\[x\]` bullets) — the checklist stops being clickable in the Jira UI.

**Why:** Jira stores descriptions as ADF; markdown round-tripping has no mapping to
the `taskList`/`taskItem` node types, so `- [ ]` degrades to a plain bullet with
escaped brackets.

**How to apply:** when an issue description contains checkboxes, edit with
`contentFormat: "adf"` and build `taskList` → `taskItem` nodes (each needs a
`localId`; `state` is `"TODO"`/`"DONE"`). Inline marks (link, strike) go on the text
nodes inside the taskItem. Plain-markdown editing is fine for comments and
checkbox-free descriptions. (Hit 2026-08-02 on AAIS-540; fixed by re-writing the
description in ADF.)
