# Contributing

Thanks for your interest in improving this Microsoft Foundry session kit. This repository follows the
[ai-coding-standards](https://github.com/frkim/ai-coding-standards); [`AGENTS.md`](AGENTS.md) summarises the rules
that apply here.

## Before you start

- Open an issue (bug or feature) to discuss the change, unless it is a small fix.
- Install Python 3.13, [`uv`](https://docs.astral.sh/uv/), Node.js 24 LTS, and the Azure CLI with Bicep.
- Keep the committed package feed configuration (Microsoft-protected PyPI and npm feeds) — do not point it at a
  public registry.

## Workflow

1. Branch from `main`: `feature/<issue>-<slug>`, `fix/<issue>-<slug>`, or `chore/<slug>`.
2. Make small, focused commits using [Conventional Commits](https://www.conventionalcommits.org/)
   (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`, `ci:`, `perf:`).
3. Add or update tests with every behaviour change; bug fixes start with a failing regression test.
4. Update the documentation (README, ADRs, session docs) in the same pull request.
5. Run the quality gates locally:

   ```bash
   # backend
   cd src/api
   uv run ruff check
   uv run mypy
   uv run pytest

   # frontend
   cd ../web
   npm ci && npm run build

   # slide deck
   cd ../../docs/presentations
   npm ci && npm run build

   # infrastructure (from the repository root)
   az bicep lint --file infra/main.bicep
   ```

6. Open a pull request, fill in the template, and link the issue (`Closes #123`). CI must be green and a code owner
   must approve before the pull request is squash merged.

## Rules worth repeating

- Microsoft Foundry (new) only — see [ADR-0001](docs/adr/0001-use-microsoft-foundry-new.md).
- Never commit secrets, keys, connection strings, or a real `.env` file. Use [`.env.example`](.env.example).
- Scratch scripts go in the git-ignored `tmp/scripts/` folder.
- Diagrams are Mermaid; slides are Marp Markdown.
- Significant decisions, exceptions, and preview features get an ADR in [`docs/adr/`](docs/adr/README.md).

## Reporting security issues

Do not open a public issue. Follow [`SECURITY.md`](SECURITY.md).
