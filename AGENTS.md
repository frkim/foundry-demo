# AGENTS.md

This file is the contract every AI coding agent (GitHub Copilot coding agent, Copilot CLI, Copilot in the IDE, and
others) reads before working in this repository. It follows the
[ai-coding-standards](https://github.com/frkim/ai-coding-standards) `templates/AGENTS.md` template.

## Project overview

`foundry-demo` is a 90-minute session kit about **Microsoft Foundry**: a Marp slide deck, a timed narrative, a demo
video, and a live demo app called **Foundry Guide**. Foundry Guide is a FastAPI backend plus a Vue 3 single-page app
that calls a Foundry agent (`foundry-guide`) with the Microsoft Learn MCP server and Code Interpreter tools, compares
two model deployments side by side, and shows run history. The app is deployed to Azure Container Apps with Bicep and
GitHub Actions, authenticating keylessly with a user-assigned managed identity.

- **Frontend**: Vue 3 + Vuetify 3 (Material Design) + Vite, TypeScript
- **Backend**: Python 3.13 FastAPI, managed with `uv`
- **AI**: Microsoft Foundry (new) — Foundry resource + project, `azure-ai-projects` 2.x, Responses API
- **Data**: none (run history is kept in memory, last 200 runs)
- **Hosting**: Azure Container Apps (consumption), Azure Container Registry, Application Insights
- **Infrastructure**: Bicep at subscription scope (`infra/`)
- **Presentations**: Marp Markdown (`docs/presentations/`)
- **CI/CD**: GitHub Actions (`ci.yml`, `deploy.yml`, `deck.yml`)

## Setup

```bash
# prerequisites: Python 3.13, uv, Node.js 24 LTS, Azure CLI (with Bicep)
cd src/api && uv sync
cd ../web && npm ci
cd ../../docs/presentations && npm ci
```

Package feeds are configured in the repository and **must not be changed** (Microsoft CISO policy):

- PyPI: `https://packagefeedproxy.microsoft.io/pypi/simple` (committed `uv` index configuration in `src/api`)
- npm: `https://packagefeedproxy.microsoft.io/npm/` (committed `.npmrc` in `src/web` and `docs/presentations`)
- NuGet (if ever needed): `https://packagefeedproxy.microsoft.io/nuget/v3/index.json`

Never reference the public PyPI or NuGet registries in configuration, Dockerfiles, CI, or lockfiles. Lockfile
`resolved` URLs must point at the protected feed. If a package is missing from the feed, stop and ask for the CFS
exception process — do not fall back to a public registry.

## Commands

| Task | Folder | Command |
| --- | --- | --- |
| Run API locally | `src/api` | `uv run uvicorn foundry_demo.main:app --reload --port 8000` |
| Run web locally | `src/web` | `npm run dev` |
| Lint (Python) | `src/api` | `uv run ruff check` |
| Type check (Python) | `src/api` | `uv run mypy` |
| Test (Python) | `src/api` | `uv run pytest` |
| Build web | `src/web` | `npm ci && npm run build` |
| Build deck | `docs/presentations` | `npm ci && npm run build:all` |
| Lint infrastructure | repository root | `az bicep lint --file infra/main.bicep` |
| Build infrastructure | repository root | `az bicep build --file infra/main.bicep` |
| Deploy | GitHub Actions | `deploy.yml` (push to `main` or manual dispatch) |

Copy `.env.example` to `src/api/.env` (git-ignored) and fill in the values before running the API locally.

## Project structure

```text
src/api/             Python 3.13 FastAPI backend (uv project, tests in src/api/tests/)
src/web/             Vue 3 + Vuetify 3 + Vite SPA
src/Dockerfile       multi-stage image: builds the SPA, serves it from the API
infra/               Bicep (main.bicep at subscription scope, modules/, main.dev.bicepparam)
.github/workflows/   ci.yml, deploy.yml, deck.yml
docs/presentations/  Marp deck
docs/session/        narrative, demo runbook, Q&A prep
docs/adr/            architecture decision records
docs/video/          demo video and subtitles
scripts/video/       reproducible video pipeline
tmp/scripts/         throwaway agent/developer scripts (git-ignored)
```

## Standards to follow

The [ai-coding-standards](https://github.com/frkim/ai-coding-standards) repository is authoritative:

- Coding: `instructions/coding-standards.instructions.md`
- Security: `instructions/security.instructions.md` and `standards/security/security.md`
- Testing: `instructions/testing.instructions.md`
- Documentation: `instructions/documentation.instructions.md`
- Architecture and UI: `instructions/architecture.instructions.md`
- Azure: `standards/azure/azure.md` · GitHub: `standards/github/github.md`

## Non-negotiables

- **Microsoft Foundry (new) only.** Use a Foundry resource (`Microsoft.CognitiveServices/accounts`, kind
  `AIServices`, `allowProjectManagement: true`) with child Foundry projects, `azure-ai-projects` 2.x
  (`agents.create_version()` + `PromptAgentDefinition`), and the `openai` client from
  `project_client.get_openai_client()` on the **Responses API**. Never use the Assistants API (`create_agent()`,
  threads, runs), `azure-ai-inference`, `AzureOpenAI()` with an `api-version`, hub-based projects, or Foundry
  (classic) samples.
- **Keyless.** `disableLocalAuth: true` on the Foundry resource; the app uses a user-assigned managed identity via
  `DefaultAzureCredential` (`AZURE_CLIENT_ID`). Never commit or log secrets, keys, tokens, or connection strings.
- **Protected package feeds** for PyPI and npm (see [Setup](#setup)), including inside the Dockerfile and CI.
- Every UI has a **dark/light mode toggle** that respects the OS preference and persists the choice.
- Every data table supports **sorting, column filtering, pagination, and a global search box**.
- Validate all input at the boundary; return errors without stack traces.
- Before adding a library, SDK, or runtime, **research its current stable version online** and use it.
- Prefer the **smallest Azure SKU** that meets the requirement.
- Diagrams are [Mermaid](https://mermaid.js.org/), presentations are [Marp](https://marp.app/) Markdown.
- Throwaway implementation or troubleshooting scripts go in the git-ignored `tmp/scripts/` folder — never in the
  repository tree. Move a script to `scripts/` only when it becomes part of a documented workflow.
- Every preview feature and every exception to the standards is recorded in an ADR under `docs/adr/`.
- **When you implement a feature, test it** — run the tests and exercise the feature, then report what you observed.
- Update documentation in the same pull request as the code.

## Pull requests

- Conventional Commit titles (`feat:`, `fix:`, `docs:`, `ci:`, `chore:`, ...), squash merge.
- Describe what changed, why, and how it was verified; complete the checklist in the pull request template.
- CI (lint, type check, build, test, Bicep lint) must be green before merge.

## Gotchas

- The agent `foundry-guide` is created idempotently at API startup; a failure must not crash the app —
  `/health/ready` returns `503` until configuration is present and the agent is ready.
- Model deployments `gpt-5.4-mini` (agent) and `gpt-5.4-nano` (fast/compare) must exist in the Foundry resource and
  are deployed sequentially by Bicep.
- The Foundry resource must be in a region that supports the Responses API and Foundry Agent Service
  (default `swedencentral`).
- `infra/main.bicep` targets the **subscription** scope: use `az deployment sub`, not `az deployment group`.
- The deploy workflow temporarily falls back to a service principal secret when OIDC is not configured — see
  [ADR-0003](docs/adr/0003-github-actions-azure-auth-exception.md) (expires 2026-12-31).
- Preview capabilities in use are tracked in [ADR-0004](docs/adr/0004-preview-features.md).
