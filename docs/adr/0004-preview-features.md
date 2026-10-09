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

**Demo 3 (session demos only — not used by the app).** [Demo 3](../session/demo-runbook.md#demo-3--foundry-capabilities-ten-short-demos)
shows these preview capabilities live on separate `demo-*` agents in the same project:

| Capability | Demo | Fallback |
| --- | --- | --- |
| Connecting a Foundry IQ knowledge base to an agent; non-index knowledge sources; portal knowledge flow | 3.1 | Pre-created agent; rehearsal screenshots |
| Incoming A2A endpoint on a Foundry agent (`agents.update_details`, SDK/REST only) | 3.2 | Show MCP catalog flow and the agent card |
| Agent guardrails; tool-call and tool-response intervention points; task adherence | 3.4 | Jailbreak at user input (GA) only |
| Skills (`project.beta.skills`), tool search | 3.5 | Toolbox (GA) without skills |
| Routines (`project.beta.routines`) — status to confirm on Learn; Durable Task extension for Agent Framework (`agent-framework-durabletask`, pre-release) | 3.6, 3.10 | Slides and code walk-through |
| Agent monitoring dashboard, continuous evaluation rules, alerts | 3.7 | Traces (GA) and KQL |
| Agent Optimizer (limited preview); some agent evaluators | 3.8 | Evaluation run (GA) and Prompt Optimizer |
| Trace-based evaluation of LangGraph agents; Azure Monitor **Agents** view | 3.9 | Traces in Application Insights |

Live-test status (October 2026, Sweden Central, `azure-ai-projects` 2.8): the SDK/REST paths for 3.1–3.3, 3.5, 3.6
(background responses and creating a routine), 3.7 (continuous evaluation rule and KQL), 3.8 (evaluation run), 3.9 and
3.10 (MCP approval and Agent Framework approval) were run end to end. **Not run (portal-only or limited preview):**
the tool-response guardrail intervention point, Agent Optimizer, Prompt Optimizer, the Monitor dashboard and alerts,
hosted-agent deployment and the Durable Task extension — these stay marked **[verify]** in the runbook.
Provisioning prerequisites discovered live (RBAC roles, ARM-created connections) are in the runbook's Demo 3 setup.

Rules:

- The app must **start and serve** even if the agent cannot be created — `/health/ready` reports the agent status
  and the model comparison keeps working.
- No preview feature is used for anything that stores or changes data; the demo handles public data only.
- Preview-only features that are **not** used by the app (for example long-running MCP operations, multi-agent
  workflows, agent memory) are shown on slides only, or in Demo 3 on `demo-*` agents with public, fictional data —
  never on the app's `foundry-guide` agent.

## Consequences

- Positive: the audience sees current capabilities running for real.
- Negative: a service change can break the live demo — mitigated by the dry run in the demo runbook, the recorded
  video in `docs/video/`, and the fallbacks above.
- Follow-up: when a capability reaches GA or is retired, update this table and the deck.

## Alternatives considered

- **GA-only demo** — rejected: would not show the agent/tool scenarios the session is about.
- **Mock the agent locally** — rejected for the live demo; acceptable only for unit tests.
