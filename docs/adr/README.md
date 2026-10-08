# Architecture decision records

This folder holds the architecture decision records (ADRs) for this repository, written in a lightweight
[MADR](https://adr.github.io/madr/) style: status, date, context, decision, consequences, and alternatives
considered. Exceptions to the [ai-coding-standards](https://github.com/frkim/ai-coding-standards) carry an expiry
date.

| ADR | Title | Status | Date |
| --- | --- | --- | --- |
| [0001](0001-use-microsoft-foundry-new.md) | Use Microsoft Foundry (new) for models and agents | Accepted | 2026-10-08 |
| [0002](0002-host-demo-on-azure-container-apps.md) | Host the demo on Azure Container Apps | Accepted | 2026-10-08 |
| [0003](0003-github-actions-azure-auth-exception.md) | Exception — service principal secret fallback for GitHub Actions to Azure | Accepted (exception, expires 2026-12-31) | 2026-10-08 |
| [0004](0004-preview-features.md) | Use of preview and fast-moving capabilities | Accepted | 2026-10-08 |
| [0005](0005-mcp-tool-microsoft-learn.md) | Give the agent the public Microsoft Learn MCP server | Accepted | 2026-10-08 |

## Adding an ADR

1. Copy the structure of an existing ADR into `NNNN-short-title.md` using the next number.
2. Set `Status: Proposed`, open a pull request, and change it to `Accepted` when merged.
3. Never rewrite an accepted ADR's decision — supersede it with a new ADR and update both statuses.
4. Add the ADR to the table above.
