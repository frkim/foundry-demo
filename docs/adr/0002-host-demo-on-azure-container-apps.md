# ADR-0002: Host the demo on Azure Container Apps

- Status: Accepted
- Date: 2026-10-08

## Context

The demo app (FastAPI backend serving a Vue 3 SPA) must be reachable over HTTPS during the session, cost almost
nothing between sessions, deploy from GitHub Actions, and call Foundry without secrets. The standards prefer the
smallest SKU that meets the requirement and user-assigned managed identities.

## Decision

- Build one container image (`src/Dockerfile`, multi-stage: Node builds the SPA, Python 3.13 serves API + static
  files on port 8000) and push it to **Azure Container Registry** (Basic, admin user disabled).
- Run it on **Azure Container Apps** in a **consumption** environment (`cae-foundrydemo-dev`) with HTTPS ingress,
  liveness probe `/health/live`, and readiness probe `/health/ready`.
- Attach a **user-assigned managed identity** (`id-foundrydemo-dev`) used both to pull images (**AcrPull** on the
  registry) and to call Foundry (**Azure AI User** on the Foundry resource). The app reads `AZURE_CLIENT_ID` and uses
  `DefaultAzureCredential` — fully keyless.
- Send logs and telemetry to Log Analytics and a workspace-based Application Insights instance.

## Consequences

- Positive: scale-to-zero consumption pricing; managed TLS and revisions; no registry passwords or API keys.
- Positive: one image keeps the SPA and API on the same origin (no CORS).
- Negative: cold starts after idle periods — warm the app before the session (see the demo runbook).
- Negative: the UAMI must exist and hold AcrPull before the first image pull; Bicep orders the role assignments.
- Follow-up: a production variant would add a WAF (Front Door), private networking, and Entra ID sign-in.

## Alternatives considered

- **Azure App Service** — viable, but no scale to zero and a fixed plan cost.
- **Azure Static Web Apps + Functions** — splits the app in two and complicates long-running agent calls.
- **AKS** — far more than a single demo container needs.
- **Foundry hosted agents only** — would hide the application code the session wants to show.
