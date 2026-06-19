# Pull Apigee Proxy Artifact

Pull the latest (or specified) revision of an Apigee proxy bundle, unzip it, and make it ready for editing. Also pulls the associated API product.

## Arguments
- $ARGUMENTS: Optional. Format: `proxy-name [revision]`.
  - If `proxy-name` is omitted, infer it: if a single `*/apiproxy/` directory already exists in the project, use that directory's name; otherwise ask the user which proxy to pull.
  - If `revision` is omitted, use the latest.

## Prerequisites
- `gcloud` authenticated against the org that hosts the proxy. The org is `$(gcloud config get-value project)` — confirm it's the intended one before pulling.

## Steps

1. Verify gcloud authentication by running `gcloud auth print-access-token` (just check it doesn't error).
2. Determine the proxy name (per Arguments) and revision:
   - If no revision specified, look up the latest with `gcloud apigee apis describe {proxy-name} --format=json` and use `latestRevisionId`.
3. Download the bundle:
   ```
   curl -s -o {proxy-name}-rev{rev}.zip \
     -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     "https://apigee.googleapis.com/v1/organizations/$(gcloud config get-value project)/apis/{proxy-name}/revisions/{rev}?format=bundle"
   ```
4. Remove the old unzipped directory if it exists, then unzip into `./{proxy-name}/`.
5. Pull the associated API product and save it alongside the bundle:
   ```
   curl -s -H "Authorization: Bearer $(gcloud auth print-access-token)" \
     "https://apigee.googleapis.com/v1/organizations/$(gcloud config get-value project)/apiproducts/{proxy-name}" \
     | python3 -m json.tool > {proxy-name}/{proxy-name}-product.json
   ```
   - Products are named after the proxy by convention. If that 404s or the product name differs, list products with `curl .../apiproducts` and find the one whose `operationGroup.operationConfigs[].apiSource` references `{proxy-name}`. If none match, note that no product was found and continue.
6. Report what was downloaded (proxy revision + product) and show the file structure.
