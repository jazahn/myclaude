# Push Apigee Proxy Artifact

Zip and deploy a local Apigee proxy bundle as a new revision, deploy it to the target environment, wait for it to become READY, then smoke-test that the deployed proxy responds.

## Arguments
- $ARGUMENTS: Optional. Format: `proxy-name [environment]`.
  - If `proxy-name` is omitted, infer it: if a single `*/apiproxy/` directory exists in the project, use that directory's name; otherwise ask which proxy to push.
  - If `environment` is omitted, default to `dev`.

## Prerequisites
- `gcloud` authenticated against the org that hosts the proxy (`$(gcloud config get-value project)`). Confirm it's the intended org before deploying.
- A local `{proxy-name}/apiproxy/` directory (e.g. produced by the `apigee-pull` command).

## Steps

1. Verify gcloud authentication by running `gcloud auth print-access-token` (just check it doesn't error).
2. Determine the proxy name (per Arguments) and environment (default `dev`).
3. Verify the local directory `./{proxy-name}/apiproxy/` exists.
4. **Read the deployed base path from the bundle** so the smoke test targets the right URL:
   the `<BasePath>` element in `{proxy-name}/apiproxy/proxies/*.xml` (e.g. via
   `grep -h "<BasePath>" {proxy-name}/apiproxy/proxies/*.xml`). Call this `{base-path}`.
5. Create the zip bundle from the proxy directory:
   ```
   cd {proxy-name} && zip -r ../{proxy-name}-upload.zip apiproxy/ && cd ..
   ```
6. Upload as a new revision (multipart form upload):
   ```
   curl -s -X POST \
     -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     -F "file=@{proxy-name}-upload.zip" \
     "https://apigee.googleapis.com/v1/organizations/$(gcloud config get-value project)/apis?action=import&name={proxy-name}"
   ```
   - If the response is an error (e.g. `bundle contains errors`), print it and stop — do not deploy.
7. Parse the new revision number from the upload response.
8. Deploy the new revision to the target environment:
   ```
   curl -s -X POST \
     -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     "https://apigee.googleapis.com/v1/organizations/$(gcloud config get-value project)/environments/{environment}/apis/{proxy-name}/revisions/{new-rev}/deployments?override=true"
   ```
9. Report the new revision number and deployment status.
10. **Poll for deployment readiness** — loop up to 12 times (every 10 seconds, ~2 minutes max):
    ```
    curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" \
      "https://apigee.googleapis.com/v1/organizations/$(gcloud config get-value project)/environments/{environment}/apis/{proxy-name}/revisions/{new-rev}/deployments"
    ```
    - Success when the response shows `"state": "READY"` (or all instances ready).
    - If not ready yet, wait 10 seconds and retry. If still not ready after all retries, warn but continue to the test step.
11. **Smoke-test the deployment** — confirm the proxy is reachable on its base path.
    - Determine the gateway host from the environment. Default mapping (HUIT ADEX gateway —
      override if this org uses a different gateway/virtual host):
      `dev` → `go.dev.apis.huit.harvard.edu`, `test` → `go.stage.apis.huit.harvard.edu`,
      `stage` → `go.stage.apis.huit.harvard.edu`, `prod` → `go.prod.apis.huit.harvard.edu`.
    - Call the base path:
      ```
      curl -s -o /dev/null -w "%{http_code}" \
        "https://{gateway-host}{base-path}/"
      ```
    - Interpreting the status (the proxy is reachable as long as it isn't a gateway/404 miss):
      - **Any HTTP status that isn't a routing miss** (e.g. 200, 401, 403, 405, even a backend 5xx) means the proxy is deployed and routing — report success with the code.
      - **404 from the gateway** (no such base path) means the proxy isn't deployed at that path — treat as failure and surface it.
      - If the request fails to connect or returns 5xx, retry up to 3 times with 5-second waits.
    - If the project documents specific routes/expected statuses (e.g. in a project command or
      README), prefer those assertions over the generic base-path check.
    - Report the final test result (status code, and response body if it failed).
12. **Archive the proxy bundle** — zip the `{proxy-name}` directory into `{proxy-name}/{proxy-name}.zip` (overwriting any existing zip):
    ```
    zip -r {proxy-name}/{proxy-name}.zip {proxy-name}/apiproxy/
    ```
13. Clean up the upload zip file.
