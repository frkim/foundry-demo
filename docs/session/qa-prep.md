# Q&A preparation

Anticipated questions with crisp answers. Each answer is grounded in the session research brief (sources listed);
**⚠ Uncertain** marks anything you must not state as fact without re-checking Microsoft Learn on the day.

**Answering rules:** repeat the question; answer in ≤ 45 seconds; say the GA/preview label; never guess a price, date,
or region list — offer to follow up.

## Index

| # | Topic | Question |
| --- | --- | --- |
| 1 | Platform | Is Microsoft Foundry just a rename of Azure AI Foundry? |
| 2 | Platform | What's the difference between a Foundry resource and a Foundry project? |
| 3 | Migration | We use hub-based projects. Do we have to migrate, and what moves? |
| 4 | Migration | When does the Assistants API / classic Agent Service retire? |
| 5 | Agents | Prompt agents vs hosted agents — which should I use? |
| 6 | Agents | Agent Framework vs Semantic Kernel vs AutoGen? |
| 7 | Agents | Should we use Foundry Workflows for multi-agent orchestration? |
| 8 | Agents | Is agent memory production-ready? |
| 9 | Agents | What is A2A and is it GA? |
| 10 | Security | How do you secure MCP tools? |
| 11 | Security | How does authentication work — any API keys? |
| 12 | Security | Can Foundry run on private networking? |
| 13 | Data | Where is my data processed — data residency? |
| 14 | Cost | What's the pricing model? |
| 15 | Cost | How do we control cost? |
| 16 | Capacity | How do quotas work and what happens when we hit them? |
| 17 | Quality | How do we evaluate agents? |
| 18 | Safety | What responsible AI / safety controls exist? |
| 19 | Gateway | APIM vs the AI Gateway built into Foundry — which one? |
| 20 | Gateway | Does the AI gateway work for non-Microsoft models? |
| 21 | Ops | How do we observe agents in production? |
| 22 | Governance | How do we govern hundreds of agents (Control Plane, Purview, Defender, Entra Agent ID)? |
| 23 | Models | Which models are available — Claude, open-weight, Model Router? |
| 24 | Distribution | Can we publish agents to Microsoft 365 Copilot and Teams? |
| 25 | DevOps | How do you deploy this from GitHub without secrets? |
| 26 | Dev tools | What tooling do developers use (VS Code, GitHub Copilot)? |
| 27 | Demo | Why did you set `require_approval="never"` on the MCP tool? |

---

## Platform & migration

### 1. Is Microsoft Foundry just a rename of Azure AI Foundry?

Partly. The lineage is Azure AI Studio → Azure AI Foundry → Microsoft Foundry, and Azure AI Services are now called
**Foundry Tools**. But the "new" Foundry is also a new resource model: one **Foundry resource** with **Foundry
projects** replaces hub + separate Azure OpenAI/AI Services resources, and agents run on the **Responses API** instead of
the Assistants API. RBAC roles were renamed (Azure AI User → Foundry User, etc.) with **unchanged role IDs and
permissions**.
⚠ Uncertain: no single first-party "rename announcement" with a rationale was found; the name appears in Ignite 2025
week posts (Nov 2025). Don't quote a precise rename date.
Sources: learn.microsoft.com/azure/foundry/what-is-foundry · learn.microsoft.com/azure/foundry/concepts/rbac-foundry

### 2. What's the difference between a Foundry resource and a Foundry project?

The **resource** (`Microsoft.CognitiveServices/accounts`, kind `AIServices`, `allowProjectManagement: true`) is the
top-level Azure resource where you manage **governance — networking, security, model deployments**. A **project**
(`accounts/projects`) is the **development boundary** where teams build and evaluate use cases — a container for access
management, data, and monitoring. Code targets the project endpoint
`https://<resource>.services.ai.azure.com/api/projects/<project>`.
Source: learn.microsoft.com/azure/foundry/concepts/architecture

### 3. We use hub-based projects. Do we have to migrate, and what moves?

New agent and model-centric capabilities — including Foundry Agent Service GA — are only available on **Foundry
projects**, and the new portal doesn't support hub-based projects. A documented migration moves **model deployments,
data files, fine-tuned models, and vector stores**; it does **not** move preview agent state (threads, messages,
files), open-source model deployments, or hub project access. Note: prompt flow and managed-compute (Hugging Face)
hosting are hub-only.
⚠ Uncertain: no first-party hard retirement date for hub-based projects as a whole was found — don't quote one.
Source: learn.microsoft.com/azure/foundry-classic/how-to/migrate-project

### 4. When does the Assistants API / classic Agent Service retire?

Classic (Assistants-API-based) **Agents are deprecated and retire on March 31, 2027** (Foundry classic "What's new").
The replacement is Foundry Agent Service on the Responses API, **GA since March 16, 2026**.
⚠ Uncertain: third-party sites claim "Assistants API retires Aug 26, 2026" and "classic infra retires Mar 31, 2027" —
**not first-party confirmed**; don't repeat them. Separately, native Foundry **Workflows** retire **Dec 1, 2026** —
a different story; don't conflate.
Sources: learn.microsoft.com/azure/foundry-classic/agents/whats-new · devblogs.microsoft.com/foundry/foundry-agent-service-ga/

## Agents

### 5. Prompt agents vs hosted agents — which should I use?

Start with **prompt agents** (GA): instructions + model + tools, Foundry-managed, no infrastructure — like our demo.
Choose **hosted agents** (GA) when you need your own code or framework — Agent Framework, LangGraph, OpenAI Agents
SDK, and others — running as a managed container. Voice-based prompt agents (Voice Live) are also GA.
Sources: learn.microsoft.com/azure/foundry/agents/overview · learn.microsoft.com/agent-framework/hosting/foundry-hosted-agent

### 6. Agent Framework vs Semantic Kernel vs AutoGen?

**Microsoft Agent Framework** is the open-source successor that unifies Semantic Kernel's enterprise foundations with
AutoGen's orchestration. **v1.0 shipped April 3, 2026** with stable APIs and long-term support; Python and .NET are GA,
Go is in preview. It has MCP and A2A interoperability built in and is the recommended path for hosted agents and
code-first multi-agent orchestration. New projects: start on Agent Framework; existing SK/AutoGen code: plan a migration.
Sources: devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/ · github.com/microsoft/agent-framework

### 7. Should we use Foundry Workflows for multi-agent orchestration?

No for new work. The native visual/YAML **Workflows** feature never reached GA and **retires on December 1, 2026**;
Microsoft's guidance is to use **Microsoft Agent Framework** for new workflows. Classic "Connected Agents" are
deprecated in favor of the A2A tool and Agent Framework.
Source: learn.microsoft.com/azure/foundry/agents/concepts/workflow

### 8. Is agent memory production-ready?

Not yet — memory in Foundry Agent Service is **Public Preview** (user profile, chat summary, and procedural memory;
extraction → consolidation → retrieval). Use it to learn and prototype; no SLA. For grounded knowledge, **Foundry IQ**
(agentic retrieval over Azure AI Search, exposed via MCP) is **GA** as of Build 2026.
Sources: learn.microsoft.com/azure/foundry/agents/concepts/what-is-memory · learn.microsoft.com/azure/foundry/agents/concepts/what-is-foundry-iq

### 9. What is A2A and is it GA?

Agent-to-Agent protocol for agents to call agents. The **A2A tool (protocol v1.0) is GA for outbound** calls (your
Foundry agent calling another agent). **Exposing** a Foundry agent as an incoming A2A endpoint is **Public Preview**
(introduced Build 2026). Externally hosted A2A agents can be registered in Foundry Control Plane for governance.
⚠ Uncertain: no dated GA follow-up for incoming A2A found — treat as preview.
Source: learn.microsoft.com/azure/foundry/agents/how-to/tools/agent-to-agent

## Security & data

### 10. How do you secure MCP tools?

Layers:
1. **Approvals** — the MCP tool's `require_approval` defaults to `always`; keep it on for tools that write data.
2. **Curate** — use **Toolbox** (GA) to define an approved tool set once and expose it through one MCP-compatible
   endpoint.
3. **Gateway** — front MCP servers with **API Management** (MCP server exposure GA; tools only, no resources/prompts
   yet); Foundry's "govern MCP tools by using an AI gateway" is **preview**.
4. **Identity** — **Microsoft Entra Agent ID** supports OAuth2/MCP/A2A for agent identities.
5. **Guardrails** — tool-call and tool-response guardrails are **preview**; Prompt Shields (GA) and Spotlighting
   (preview) address indirect prompt injection.
Sources: learn.microsoft.com/azure/api-management/mcp-server-overview · learn.microsoft.com/azure/foundry/agents/how-to/tools/governance · learn.microsoft.com/azure/foundry/guardrails/guardrails-overview

### 11. How does authentication work — any API keys?

No keys in the demo. The Foundry resource has `disableLocalAuth: true`; the Container App uses a **user-assigned
managed identity** with **Azure AI User** (now displayed as **Foundry User**) on the Foundry resource and AcrPull on the
registry, via `DefaultAzureCredential`. The OpenAI client comes from `project_client.get_openai_client()` with Entra ID
tokens. Through APIM, the gateway calls Foundry with its own managed identity.
Source: this repo (`infra/`, `docs/architecture.md`) · learn.microsoft.com/azure/foundry/concepts/rbac-foundry

### 12. Can Foundry run on private networking?

Yes, networking is governed at the **Foundry resource** level. For reference implementations, point to the
Azure-Samples/AI-Gateway labs **`private-connectivity`**, **`foundry-e2e-private`**, and **`ai-foundry-private-mcp`**.
Our demo uses public endpoints for simplicity (public data only).
⚠ Uncertain: the research brief doesn't detail which agent tools/features support private networking — check the
Foundry networking docs before committing to a design.
Sources: learn.microsoft.com/azure/foundry/concepts/architecture · github.com/Azure-Samples/AI-Gateway

### 13. Where is my data processed — data residency?

Honest answer: it depends on the **deployment type** and the **region**. The Foundry resource is regional (our demo:
Sweden Central), but our model deployments use **GlobalStandard**, so check what the deployment-type documentation says
about where inference may be processed, and whether another deployment type fits stricter residency needs.
Tools that call external services (e.g., a public MCP server, web grounding) send data outside the model boundary — that's
why our demo sends only public queries to the public Learn MCP server.
⚠ Uncertain: data residency and deployment-type guarantees were **not covered** by the research brief — verify on
Microsoft Learn (Foundry Models deployment types, data privacy) before answering specifically. Offer to follow up.

## Cost & capacity

### 14. What's the pricing model?

Consumption-based, per component:
- **Models** — billed by usage on the deployment (tokens for chat models); price depends on model and deployment type.
- **Tools** — some tools add charges, e.g., Code Interpreter sessions (see ADR-0004).
- **Third-party models** — e.g., Claude in Foundry is billed through an **Azure Marketplace** subscription in "Claude
  Consumption Units".
- **Hosting** — your app (here Container Apps, scale to zero), monitoring, API Management, search, and storage are
  billed as their own Azure services.
⚠ Uncertain: no prices are in the research brief — never quote a number; use the Azure pricing pages/calculator.
Sources: learn.microsoft.com/azure/foundry/foundry-models/concepts/claude-models · docs/adr/0004-preview-features.md

### 15. How do we control cost?

1. **Right-size the model** — measure mini vs nano (demo's Model compare) and gate changes with evaluations.
2. **Gateway budgets** — `llm-token-limit` per consumer/product (429 on rate, 403 on quota).
3. **Chargeback** — `llm-emit-token-metric` to Application Insights with custom dimensions.
4. **Cache** — `llm-semantic-cache-lookup`/`-store` (needs an embeddings deployment + Azure Managed Redis with
   RediSearch).
5. **Routing** — Model Router can route across models from one deployment (⚠ check its GA status first).
6. **Hygiene** — tags (`costCenter`), scale-to-zero hosting, delete demo environments, and the AI-Gateway
   **`finops-framework`** lab.
Sources: learn.microsoft.com/azure/api-management/llm-token-limit-policy · .../llm-emit-token-metric-policy · .../azure-openai-enable-semantic-caching

### 16. How do quotas work and what happens when we hit them?

Model deployments are created with a capacity (our demo: GlobalStandard, capacity 50 per deployment) against regional
subscription quota; exceeding the rate returns **HTTP 429**. Mitigations: retry with `Retry-After`, spread load with
**APIM backend pools + circuit breakers** across deployments or regions (the apim-demo pool spans Sweden Central and
France Central), and request more quota. Check usage with `az cognitiveservices usage list --location <region>`.
⚠ Uncertain: exact quota units/limits per model and the full Agent Service region list weren't captured — check the
quota and region pages.
Source: learn.microsoft.com/azure/api-management/backends · frkim/apim-demo

## Quality, safety & operations

### 17. How do we evaluate agents?

**Evaluations are GA** (announced with Agent Service GA, March 16, 2026). **Continuous evaluation** (recurring runs) is
**preview**; the **agent monitoring dashboard** showing eval scores is **preview**. For adversarial testing, the **AI
Red Teaming Agent** (built on open-source PyRIT) measures attack success rate; agentic-risk categories run in East US 2,
France Central, Sweden Central, Switzerland West, and North Central US. Advice: run evaluations in CI before any
model/prompt change.
⚠ Uncertain: red teaming shows as GA in the portal readiness table but preview in the how-to/SDK docs — say "check the
current status".
Sources: devblogs.microsoft.com/foundry/foundry-agent-service-ga/ · learn.microsoft.com/azure/foundry/concepts/ai-red-teaming-agent

### 18. What responsible AI / safety controls exist?

- **Guardrails and controls framework — GA**; interventions on user input (GA), tool call and tool response
  (**preview** — "agent guardrails are in preview").
- **Prompt Shields** (jailbreak / prompt-injection detection) — GA, part of Azure AI Content Safety.
- **Spotlighting** (indirect-attack defense) — preview. **Task adherence** and **custom filtering** — GA.
- **Red teaming** (see Q17), **Purview** for compliance, **Defender for Cloud** threat protection for AI agents
  (preview).
- At the gateway: **`llm-content-safety`** policy (403 on block).
Sources: learn.microsoft.com/azure/foundry/guardrails/guardrails-overview · learn.microsoft.com/azure/api-management/llm-content-safety-policy

### 19. APIM vs the AI Gateway built into Foundry — which one?

They're the same engine. Foundry's **Manage → AI Gateway** pane (**preview**) either auto-provisions an API Management
**Basic v2** instance or attaches an existing one (must be a **v2 tier**, same tenant and subscription). Use the pane for
a quick start from Foundry; manage APIM directly when you need custom policies, multiple products, multi-provider
backends, or an existing enterprise APIM estate — like the apim-demo with Gold/Bronze products and a two-region pool.
Source: learn.microsoft.com/azure/foundry/configuration/enable-ai-api-management-gateway-portal

### 20. Does the AI gateway work for non-Microsoft models?

Yes, the `llm-*` policies are model-agnostic by name (`llm-token-limit` replaced the legacy `azure-openai-token-limit`),
and the Azure-Samples/AI-Gateway repo has multi-provider labs — e.g., `gemini-models`, `aws-bedrock`, `self-hosted-ollama`,
`slm-self-hosting`.
⚠ Uncertain: confirm policy support for a specific provider's API format in the policy docs.
Source: github.com/Azure-Samples/AI-Gateway · learn.microsoft.com/azure/api-management/llm-token-limit-policy

### 21. How do we observe agents in production?

**Foundry Observability**: OpenTelemetry-based **tracing (preview)**. Once Application Insights is connected,
server-side traces are logged automatically (90-day retention); client-side, use the Azure Monitor OpenTelemetry
exporter (our app uses `azure-monitor-opentelemetry` with OpenAI/agents instrumentation). OTLP export to Datadog,
Grafana Tempo, Jaeger, or Honeycomb is supported. Tracing is **off by default** — turn it on from day one. Add gateway
token metrics for cost per consumer.
Source: learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-client-side

### 22. How do we govern hundreds of agents?

**Foundry Control Plane** for central governance (including registering externally hosted A2A agents); **Microsoft
Purview** toggle in Operate → Compliance (preview surface) for audit, classification, DSPM for AI, eDiscovery;
**Defender for Cloud** threat protection for AI agents (preview since Feb 2, 2026; agent discovery/posture requires
**Microsoft Agent 365** licensing from Jul 1, 2026); **Microsoft Entra Agent ID** for agent identities, adaptive access,
and lifecycle governance (deeper M365 governance needs Agent 365).
⚠ Uncertain: Entra Agent ID has no explicit GA/preview badge on its page.
Sources: learn.microsoft.com/azure/foundry/control-plane/how-to-manage-compliance-security · learn.microsoft.com/azure/defender-for-cloud/release-notes · learn.microsoft.com/entra/agent-id/what-is-microsoft-entra-agent-id

## Models, distribution & DevOps

### 23. Which models are available — Claude, open-weight, Model Router?

The catalog lists **10,000+ models** from Microsoft, OpenAI, Anthropic, Meta, and others: OpenAI GPT-5.x families
(our demo: `gpt-5.4-mini`, `gpt-5.4-nano`), `gpt-oss`, GPT-4.1, o-series; **Claude** models GA via Azure Marketplace;
open-weight DeepSeek, Llama, Mistral, Cohere. **Model Router** routes across providers from one deployment.
⚠ Uncertain: newest model codenames (e.g., GPT-6.x "sol/astra/luna/terra"), some Claude preview names, Model Router's
GA badge, and the xAI/Grok attribution on the fetched page could not be cross-verified — check ai.azure.com before
naming them. Foundry Local's overall GA badge is inconsistent across docs.
Source: learn.microsoft.com/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure

### 24. Can we publish agents to Microsoft 365 Copilot and Teams?

Yes — **GA**. In the Foundry portal: Publish → Teams and Microsoft Copilot. It compiles a Teams app manifest and submits
to the catalogs, using an auto-created Azure Bot Service resource; scope is individual (`BotServiceRbac`) or org-wide
(`BotServiceTenant`, needs admin approval). Requires the **Foundry User** role.
Source: learn.microsoft.com/azure/foundry/agents/how-to/publish-copilot

### 25. How do you deploy this from GitHub without secrets?

Bicep at **subscription scope** (creates the resource group, Foundry resource + project + deployments, identity, ACR
with admin disabled, Container Apps, monitoring) run by GitHub Actions `deploy.yml`. The **runtime is keyless**
(managed identity). For GitHub → Azure, the recommended approach is **OIDC workload identity federation**. Be
transparent: this repo currently documents a temporary service-principal-secret fallback in **ADR-0003**, expiring
2026-12-31, with a migration plan to OIDC.
Source: docs/adr/0003-github-actions-azure-auth-exception.md

### 26. What tooling do developers use?

The **Microsoft Foundry Toolkit for VS Code** (evolution of the AI Toolkit; `aka.ms/foundrytk`); the **Foundry
DevPack** bundle (Toolkit + `azd`/`azd ai` + Foundry Canvas + Foundry Skill); and the **Microsoft Foundry Skill** for
GitHub Copilot (VS Code, Copilot CLI) for model deployment, agent development, evaluation, and optimization guidance.
SDK: `azure-ai-projects` 2.x (latest 2.8.0 as of Oct 2026).
Sources: learn.microsoft.com/azure/foundry/how-to/develop/install-foundry-toolkit-visual-studio-code · learn.microsoft.com/azure/foundry/how-to/develop/use-microsoft-foundry-skill

### 27. Why did you set `require_approval="never"` on the MCP tool?

Because the Microsoft Learn MCP server is **public, read-only, and needs no credentials** — it can't change data or
resources, and no secret is sent to it. The default is `always`, and Microsoft's guidance is to require approval for
high-risk tools, especially those that write data. We only send public queries (`dataClassification=public`).
Source: docs/adr/0005-mcp-tool-microsoft-learn.md

---

## Questions to deflect gracefully

| Question type | Response |
| --- | --- |
| Exact price for X | "Prices change and depend on region and deployment type — let's look at the Azure pricing calculator together after the session." |
| Unannounced roadmap / dates not on Learn | "I only share what's published on Microsoft Learn or the official blogs. Here's where to watch: the Foundry what's-new pages." |
| Customer-specific architecture | "Great question for a 1:1 — let's capture your constraints after the session." |
| Competitor comparisons | Stay factual about Foundry capabilities; avoid claims about other vendors. |
