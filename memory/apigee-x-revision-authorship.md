---
name: apigee-x-revision-authorship
description: Apigee X records no author on proxy revisions; attribution needs GCP audit logs (400-day retention) which jcleveng's account cannot read on the HUIT apigee-x-* projects
metadata:
  type: project
---

Apigee X revision metadata (`GET /organizations/{org}/apis/{proxy}/revisions/{n}`)
has only `createdAt` and `lastModifiedAt`; no creator or modifier, unlike Edge, whose
exports carried `CreatedBy`/`LastModifiedBy`. The only record of who changed a proxy
is the GCP Admin Activity audit log on the org's project (`apigee-x-nonprod-406719`,
`apigee-x-preprod`, `apigee-x-prod-406719`), fields
`protoPayload.authenticationInfo.principalEmail` and `protoPayload.methodName`
(`CreateApiProxy`, `UpdateApiProxyRevision`, `DeployApiProxyRevision`).

**Why:** checked 2026-10-08 for ats-course-v2. `gcloud logging read` on the nonprod
project returned PERMISSION_DENIED for all log views, and `logging.sinks.list` was
denied too. Admin Activity logs are kept 400 days, non-configurable, so anything older
is gone unless the Apigee platform team exports to a sink.

**How to apply:** don't spend time on audit logs from this account; ask the HUIT
Apigee platform team with the project id and the query above, or ask the likely
people directly. What this account *can* do is download every revision bundle
(`?format=bundle`) and diff them to build a timeline of when each change first
appeared, which narrows the window. Downloading revisions is cheap; a loop over 25
revisions takes under a minute. See also [[harvard-vpn-google-oauth-youtube-block]]
for the login side.
