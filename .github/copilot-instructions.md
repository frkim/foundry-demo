# Copilot instructions

This repository is a Microsoft Foundry session kit: a Marp deck, a session narrative, a demo video, and the
**Foundry Guide** demo app (Python 3.13 FastAPI + Vue 3/Vuetify SPA) deployed to Azure Container Apps with Bicep and
GitHub Actions.

**Read [`AGENTS.md`](../AGENTS.md) first** — it is the authoritative agent contract for this repository (setup,
commands, structure, non-negotiables, gotchas). It follows the
[ai-coding-standards](https://github.com/frkim/ai-coding-standards) repository, which wins on any conflict.

Key rules, in short:

- Microsoft Foundry (new) only: Foundry resource + project, `azure-ai-projects` 2.x, Responses API. Never the
  Assistants API, `azure-ai-inference`, `AzureOpenAI()`, hub-based projects, or API keys.
- Keyless Azure access with a managed identity and `DefaultAzureCredential`; never commit secrets.
- Install packages only from the Microsoft-protected feeds (`packagefeedproxy.microsoft.io`); never point
  configuration or lockfiles at a public registry.
- Throwaway scripts go in the git-ignored `tmp/scripts/` folder.
- Conventional Commits; Mermaid diagrams; record exceptions and preview features as ADRs in `docs/adr/`.
- Run `uv run ruff check`, `uv run mypy`, `uv run pytest` (in `src/api`) and `npm run build` (in `src/web`) before
  saying the work is done, and report what you ran.
