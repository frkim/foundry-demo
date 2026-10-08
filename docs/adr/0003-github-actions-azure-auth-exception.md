# ADR-0003: Exception — service principal secret fallback for GitHub Actions to Azure

- Status: Accepted (exception)
- Date: 2026-10-08
- **Expires: 2026-12-31**
- Owner: @frkim

## Context

The standards (`standards/security/security.md` §1, `standards/github/github.md` §5) require GitHub Actions to
authenticate to Azure with **workload identity federation (OIDC)** and forbid stored Azure credentials; a service
principal secret needs a documented exception with an expiry date.

The service principal used to deploy this repository lacks the Microsoft Graph permission needed to add a federated
identity credential to its own app registration, and the tenant administrator who can add it is not available before
the session. A working deployment is required now.

## Decision

The deploy workflow (`.github/workflows/deploy.yml`) supports both modes:

1. **OIDC (preferred)** — when the repository variable `AZURE_CLIENT_ID` is set, `azure/login` uses `client-id`,
   `tenant-id`, and `subscription-id` from the variables `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and
   `AZURE_SUBSCRIPTION_ID`, with job-level `id-token: write`.
2. **Fallback (this exception)** — otherwise, `azure/login` uses the `AZURE_CREDENTIALS` secret (a JSON service
   principal client secret).

This exception applies **only** to the deployment identity. The running application stays keyless (managed identity).

### Mitigations

- The secret is stored **only** as a GitHub encrypted repository/environment secret — never in code, logs, or docs.
- The service principal is scoped to the demo subscription/resource group with the minimum roles required to deploy
  the Bicep template and assign the app's roles; it holds no other access.
- The client secret has a lifetime of at most 90 days, ending no later than this ADR's expiry, and is rotated
  immediately on any suspicion of leakage.
- Workflow permissions stay at `contents: read`; the deploy job runs only on `main` / manual dispatch, never on
  pull requests from forks.
- Secret scanning with push protection is enabled on the repository.

## Migration to OIDC (required before 2026-12-31)

An administrator with permission on the app registration runs (replace `<app-id>` with the service principal's
application (client) ID):

```bash
az ad app federated-credential create --id <app-id> --parameters '{
  "name": "github-foundry-demo-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:frkim/foundry-demo:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'

# Needed when the deploy job declares `environment: dev`
az ad app federated-credential create --id <app-id> --parameters '{
  "name": "github-foundry-demo-env-dev",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:frkim/foundry-demo:environment:dev",
  "audiences": ["api://AzureADTokenExchange"]
}'
```

Then:

1. Set the repository variables `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID`.
2. Run the deploy workflow and confirm it logs in with OIDC.
3. Delete the `AZURE_CREDENTIALS` secret, remove the client secret from the app registration
   (`az ad app credential delete`), and remove the fallback branch from `deploy.yml`.
4. Mark this ADR **Superseded**.

## Consequences

- Positive: the demo can be deployed today; switching to OIDC needs no workflow change — only setting variables.
- Negative: a long-lived credential exists until migration; compliance item CI-09 / SEC-02 is reported as
  `Exception` until then.

## Alternatives considered

- **Wait for OIDC before deploying** — rejected: blocks the session.
- **Deploy manually from a laptop** — rejected: violates "deploy only through CI" and is not reproducible.
- **User-assigned managed identity with a federated credential** — avoids the Graph permission (the federated
  credential is an Azure Resource Manager child resource), but needs a subscription owner to create the identity and
  grant it the deployment roles. It is an acceptable alternative migration target if the app registration route
  stays blocked.
