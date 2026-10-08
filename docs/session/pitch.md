# Pitch — Microsoft Foundry: from AI pilot to production agents

## Title options

| # | Title | Tone |
| --- | --- | --- |
| 1 | **From PoC to Production: Building, Governing, and Shipping AI Agents with Microsoft Foundry** | Recommended — outcome-focused |
| 2 | Microsoft Foundry, the AI App & Agent Factory — Live, End to End | Platform-focused |
| 3 | Escape PoC Purgatory: Agents, Observability, and an AI Gateway on Microsoft Foundry | Problem-focused |
| 4 | One Resource, Many Agents: A Practical Tour of the New Microsoft Foundry | Architecture-focused |
| 5 | Build It, Watch It, Govern It, Ship It — Microsoft Foundry for Developers | Hands-on, developer audience |

## Elevator pitch (30 seconds)

> Most companies have AI pilots; few have AI in production. The gap isn't the model — it's identity, observability,
> cost control, and deployment. In 90 minutes I'll show how the new Microsoft Foundry closes that gap: one Foundry
> resource with projects, thousands of models, and a Responses-API-based Agent Service that went GA in March 2026.
> We'll build a live agent grounded in Microsoft Learn through MCP, trace it, put an AI gateway in front of it, and
> ship it keylessly with Bicep and GitHub Actions. You leave with a working repo, not just slides.

## 2-minute pitch

> **The problem.** Every organization I talk to has a handful of generative AI pilots. Many of them have been "almost
> ready for production" for months. They stall for the same reasons: security asks how the app authenticates, the
> platform team asks how token spend is capped, operations asks how to trace a bad answer, and nobody can say which
> model version is actually running.
>
> **The platform.** Microsoft Foundry — formerly Azure AI Studio and Azure AI Foundry — is Microsoft's platform for
> building, evaluating, and deploying AI apps and agents. The new Foundry collapses the old hub-plus-separate-resources
> model into **one Foundry resource with Foundry projects**, gives you a catalog of more than 10,000 models from
> Microsoft, OpenAI, Anthropic, Meta, and others, and runs agents on the **Foundry Agent Service**, whose
> Responses-API-based runtime reached general availability on March 16, 2026.
>
> **The session.** We go end to end. We tour the resource model and the new portal at ai.azure.com. We look at agent
> types — prompt agents and hosted agents — and the tool catalog: MCP, Code Interpreter, A2A. Then we build it live:
> **Foundry Guide**, a prompt agent that answers Foundry questions with the public Microsoft Learn MCP server and does
> cost math in Code Interpreter. We trace it in Application Insights, talk evaluations and guardrails, then govern it
> at scale with **Azure API Management as an AI gateway** — token limits returning HTTP 429, a load-balanced backend
> pool across two regions, token metrics, and MCP exposed through APIM. Finally, we ship it: Bicep at subscription
> scope, GitHub Actions, managed identity, and no API keys anywhere.
>
> **What you get.** A public repo you can deploy in your own subscription, a mental model for moving from pilot to
> production, and a short list of things to do on Monday.

## Session abstract (event catalog)

**From PoC to Production: Building, Governing, and Shipping AI Agents with Microsoft Foundry** (~120 words)

> AI pilots are easy; production AI is hard. This demo-driven session shows how the new Microsoft Foundry turns
> experiments into governed, observable agents. We tour the Foundry resource and project model, the model catalog,
> and the new portal; explore Foundry Agent Service on the Responses API, Microsoft Agent Framework, MCP, A2A, and
> hosted agents; and build a live agent grounded in Microsoft Learn with Code Interpreter. Next, we trace and evaluate
> it, apply guardrails, and govern model and tool traffic with Azure API Management as an AI gateway — token limits,
> load balancing, token metrics, and MCP. We finish by shipping keylessly with Bicep, managed identity, and GitHub
> Actions. Attendees leave with a deployable reference repo and a practical path from pilot to production.

## Format

| Item | Value |
| --- | --- |
| Duration | 90 minutes (≈ 60 % talk, 30 % live demo, 10 % Q&A) |
| Level | 300 (intermediate–advanced) |
| Demos | 2 live demos (Foundry Guide agent, AI Gateway) with recorded fallback |
| Code | Python 3.13 (FastAPI), Vue 3, Bicep, GitHub Actions — public repo `frkim/foundry-demo` |

## Target audience

| Audience | What they get |
| --- | --- |
| Application developers and AI engineers | Agent definitions, Responses API calls, MCP and Code Interpreter tools, conversations, tracing |
| Solution and cloud architects | Foundry resource/project model, identity, networking hooks, AI gateway patterns, reference architecture |
| Platform / DevOps engineers | Bicep at subscription scope, GitHub Actions, keyless deployment, observability wiring |
| Technical decision makers | What is GA vs preview, migration from classic, cost and governance levers |

## Prerequisites

- Comfortable with Azure fundamentals (subscriptions, resource groups, Microsoft Entra ID, RBAC).
- Basic familiarity with large language models and REST APIs; reading Python is enough.
- Optional, to follow along later: an Azure subscription with model quota in a supported region, Azure CLI, GitHub
  CLI, Python 3.13 with `uv`, Node.js, and permission to assign roles.

## Three key takeaways

1. **One resource, many projects, many models.** The new Foundry resource (`Microsoft.CognitiveServices/accounts`,
   kind `AIServices`) with Foundry projects is the foundation; hub-based projects and the Assistants-API agents are
   the past — classic agents are deprecated and retire on March 31, 2027.
2. **Agents are production-ready — when you can see and govern them.** Foundry Agent Service (GA) plus tools like MCP
   and Code Interpreter get you a capable agent in minutes; tracing, evaluations, guardrails, and an AI gateway in
   API Management make it operable, safe, and cost-controlled.
3. **Ship it like any other app.** Infrastructure as code, GitHub Actions, managed identity, and no API keys
   (`disableLocalAuth: true`) are what turn a demo into a service.

## Call to action

1. **Clone and deploy** `frkim/foundry-demo` in your own subscription — it is designed to be redeployed end to end.
2. **Pick one stalled pilot** and move it onto a Foundry project with managed identity and tracing turned on.
3. **Put an AI gateway in front of your models** — start from `frkim/apim-demo` or the
   [Azure-Samples/AI-Gateway](https://github.com/Azure-Samples/AI-Gateway) labs (`token-rate-limiting`,
   `backend-pool-load-balancing`, `token-metrics-emitting`).
4. **Plan your migration** off hub-based projects and classic agents before March 31, 2027, and off the native
   Foundry Workflows preview before December 1, 2026 (move to Microsoft Agent Framework).
5. **Install the tooling**: Microsoft Foundry Toolkit for VS Code (`aka.ms/foundrytk`) and the Microsoft Foundry
   Skill for GitHub Copilot.

## Host introduction (read by the moderator, 20 seconds)

> "Our next speaker spends their days helping teams take generative AI from pilot to production on Azure. In this
> session you'll see Microsoft Foundry end to end — a live agent, its traces, an AI gateway in front of it, and a
> keyless GitHub Actions deployment — all from a public repo you can reuse. Please welcome …"
