# ADR-0001: Use Microsoft Foundry (new) for models and agents

- Status: Accepted
- Date: 2026-10-08

## Context

The session showcases Microsoft Foundry and needs a live demo with an agent, tools, and two model deployments.
Microsoft offers two experiences: Foundry (new) — a Foundry resource with child projects, the Foundry SDK 2.x, and
Foundry Agent Service on the Responses API — and Foundry (classic), with hub-based projects, standalone Azure OpenAI
resources, and the Assistants API (sunset 26 August 2026). The
[ai-coding-standards](https://github.com/frkim/ai-coding-standards) (`standards/azure/azure.md` §8) require
Foundry (new) for all AI workloads, keyless access, and a region that supports the Responses API and Agent Service.

## Decision

- Provision a **Foundry resource** (`Microsoft.CognitiveServices/accounts`, kind `AIServices`,
  `allowProjectManagement: true`, `disableLocalAuth: true`) and a child **Foundry project** (`proj-foundrydemo-dev`)
  in `swedencentral` with Bicep.
- Deploy `gpt-5.4-mini` (agent, primary) and `gpt-5.4-nano` (fast/compare) as `GlobalStandard` deployments.
- In the API, use **`azure-ai-projects` 2.x**: `AIProjectClient` with `DefaultAzureCredential`,
  `agents.create_version()` with a `PromptAgentDefinition` for the `foundry-guide` agent, and the `openai` client from
  `project_client.get_openai_client()` on the **Responses API** with Foundry conversations.
- Grant the app's user-assigned managed identity **Azure AI User** on the Foundry resource; no API keys.

## Consequences

- Positive: the demo matches what the session teaches; agents, tools, conversations, tracing, and evaluations come from
  one resource; no keys to manage or leak.
- Positive: new Foundry capabilities (tool catalog, hosted agents, Control Plane) are available to extend the demo.
- Negative: Foundry (new) evolves quickly; SDK and API changes must be tracked (Dependabot, release notes).
- Negative: region choice is constrained by model, tool, and Agent Service availability.
- Follow-up: never copy samples from Foundry (classic) docs (`/azure/foundry-classic/`); keep SDK majors consistent.

## Alternatives considered

- **Foundry (classic) hub-based project** — rejected: not allowed by the standards, no new features.
- **Standalone Azure OpenAI resource with `AzureOpenAI()`** — rejected: classic pattern, no Agent Service.
- **Assistants API (threads and runs)** — rejected: being retired; replaced by the Responses API.
- **`azure-ai-inference`** — rejected: superseded by the Foundry SDK 2.x and the OpenAI client.
