## What and why

<!-- What changed and why. Link the issue: Closes #123 -->

## How it was verified

<!-- Commands you ran and what you observed (tests, local run, screenshots, deployment). -->

## Risk and follow-up

<!-- Anything reviewers should watch, rollback notes, follow-up issues. -->

## Checklist

- [ ] Title follows [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `ci:`, ...).
- [ ] Quality gates pass locally: `uv run ruff check`, `uv run mypy`, `uv run pytest` (`src/api`);
      `npm ci && npm run build` (`src/web`, `docs/presentations`); `az bicep lint --file infra/main.bicep`.
- [ ] Tests added or updated for the behaviour change, and the feature was exercised manually.
- [ ] Microsoft Foundry (new) only — no Assistants API, `azure-ai-inference`, `AzureOpenAI()`, hub projects, or API keys.
- [ ] Keyless access (managed identity / OIDC); no secrets, keys, tokens, or real `.env` committed.
- [ ] Packages resolve only from the Microsoft-protected feeds; lock files committed and their URLs checked.
- [ ] GitHub Actions pinned to full commit SHAs with least-privilege `permissions`.
- [ ] UI changes keep the dark/light toggle and table sort/filter/pagination/search behaviour.
- [ ] Documentation (README, AGENTS.md, session docs) updated; diagrams in Mermaid.
- [ ] New preview features or standards exceptions recorded as an ADR in `docs/adr/`.
- [ ] Throwaway scripts kept in the git-ignored `tmp/scripts/` folder.
