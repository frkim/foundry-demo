# ADR-0004: Use of preview and fast-moving capabilities

- Status: Accepted
- Date: 2026-10-08
- Review: before every delivery of the session

## Context

The standards (`standards/azure/azure.md` §8, compliance item AI-05) prefer generally available capabilities and
require an ADR for each preview feature in use. The session's purpose is to show the latest Microsoft Foundry
capabilities, so the demo deliberately relies on features that are in preview or were released recently, whose
behaviour, regional availability, quotas, and SDK surface can change without notice. Preview features have no SLA
and are not recommended for production.

## Decision

The demo uses the following capabilities. Check their status on Microsoft Learn before each session:

| Capability | Where | Risk | Fallback |
| --- | --- | --- | --- |
| **MCP tool** in Foundry Agent Service (remote Microsoft Learn MCP server) | `foundry-guide` agent | Tool schema or approval behaviour changes; server unavailable | Agent still answers from the model; recorded demo video; see [ADR-0005](0005-mcp-tool-microsoft-learn.md) |
| **Code Interpreter tool** | `foundry-guide` agent | Regional/model availability; extra per-session charges | Remove the tool from the agent definition; show the recorded segment |
| **`gpt-5.4-mini` / `gpt-5.4-nano`** (version `2026-03-17`, `GlobalStandard`) | Model deployments | Newest model family: regional availability, quota, and version retirement | Change `FOUNDRY_MODEL_DEPLOYMENT` / `FOUNDRY_FAST_MODEL_DEPLOYMENT` and the Bicep parameters to another available GA model |
| **Foundry SDK 2.x / Agent Service on the Responses API** | `src/api` | Breaking changes between minor versions | Pin versions in `uv.lock`; Dependabot pull requests reviewed and tested before merge |

Rules:

- The app must **start and serve** even if the agent cannot be created — `/health/ready` reports the agent status
  and the model comparison keeps working.
- No preview feature is used for anything that stores or changes data; the demo handles public data only.
- Preview-only features that are **not** used (for example long-running MCP operations, multi-agent workflows,
  agent memory) are shown on slides only.

## Consequences

- Positive: the audience sees current capabilities running for real.
- Negative: a service change can break the live demo — mitigated by the dry run in the demo runbook, the recorded
  video in `docs/video/`, and the fallbacks above.
- Follow-up: when a capability reaches GA or is retired, update this table and the deck.

## Alternatives considered

- **GA-only demo** — rejected: would not show the agent/tool scenarios the session is about.
- **Mock the agent locally** — rejected for the live demo; acceptable only for unit tests.
