---
marp: true
theme: foundry
lang: en
size: 16:9
paginate: true
title: "Microsoft Foundry: build, ship and govern AI agents"
description: 90-minute technical session on Microsoft Foundry (new) — models, Agent Service, Agent Framework, observability, AI Gateway and DevOps
author: frkim
header: 'Microsoft Foundry · Technical session'
footer: 'Microsoft Foundry deep dive · October 2026 · github.com/frkim/foundry-demo'
---

<!-- _class: lead -->
<!-- _paginate: false -->
<!-- _header: '' -->

<span class="eyebrow">Technical session · 90 minutes · October 2026</span>

# Microsoft Foundry

### Build, ship and **govern** AI agents — from model to production

<div class="meta">Models · Foundry Agent Service · Microsoft Agent Framework · Observability · AI Gateway · Bicep + GitHub Actions<br/>Live demo: <strong>Foundry Guide</strong> — github.com/frkim/foundry-demo</div>

<!--
[00:00 · Opening — 10 min block starts]
Welcome everyone. Over the next 90 minutes we go from "what is Microsoft Foundry" to a governed agent running in production on Azure, built live from a public repo.
Two demos anchor the session: the Foundry Guide agent, and an AI Gateway in front of Foundry with Azure API Management.
Everything you see is in github.com/frkim/foundry-demo, so you do not need to take notes on code.
-->

---

# About this session

<div class="cols-60">
<div>
  <div class="card">
    <h3>Your speaker</h3>
    <p><strong>[Speaker name]</strong> · [Role, team]<br/>[One line about your Azure AI / Foundry experience]</p>
    <p class="mt-s small">[@handle] · [linkedin.com/in/…] · [email]</p>
  </div>
  <div class="card cyan mt">
    <h3>Who this is for</h3>
    <ul>
      <li>Developers and architects shipping generative AI on Azure</li>
      <li>Platform teams who must govern models, agents and cost</li>
      <li>Anyone migrating from Azure OpenAI, hubs or the Assistants API</li>
    </ul>
  </div>
</div>
<div>
  <div class="card dark">
    <h3>Ground rules</h3>
    <ul>
      <li><strong>Foundry (new)</strong> only: Foundry resource + projects</li>
      <li>Status pills on every feature: <span class="pill ok">GA</span> <span class="pill prev">Preview</span> <span class="pill ret">Retiring</span></li>
      <li>Keyless everywhere — no API keys on screen</li>
      <li>Questions welcome any time; deep dives at the end</li>
    </ul>
  </div>
</div>
</div>

<!--
Introduce yourself briefly — keep it under a minute; replace the bracketed placeholders before presenting.
Set the contract: we only cover the new Foundry model (Foundry resource plus projects), and every feature is labelled GA, Preview or Retiring so nobody leaves with a wrong assumption.
Stress that the demos are keyless — managed identity and Entra ID only.
-->

---

# Agenda — 90 minutes

<div class="cols">
<div class="agenda">
  <div class="n">1</div><div class="t">Opening &amp; why Foundry <span>· the enterprise AI problem</span></div><div class="m">10'</div>
  <div class="n">2</div><div class="t">Platform tour <span>· resource, projects, models, portal</span></div><div class="m">15'</div>
  <div class="n">3</div><div class="t">Agents <span>· Agent Service, tools, MCP, A2A, memory</span></div><div class="m">15'</div>
  <div class="n demo">4</div><div class="t">DEMO 1 <span>· Foundry Guide agent</span></div><div class="m">15'</div>
</div>
<div class="agenda">
  <div class="n">5</div><div class="t">Observe, evaluate, govern <span>· safety, Control Plane</span></div><div class="m">10'</div>
  <div class="n demo">6</div><div class="t">AI Gateway + DEMO 2 <span>· Azure API Management</span></div><div class="m">10'</div>
  <div class="n">7</div><div class="t">Ship it <span>· Bicep, GitHub Actions, keyless</span></div><div class="m">5'</div>
  <div class="n">8</div><div class="t">Roadmap, resources, Q&amp;A</div><div class="m">10'</div>
</div>
</div>

<div class="callout violet mt">Two live demos, one public repo, zero API keys. Everything shown is reproducible from <strong>github.com/frkim/foundry-demo</strong>.</div>

<!--
[00:02] Walk the agenda quickly: roughly half concepts, half hands-on.
Blocks 4 and 6 are live demos; if anything misbehaves we have a recorded fallback video in the repo.
Timings are in the speaker notes of every section divider so you can keep pace.
-->

---

# The enterprise AI problem

<p class="kicker">Prototypes are easy. Running hundreds of models and agents safely, at scale, is not.</p>

<div class="cols-3">
  <div class="card red"><h3>Sprawl</h3><p>Separate resources per model, per team, per region. Keys in config files. No single inventory of what is deployed or who calls it.</p></div>
  <div class="card amber"><h3>Agents act</h3><p>Agents call tools, APIs and other agents. That needs identity, approvals, guardrails on tool calls — not just on prompts.</p></div>
  <div class="card"><h3>Proof, not vibes</h3><p>Leaders ask "is it good, is it safe, what does it cost?" — you need traces, evaluations and red-teaming evidence.</p></div>
</div>
<div class="cols-3 mt">
  <div class="card cyan"><h3>Choice</h3><p>The best model changes every quarter. Switching must be a deployment change, not a rewrite.</p></div>
  <div class="card green"><h3>Cost &amp; quota</h3><p>Token budgets per team, chargeback, failover across regions when capacity runs out.</p></div>
  <div class="card navy"><h3>Path to prod</h3><p>Infra as code, CI/CD, private networking and compliance from day one.</p></div>
</div>

<!--
Frame the problem before the product. Most teams we meet have a working prototype but hit walls on sprawl, governance and cost.
Agents raise the stakes because they act: they call tools and other agents, so identity and tool-call guardrails become mandatory.
Each of these six cards maps to a section later in the session — keep that promise in mind.
-->

---

# What Microsoft Foundry is

<p class="kicker">“A managed platform for building, evaluating, and deploying generative AI applications with foundation models.” — <span class="small">Microsoft Learn glossary</span></p>

<div class="diagram">
<svg viewBox="0 0 1152 404" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Rename history: before and now">
  <defs>
    <linearGradient id="gNow" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2e2a85"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>
    <marker id="a1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7c3aed"/></marker>
  </defs>
  <g font-size="13" font-weight="700" fill="#8a8fb0" letter-spacing="2">
    <text x="0" y="18">BEFORE</text><text x="540" y="18">MICROSOFT FOUNDRY (NEW)</text>
  </g>
  <g font-size="17" fill="#1b1f3b">
    <rect x="0" y="32" width="440" height="62" rx="10" fill="#f6f6fc" stroke="#e1e3f0"/><text x="20" y="69">Azure AI Studio → Azure AI Foundry</text>
    <rect x="0" y="106" width="440" height="62" rx="10" fill="#f6f6fc" stroke="#e1e3f0"/><text x="20" y="143">Azure AI Services</text>
    <rect x="0" y="180" width="440" height="62" rx="10" fill="#f6f6fc" stroke="#e1e3f0"/><text x="20" y="208">Hub + separate Azure OpenAI /</text><text x="20" y="230">AI Services resources</text>
    <rect x="0" y="254" width="440" height="62" rx="10" fill="#f6f6fc" stroke="#e1e3f0"/><text x="20" y="291">Assistants API (Agents v0.5 / v1)</text>
    <rect x="0" y="328" width="440" height="62" rx="10" fill="#f6f6fc" stroke="#e1e3f0"/><text x="20" y="356">Azure AI User / Owner /</text><text x="20" y="378">Account Owner / Project Manager</text>
  </g>
  <g stroke="#7c3aed" stroke-width="2.5" marker-end="url(#a1)">
    <line x1="452" y1="63" x2="528" y2="63"/><line x1="452" y1="137" x2="528" y2="137"/><line x1="452" y1="211" x2="528" y2="211"/><line x1="452" y1="285" x2="528" y2="285"/><line x1="452" y1="359" x2="528" y2="359"/>
  </g>
  <g fill="#ffffff">
    <rect x="540" y="32" width="612" height="62" rx="10" fill="url(#gNow)"/>
    <rect x="540" y="106" width="612" height="62" rx="10" fill="url(#gNow)"/>
    <rect x="540" y="180" width="612" height="62" rx="10" fill="url(#gNow)"/>
    <rect x="540" y="254" width="612" height="62" rx="10" fill="url(#gNow)"/>
    <rect x="540" y="328" width="612" height="62" rx="10" fill="url(#gNow)"/>
    <g font-size="19" font-weight="700">
      <text x="562" y="60">Microsoft Foundry</text><text x="562" y="134">Foundry Tools</text><text x="562" y="208">Foundry resource + Foundry projects</text><text x="562" y="282">Responses API (Agents v2)</text><text x="562" y="356">Foundry User / Owner / Account Owner / Project Manager</text>
    </g>
    <g font-size="14" fill="#d9dcff">
      <text x="562" y="82">one platform for models, agents, tools, evaluation and governance</text>
      <text x="562" y="156">Speech, Language, Vision, Document Intelligence, Content Safety, Search…</text>
      <text x="562" y="230">Microsoft.CognitiveServices/accounts · kind AIServices · child projects</text>
      <text x="562" y="304">Foundry Agent Service runtime, wire-compatible with OpenAI agents</text>
      <text x="562" y="378">renamed roles — role IDs and core permissions unchanged</text>
    </g>
  </g>
</svg>
</div>

<!--
One sentence: Foundry is Microsoft's managed platform to build, evaluate and deploy generative AI apps and agents.
The name went Azure AI Studio, then Azure AI Foundry, now Microsoft Foundry — the new name shows up across the Ignite 2025 announcements.
The renames that matter to engineers: AI Services became Foundry Tools, hubs became a single Foundry resource with projects, Assistants became the Responses API, and the RBAC roles were renamed with the same role IDs, so existing assignments keep working.
-->

---

# Foundry at scale — the public numbers

<p class="kicker">Each figure is tied to the moment Microsoft published it — don't mix eras.</p>

<div class="cols-4">
  <div class="kpi"><div class="v">70K<small>+</small></div><div class="l">customers using the platform</div><div class="d">Build 2025 · pre-rename</div></div>
  <div class="kpi alt"><div class="v">100<small> T</small></div><div class="l">tokens processed in the prior quarter</div><div class="d">Build 2025 · pre-rename</div></div>
  <div class="kpi warn"><div class="v">10K<small>+</small></div><div class="l">organizations on Agent Service at its first GA</div><div class="d">Build 2025</div></div>
  <div class="kpi dark"><div class="v">10K<small>+</small></div><div class="l">models from Microsoft, OpenAI, Anthropic, Meta and others</div><div class="d">Microsoft Learn · live</div></div>
</div>

<div class="cols mt">
  <div class="card cyan"><h3>1,400+ enterprise connectors</h3><p>Data-source connectors announced for Agent Service grounding (Build 2025).</p></div>
  <div class="card"><h3>From ~1,800 to 10,000+ models</h3><p>The catalog grew from ~1,800 models (Jan 2025) to 11,000+ in the Ignite 2025 ecosystem message.</p></div>
</div>

<!--
These are Microsoft's published figures, each with its date: 70,000 customers and 100 trillion tokens were Build 2025 numbers, before the rename.
The catalog line is the live Learn statement — more than 10,000 models from Microsoft, OpenAI, Anthropic, Meta and others.
The point is not the size; it's that model choice is now a deployment decision inside one platform.
-->

---

<!-- _class: section -->
<!-- _paginate: false -->

<span class="num">02</span>

# Platform tour

Foundry resource and projects, the model catalog, deployment types, Foundry Tools and the new portal.

<span class="time">15 min · 00:10 → 00:25</span>

<!--
[00:10 · Section 2 — Platform tour, 15 minutes]
We look at the resource model first because every other feature hangs off it: RBAC, networking, deployments and projects.
Then models and deployment types, Foundry Tools, the new portal and the developer tooling.
-->

---

# One resource, many projects

<div class="diagram">
<svg viewBox="0 0 1152 404" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Foundry resource model">
  <defs>
    <linearGradient id="gHead" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#0b1033"/><stop offset="1" stop-color="#2e2a85"/></linearGradient>
  </defs>
  <rect x="0" y="0" width="1152" height="404" rx="14" fill="#f6f6fc" stroke="#c9cbe0" stroke-dasharray="6 5"/>
  <text x="20" y="24" font-size="13" font-weight="700" fill="#8a8fb0" letter-spacing="1.5">RESOURCE GROUP · rg-foundrydemo-dev-swc · Sweden Central</text>
  <rect x="20" y="38" width="1112" height="350" rx="14" fill="#ffffff" stroke="#7c3aed" stroke-width="2"/>
  <rect x="20" y="38" width="1112" height="52" rx="14" fill="url(#gHead)"/>
  <rect x="20" y="66" width="1112" height="24" fill="url(#gHead)"/>
  <text x="44" y="71" font-size="21" font-weight="700" fill="#ffffff">Foundry resource</text>
  <text x="1110" y="70" font-size="15" fill="#c9cdf5" text-anchor="end">Microsoft.CognitiveServices/accounts · kind AIServices · allowProjectManagement: true</text>
  <text x="44" y="118" font-size="12" font-weight="700" fill="#8a8fb0" letter-spacing="1.5">SHARED BY ALL PROJECTS</text>
  <g font-size="17" text-anchor="middle">
    <rect x="44" y="128" width="255" height="84" rx="10" fill="#f1ecff"/>
    <text x="171" y="156" font-weight="700" fill="#0b1033">Model deployments</text><text x="171" y="178" font-size="14" fill="#565d7a">gpt-5.4-mini · gpt-5.4-nano</text><text x="171" y="198" font-size="13" fill="#7c3aed">GlobalStandard</text>
    <rect x="316" y="128" width="255" height="84" rx="10" fill="#f1ecff"/>
    <text x="443" y="156" font-weight="700" fill="#0b1033">Security &amp; networking</text><text x="443" y="178" font-size="14" fill="#565d7a">Entra ID · disableLocalAuth</text><text x="443" y="198" font-size="13" fill="#7c3aed">public or private endpoints</text>
    <rect x="588" y="128" width="255" height="84" rx="10" fill="#f1ecff"/>
    <text x="715" y="156" font-weight="700" fill="#0b1033">Governance</text><text x="715" y="178" font-size="14" fill="#565d7a">RBAC · guardrails · quota</text><text x="715" y="198" font-size="13" fill="#7c3aed">policies at the top level</text>
    <rect x="860" y="128" width="255" height="84" rx="10" fill="#f1ecff"/>
    <text x="987" y="156" font-weight="700" fill="#0b1033">Connections</text><text x="987" y="178" font-size="14" fill="#565d7a">App Insights · Search · MCP</text><text x="987" y="198" font-size="13" fill="#7c3aed">reusable by projects</text>
  </g>
  <text x="44" y="242" font-size="12" font-weight="700" fill="#8a8fb0" letter-spacing="1.5">PROJECTS · accounts/projects — development boundary</text>
  <rect x="44" y="252" width="530" height="122" rx="12" fill="#ffffff" stroke="#0891b2" stroke-width="2"/>
  <text x="64" y="282" font-size="19" font-weight="700" fill="#0b1033">proj-foundrydemo-dev</text>
  <text x="554" y="282" font-size="13" fill="#0891b2" text-anchor="end">this demo</text>
  <rect x="588" y="252" width="527" height="122" rx="12" fill="#ffffff" stroke="#a78bfa" stroke-width="2" stroke-dasharray="6 5"/>
  <text x="608" y="282" font-size="19" font-weight="700" fill="#0b1033">Another team's project</text>
  <text x="1095" y="282" font-size="13" fill="#7c3aed" text-anchor="end">isolated access, data &amp; cost</text>
  <g font-size="14" text-anchor="middle" fill="#2e2a85">
    <rect x="64" y="298" width="118" height="28" rx="14" fill="#e3f8fc"/><text x="123" y="317">Agents</text>
    <rect x="190" y="298" width="118" height="28" rx="14" fill="#e3f8fc"/><text x="249" y="317">Conversations</text>
    <rect x="316" y="298" width="118" height="28" rx="14" fill="#e3f8fc"/><text x="375" y="317">Evaluations</text>
    <rect x="442" y="298" width="118" height="28" rx="14" fill="#e3f8fc"/><text x="501" y="317">Traces</text>
    <rect x="64" y="334" width="118" height="28" rx="14" fill="#e3f8fc"/><text x="123" y="353">Files</text>
    <rect x="190" y="334" width="118" height="28" rx="14" fill="#e3f8fc"/><text x="249" y="353">Vector stores</text>
    <rect x="316" y="334" width="118" height="28" rx="14" fill="#e3f8fc"/><text x="375" y="353">Connections</text>
    <rect x="608" y="298" width="118" height="28" rx="14" fill="#f1ecff"/><text x="667" y="317">Agents</text>
    <rect x="734" y="298" width="118" height="28" rx="14" fill="#f1ecff"/><text x="793" y="317">Evaluations</text>
    <rect x="860" y="298" width="118" height="28" rx="14" fill="#f1ecff"/><text x="919" y="317">Data</text>
  </g>
</svg>
</div>

<p class="mt-s small">Project endpoint: <code>https://&lt;resource-name&gt;.services.ai.azure.com/api/projects/&lt;project-name&gt;</code></p>

<!--
The Foundry resource is a Microsoft.CognitiveServices account of kind AIServices — it's where governance lives: networking, security, model deployments, RBAC.
Setting allowProjectManagement to true lets it host child projects; a project is the development boundary for a team — agents, conversations, evaluations, files and traces.
Notice there's no hub, no storage account or key vault you must create first. Each project gets its own endpoint, shown at the bottom, and that's the only URL your code needs.
-->

---

# Foundry (new) vs. classic

| | **Foundry project** (new) | Hub-based project (classic) |
|---|---|---|
| Parent resource | Foundry resource (`accounts/projects`) | Foundry hub + separate resources |
| Agent Service | <span class="pill ok">GA</span> on the Responses API | Preview, Assistants-API based |
| Portal | ai.azure.com — **Foundry (new)** | Foundry (classic) portal only |
| Foundry API & SDK | Full `azure-ai-projects` 2.x surface | Partial |
| Prompt flow, managed compute (Hugging Face) | Not available | Hub only |
| New agent and model capabilities | **Yes — only here** | No |

<div class="callout warn">Migration moves model deployments, data files, fine-tuned models and vector stores. It does <strong>not</strong> move preview agent state (threads, messages, files), open-source model deployments or hub project access.</div>

<!--
Microsoft is explicit: new agents and model-centric capabilities are only available on Foundry projects, including Agent Service GA.
Hub-based projects still exist for prompt flow and managed-compute hosting, but the new portal does not support hubs, standalone Azure OpenAI resources or classic assistants.
If you migrate, plan for agent state: threads and messages from the preview agents do not transfer.
-->

---

# Endpoints and SDK surface

<div class="cols">
<div>

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

project = AIProjectClient(
    endpoint="https://aif-foundrydemo-dev-xxxxx"
             ".services.ai.azure.com"
             "/api/projects/proj-foundrydemo-dev",
    credential=DefaultAzureCredential(),
)

agents = project.agents              # create_version, list…
openai = project.get_openai_client() # Responses API, v1
```

</div>
<div>
  <div class="card"><h3>One endpoint per project</h3><p>The project endpoint is the only URL the app needs — agents, conversations, evaluations and model calls hang off it.</p></div>
  <div class="card cyan mt-s"><h3>One OpenAI client</h3><p><code>get_openai_client()</code> returns an authenticated OpenAI client on the v1 route — no <code>api-version</code> juggling.</p></div>
  <div class="card green mt-s"><h3>Keyless by default</h3><p><code>DefaultAzureCredential</code>: your az login locally, managed identity in Azure.</p></div>
</div>
</div>

<!--
This is the entire client bootstrap. AIProjectClient from azure-ai-projects 2.x takes the project endpoint and an Entra credential.
From it you get the agents client for creating versioned agents and an OpenAI client already pointed at the Responses API on the v1 route.
There is no API key anywhere; locally DefaultAzureCredential uses your az login, in Azure it uses the user-assigned managed identity.
-->

---

# Model catalog highlights

<div class="cols-3">
  <div class="card"><h3>OpenAI</h3><p>GPT-5.x generations incl. <code>gpt-5.4</code>, <code>-mini</code>, <code>-nano</code>, <code>-pro</code>; GPT-5 family; <code>gpt-oss</code>; GPT-4.1; o-series; GPT-4o.</p></div>
  <div class="card cyan"><h3>Anthropic Claude</h3><p>Opus, Sonnet and Haiku families <span class="pill ok">GA</span> via Azure Marketplace — Anthropic-hosted or Azure-hosted.</p></div>
  <div class="card green"><h3>Open-weight</h3><p>DeepSeek V3.2 / V4, Meta Llama 4 Maverick and 3.3-70B, Cohere Command-A and rerank v4, Mistral Large 3 <span class="pill prev">Preview</span>.</p></div>
</div>
<div class="cols-3 mt">
  <div class="card amber"><h3>Model Router</h3><p>One deployment that routes each request across models from several providers — pick quality vs. cost per prompt.</p></div>
  <div class="card navy"><h3>Foundry Local</h3><p>On-device inference with an OpenAI-compatible API — CUDA, WebGPU, NPU, OpenVINO or CPU.</p></div>
  <div class="card red"><h3>This demo</h3><p><code>gpt-5.4-mini</code> powers the agent; <code>gpt-5.4-nano</code> is the fast model for side-by-side comparison.</p></div>
</div>

<p class="small mt">The catalog changes weekly — always confirm model names, versions and regions at ai.azure.com before you commit to one.</p>

<!--
The catalog is broad: OpenAI's GPT-5.x generations, Anthropic's Claude families as GA via the Azure Marketplace, and open-weight models like DeepSeek, Llama, Cohere and Mistral.
Model Router lets one deployment pick a model per request; Foundry Local brings the same API to devices.
For the demo we use gpt-5.4-mini for the agent and gpt-5.4-nano as the fast comparison model. Always re-check the live catalog — names and versions move quickly.
-->

---

# Deployment types — choose by residency, load and latency

| Requirement | Recommended deployment type |
|---|---|
| Default: newest models, lowest price, broadest regions | **Global Standard** (`GlobalStandard`) |
| Reserved, predictable throughput | Global Provisioned |
| Keep processing in the EU / US / APAC data zone | Data Zone Standard (`DataZoneStandard`) or Data Zone Provisioned |
| Keep processing in one Azure geography | Standard or Regional Provisioned (where supported) |
| Large asynchronous jobs, ~50% cheaper, 24 h target | Global Batch (`GlobalBatch`) or Data Zone Batch |
| Evaluate a fine-tuned model (temporary, no SLA) | Developer |

<div class="callout">Pay-per-token types suit bursty traffic; provisioned types give low latency variance at consistent high volume. The demo uses <strong>Global Standard</strong> in Sweden Central.</div>

<!--
Deployment type is a residency and economics decision, not a model decision. Global Standard is the default: newest models, lowest price, widest availability.
Use Data Zone types when data must stay in the EU, US or APAC zone, provisioned throughput when you need predictable latency at volume, and Batch for large offline jobs at roughly half the cost.
Our demo uses Global Standard for both deployments in Sweden Central.
-->

---

# Foundry Tools — the services formerly known as Azure AI Services

<div class="cols-4">
  <div class="card"><h3>Speech</h3><p>Speech-to-text, text-to-speech and speech translation.</p></div>
  <div class="card cyan"><h3>Language</h3><p>Language understanding and Translator.</p></div>
  <div class="card green"><h3>Documents</h3><p>Document Intelligence and Content Understanding.</p></div>
  <div class="card amber"><h3>Vision</h3><p>Vision and Custom Vision.</p></div>
</div>
<div class="cols-3 mt">
  <div class="card red"><h3>Content Safety</h3><p>Harm categories, Prompt Shields, blocklists — the engine behind Foundry guardrails.</p></div>
  <div class="card navy"><h3>Azure AI Search</h3><p>Hybrid and vector retrieval — the backbone of Foundry IQ knowledge.</p></div>
  <div class="card"><h3>Same resource</h3><p>Reached through the same <code>AIServices</code> account, the same Entra auth, the same RBAC.</p></div>
</div>

<!--
Foundry Tools is the new name for Azure AI Services — the Learn page is literally titled "What are Foundry Tools?".
Speech, Language, Translator, Document Intelligence, Content Understanding, Vision, Content Safety and Azure AI Search all sit here.
Practically, they share the Foundry resource's identity and RBAC model, so an agent can use them without new credentials. Our video pipeline, for example, uses Speech with the same keyless pattern.
-->

---

# The new Foundry portal — ai.azure.com

<div class="cols-60">
<div>

| Portal capability (new Foundry) | Status |
|---|---|
| Agents (core) | <span class="pill ok">GA</span> |
| Publish to Microsoft 365 Copilot / Teams | <span class="pill ok">GA</span> |
| Guardrails for models | <span class="pill ok">GA</span> |
| Guardrails for agents | <span class="pill prev">Preview</span> |
| Monitoring / observability | <span class="pill prev">Preview</span> |
| AI Gateway (APIM) pane | <span class="pill prev">Preview</span> |
| Voice Live | <span class="pill prev">Preview</span> |

</div>
<div>
  <div class="card"><h3>Foundry projects only</h3><p>Hubs, standalone Azure OpenAI resources and classic v1 agents stay in the classic portal.</p></div>
  <div class="card cyan mt-s"><h3>Build → Operate</h3><p>Model playgrounds, agent builder, evaluations, then <strong>Operate</strong> for compliance, AI Gateway and fleet views.</p></div>
  <div class="card amber mt-s"><h3>Tip</h3><p>Use the portal to explore; commit agents and infra as code for anything that ships.</p></div>
</div>
</div>

<!--
The new portal at ai.azure.com shows Foundry projects only — hubs and classic assistants are not supported there.
This table is Microsoft's own GA-readiness snapshot for portal features; note agents core and publishing to Microsoft 365 Copilot and Teams are GA, while agent guardrails, monitoring and the AI Gateway pane are still preview.
My recommendation: explore in the portal, but version your agents and infrastructure in code — which is exactly what the demo does.
-->

---

# Developer experience — VS Code, GitHub Copilot, azd

<div class="cols-3">
  <div class="card"><h3>Foundry Toolkit for VS Code</h3><p>The evolution of AI Toolkit: browse models, build agents, run playgrounds and traces from the editor. Install via <code>aka.ms/foundrytk</code>.</p></div>
  <div class="card cyan"><h3>Microsoft Foundry skill</h3><p>Reusable Copilot guidance for model deployment, prompt and hosted agents, A2A, evaluation and agent optimization.</p></div>
  <div class="card green"><h3>Foundry DevPack</h3><p>Foundry Toolkit + <code>azd</code> / <code>azd ai</code> + Foundry Canvas + the Foundry skill, bundled.</p></div>
</div>

```text
/plugin marketplace add microsoft/azure-skills
/plugin install azure@azure-skills      # also wires Azure MCP + Foundry MCP servers
```

<p class="codecap">Works with GitHub Copilot in VS Code and in the Copilot CLI.</p>

<!--
Developers live in the editor, so Foundry meets them there. The Foundry Toolkit for VS Code is the renamed AI Toolkit.
For GitHub Copilot, the Microsoft Foundry skill gives the agent reusable know-how for deployments, agents, evaluation and optimization; the two plugin commands also wire up the Azure and Foundry MCP servers.
The DevPack bundles all of this with azd so a new team gets a consistent setup in minutes.
-->

---

<!-- _class: section -->
<!-- _paginate: false -->

<span class="num">03</span>

# Agents

Foundry Agent Service, the tool catalog, MCP and A2A, knowledge and memory, Microsoft Agent Framework — and the code.

<span class="time">15 min · 00:25 → 00:40</span>

<!--
[00:25 · Section 3 — Agents, 15 minutes]
This is the heart of the platform. We cover the runtime, the agent types, the tools agents can use, knowledge and memory, and the open-source framework for code-first agents.
We finish with the exact Python you'll see running in Demo 1.
-->

---

# Foundry Agent Service — generally available on the Responses API

<div class="cols-4">
  <div class="kpi dark"><div class="v">GA</div><div class="l">next-gen Agent Service, Responses API-based runtime</div><div class="d">March 16, 2026</div></div>
  <div class="kpi"><div class="v">v1</div><div class="l">wire-compatible with OpenAI agents — one OpenAI client</div><div class="d">Responses API</div></div>
  <div class="kpi alt"><div class="v">2</div><div class="l">GA agent types: prompt agents and hosted agents</div><div class="d">October 2026</div></div>
  <div class="kpi warn"><div class="v">2027</div><div class="l">classic Assistants-API agents retire on March 31</div><div class="d">Deprecated</div></div>
</div>

<div class="cols-3 mt">
  <div class="card"><h3>Versioned agents</h3><p>Every <code>create_version()</code> call produces an immutable agent version you can evaluate, compare and roll back.</p></div>
  <div class="card cyan"><h3>Conversations</h3><p>Server-side conversation state — no thread plumbing, just pass a <code>conversation</code> id.</p></div>
  <div class="card green"><h3>Evaluations GA</h3><p>Evaluations reached GA with the same March 2026 release.</p></div>
</div>

<!--
Two GA stories exist — don't mix them. The classic, Assistants-based Agent Service went GA at Build 2025 and is now deprecated, retiring March 31, 2027.
The next-generation Agent Service, built on the Responses API and wire-compatible with OpenAI agents, went GA on March 16, 2026, together with evaluations.
Agents are versioned, conversations are server-side, and you call everything with the standard OpenAI client.
-->

---

# Agent types — pick the right level of control

<div class="cols-3">
  <div class="card"><h3>Prompt agents <span class="pill ok">GA</span></h3><p>Instructions + model + tools, fully managed by Foundry — no infrastructure. Defined with <code>PromptAgentDefinition</code>. Voice-based prompt agents via Voice Live are GA too.</p></div>
  <div class="card cyan"><h3>Hosted agents <span class="pill ok">GA</span></h3><p>Bring your own code as a managed container: Microsoft Agent Framework, LangGraph, OpenAI Agents SDK, Anthropic Agent SDK, GitHub Copilot SDK.</p></div>
  <div class="card red"><h3>Workflows <span class="pill ret">Retiring</span></h3><p>The visual / YAML multi-agent workflows never left preview and retire on <strong>December 1, 2026</strong>. Build new orchestrations with Agent Framework.</p></div>
</div>

<div class="callout mt"><strong>Connected agents</strong> (classic <code>agent.as_tool</code>) are deprecated — use the <strong>A2A tool</strong> or Agent Framework orchestration instead.</div>

<!--
Prompt agents are the default: declarative, no infrastructure, and they're what Demo 1 uses.
Hosted agents run your own code in a managed container and accept many frameworks; they reached general availability this autumn.
The low-code Workflows feature is the one to avoid for new work — Microsoft retires it on December 1, 2026 and points you to Agent Framework for orchestration. Connected agents are replaced by the A2A tool.
-->

---

# Anatomy of a Foundry agent

<div class="diagram">
<svg viewBox="0 0 1152 430" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Agent anatomy">
  <defs>
    <linearGradient id="gAgent" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2e2a85"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>
    <marker id="a3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#565d7a"/></marker>
  </defs>
  <rect x="210" y="6" width="570" height="38" rx="10" fill="#fff4dc" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="495" y="31" font-size="15" text-anchor="middle" fill="#8a4b00"><tspan font-weight="700">Guardrails</tspan> · user input · tool call · tool response</text>
  <rect x="0" y="150" width="170" height="110" rx="12" fill="#0b1033"/>
  <text x="85" y="192" font-size="19" font-weight="700" fill="#fff" text-anchor="middle">Your app</text>
  <text x="85" y="215" font-size="14" fill="#c9cdf5" text-anchor="middle">OpenAI client</text>
  <text x="85" y="235" font-size="13" fill="#22d3ee" text-anchor="middle">get_openai_client()</text>
  <rect x="210" y="120" width="200" height="170" rx="12" fill="#f1ecff" stroke="#7c3aed" stroke-width="1.5"/>
  <text x="310" y="156" font-size="19" font-weight="700" fill="#0b1033" text-anchor="middle">Responses API</text>
  <g font-size="14" fill="#565d7a" text-anchor="middle"><text x="310" y="184">v1 route · no api-version</text><text x="310" y="208">conversations</text><text x="310" y="232">agent_reference</text><text x="310" y="256">streaming · tool events</text></g>
  <rect x="450" y="60" width="330" height="290" rx="16" fill="url(#gAgent)"/>
  <text x="470" y="96" font-size="21" font-weight="700" fill="#fff">Prompt agent</text>
  <text x="760" y="96" font-size="14" fill="#c9cdf5" text-anchor="end">foundry-guide · v3</text>
  <g font-size="15" fill="#fff">
    <rect x="470" y="114" width="290" height="36" rx="8" fill="#ffffff" fill-opacity="0.13"/><text x="486" y="138">Instructions</text>
    <rect x="470" y="158" width="290" height="36" rx="8" fill="#ffffff" fill-opacity="0.13"/><text x="486" y="182">Model deployment · gpt-5.4-mini</text>
    <rect x="470" y="202" width="290" height="36" rx="8" fill="#ffffff" fill-opacity="0.13"/><text x="486" y="226">Tools</text>
    <rect x="470" y="246" width="290" height="36" rx="8" fill="#ffffff" fill-opacity="0.13"/><text x="486" y="270">Knowledge · Foundry IQ</text>
    <rect x="470" y="290" width="290" height="36" rx="8" fill="#ffffff" fill-opacity="0.13"/><text x="486" y="314">Memory <tspan fill="#c4b5fd">(preview)</tspan></text>
  </g>
  <g fill="none" stroke="#565d7a" stroke-width="2" marker-end="url(#a3)">
    <line x1="170" y1="205" x2="206" y2="205"/>
    <line x1="410" y1="205" x2="446" y2="205"/>
    <line x1="805" y1="63" x2="826" y2="63"/><line x1="805" y1="119" x2="826" y2="119"/><line x1="805" y1="175" x2="826" y2="175"/><line x1="805" y1="231" x2="826" y2="231"/><line x1="805" y1="287" x2="826" y2="287"/><line x1="805" y1="343" x2="826" y2="343"/>
  </g>
  <path d="M780,220 H805 M805,63 V343" stroke="#565d7a" stroke-width="2" fill="none"/>
  <g font-size="15" fill="#0b1033">
    <rect x="830" y="40" width="322" height="46" rx="10" fill="#fff" stroke="#0891b2" stroke-width="1.5"/><text x="848" y="69"><tspan font-weight="700">MCP</tspan> · Microsoft Learn, your servers</text>
    <rect x="830" y="96" width="322" height="46" rx="10" fill="#fff" stroke="#0891b2" stroke-width="1.5"/><text x="848" y="125"><tspan font-weight="700">Code Interpreter</tspan> · sandboxed Python</text>
    <rect x="830" y="152" width="322" height="46" rx="10" fill="#fff" stroke="#0891b2" stroke-width="1.5"/><text x="848" y="181"><tspan font-weight="700">File search</tspan> · Azure AI Search</text>
    <rect x="830" y="208" width="322" height="46" rx="10" fill="#fff" stroke="#0891b2" stroke-width="1.5"/><text x="848" y="237"><tspan font-weight="700">Web search</tspan> · Grounding with Bing</text>
    <rect x="830" y="264" width="322" height="46" rx="10" fill="#fff" stroke="#0891b2" stroke-width="1.5"/><text x="848" y="293"><tspan font-weight="700">OpenAPI</tspan> · Azure Functions</text>
    <rect x="830" y="320" width="322" height="46" rx="10" fill="#fff" stroke="#0891b2" stroke-width="1.5"/><text x="848" y="349"><tspan font-weight="700">A2A</tspan> · other agents</text>
  </g>
  <rect x="0" y="384" width="1152" height="42" rx="10" fill="#e3f8fc"/>
  <text x="576" y="411" font-size="15" text-anchor="middle" fill="#0e6f86"><tspan font-weight="700">Observability</tspan> · OpenTelemetry traces → Application Insights · evaluations · Foundry Control Plane</text>
</svg>
</div>

<!--
Here's the mental model. Your app uses a plain OpenAI client against the Responses API and references the agent by name.
The agent is a versioned bundle of instructions, a model deployment, tools, knowledge and — in preview — memory.
Guardrails sit around inputs and tool traffic, and everything emits OpenTelemetry traces into Application Insights, which we'll use in Demo 1.
-->

---

# Tool catalog

<div class="cols">
<div>

| Generally available | |
|---|---|
| Function calling · custom tools | <span class="pill ok">GA</span> |
| Code interpreter · file search | <span class="pill ok">GA</span> |
| Web search / Grounding with Bing | <span class="pill ok">GA</span> |
| Azure AI Search · knowledge retrieval | <span class="pill ok">GA</span> |
| OpenAPI · Azure Functions | <span class="pill ok">GA</span> |
| MCP tools (remote + custom) | <span class="pill ok">GA</span> |
| A2A tool (protocol v1.0, outbound) | <span class="pill ok">GA</span> |
| Toolbox | <span class="pill ok">GA</span> |

</div>
<div>

| In preview | |
|---|---|
| SharePoint · Microsoft Fabric connectors | <span class="pill prev">Preview</span> |
| Browser automation · computer use | <span class="pill prev">Preview</span> |
| Image generation | <span class="pill prev">Preview</span> |
| Skills (platform catalog) | <span class="pill prev">Preview</span> |
| Deep research | <span class="pill prev">Preview</span> |
| Incoming A2A endpoint | <span class="pill prev">Preview</span> |

<div class="callout violet">Demo 1 uses only GA tools: <strong>MCP</strong> (Microsoft Learn) and <strong>Code Interpreter</strong>.</div>

</div>
</div>

<!--
The left column is everything that's GA today: function calling, code interpreter, file search, Bing grounding, Azure AI Search, OpenAPI, Azure Functions, MCP, outbound A2A and Toolbox.
On the right, the preview tools — useful to explore, but call them out explicitly in any production design review.
Our demo deliberately sticks to GA tools: the Microsoft Learn MCP server and Code Interpreter.
-->

---

# MCP, A2A and Toolbox — open protocols, governed centrally

<div class="cols-3">
  <div class="card"><h3>MCP tools <span class="pill ok">GA</span></h3><p>Point an agent at any remote MCP server — <code>server_label</code>, <code>server_url</code>, <code>require_approval</code>, optional project connection for auth.</p><p class="mt-s small">Demo: <code>https://learn.microsoft.com/api/mcp</code></p></div>
  <div class="card cyan"><h3>A2A <span class="pill ok">GA</span></h3><p>Protocol v1.0: a Foundry agent calls another agent, anywhere. Exposing a Foundry agent as an A2A endpoint is <span class="pill prev">Preview</span>.</p><p class="mt-s small">External A2A agents can be registered in Foundry Control Plane.</p></div>
  <div class="card green"><h3>Toolbox <span class="pill ok">GA</span></h3><p>Define a curated set of tools once and expose them through a single MCP-compatible endpoint, shared across agents.</p><p class="mt-s small">Skills (versioned <code>SKILL.md</code>) ride on Toolbox — <span class="pill prev">Preview</span></p></div>
</div>

<div class="callout mt">Approval matters: <code>require_approval="always"</code> returns an <code>mcp_approval_request</code> your app must answer — use it for any tool with side effects.</div>

<!--
MCP is the standard way to give agents tools; Foundry supports remote MCP servers as GA, with optional approval round-trips for sensitive calls.
A2A version 1.0 lets agents call other agents across platforms; exposing your own agent as an A2A endpoint is still preview.
Toolbox lets a platform team curate tools once and publish them behind one MCP endpoint — that's how you stop every team from wiring its own connectors.
-->

---

# Foundry IQ — the knowledge layer for agents

<p class="kicker">Agentic retrieval over Azure AI Search, exposed to agents through an MCP endpoint. Core <span class="pill ok">GA</span> since Build 2026.</p>

<div class="steps">
  <div><h3>Plan</h3><p>The model decomposes the question into focused sub-queries.</p></div>
  <div><h3>Search</h3><p>Sub-queries run in parallel as hybrid (keyword + vector) searches.</p></div>
  <div><h3>Rerank</h3><p>Results are reranked so only the most relevant passages remain.</p></div>
  <div><h3>Synthesize</h3><p>A grounded answer with citations back to the sources.</p></div>
</div>

<div class="cols-3 mt">
  <div class="card"><h3>Sources</h3><p>Unifies Work IQ, Fabric IQ, Azure SQL, File Search and MCP sources.</p></div>
  <div class="card amber"><h3>Still in preview</h3><p>Fabric IQ, Work IQ and the Serverless tier; portal UI for agentic retrieval.</p></div>
  <div class="card cyan"><h3>Wiring</h3><p>Attach as an <code>MCPTool</code> pointing at the knowledge base MCP endpoint.</p></div>
</div>

<!--
Foundry IQ is the dedicated knowledge layer: query planning, parallel hybrid search, reranking and cited synthesis on top of Azure AI Search.
It reached GA at Build 2026; Fabric IQ, Work IQ and the serverless tier remain preview.
For your code it's just another MCP tool on the agent — the same pattern as the Microsoft Learn server in our demo.
-->

---

# Agent memory <span class="pill prev">Preview</span>

<div class="cols-60">
<div>
  <div class="cols-3">
    <div class="card"><h3>User profile</h3><p>Stable facts and preferences about the user.</p></div>
    <div class="card cyan"><h3>Chat summary</h3><p>Condensed context from past conversations.</p></div>
    <div class="card green"><h3>Procedural</h3><p>How-to knowledge the agent learns from completed tasks.</p></div>
  </div>
  <div class="steps s3 mt">
    <div><h3>Extract</h3><p>Pull candidate memories from conversations.</p></div>
    <div><h3>Consolidate</h3><p>LLM-based deduplication and merge.</p></div>
    <div><h3>Retrieve</h3><p>Inject relevant memories at run time.</p></div>
  </div>
</div>
<div>
  <div class="kpi dark"><div class="v">+7–14<small> pts</small></div><div class="l">absolute success-rate gain on Tau-bench from procedural memory, at near-baseline cost</div><div class="d">Build 2026 announcement</div></div>
  <div class="callout warn">Memory and the Memory Store API are <strong>preview</strong>. Treat stored memories as personal data: retention, deletion and consent.</div>
</div>
</div>

<!--
Memory gives agents continuity across sessions with three types: user profile, chat summary and the newer procedural memory.
The pipeline extracts, consolidates with an LLM to remove duplicates, then retrieves at run time. Microsoft reported a 7 to 14 point success-rate gain on Tau-bench from procedural memory.
It is preview — and memories are personal data, so design retention and deletion from day one.
-->

---

# Microsoft Agent Framework 1.x — code-first agents

<div class="cols-4">
  <div class="kpi dark"><div class="v">1.0</div><div class="l">production-ready, stable APIs, long-term support</div><div class="d">April 3, 2026</div></div>
  <div class="kpi"><div class="v">1.20</div><div class="l">latest <code>agent-framework</code> Python release</div><div class="d">October 2026</div></div>
  <div class="kpi alt"><div class="v">2</div><div class="l">GA languages: Python and .NET (<code>Microsoft.Agents.AI</code>)</div><div class="d">Go in preview</div></div>
  <div class="kpi warn"><div class="v">SK+AG</div><div class="l">successor to Semantic Kernel and AutoGen</div><div class="d">open source</div></div>
</div>

<div class="cols-3 mt">
  <div class="card"><h3>Orchestration</h3><p>Code-first multi-agent orchestration, including Magentic-One — stable since Build 2026 and the replacement for retiring Foundry workflows.</p></div>
  <div class="card cyan"><h3>Interop built in</h3><p>MCP and A2A out of the box; wraps Foundry prompt agents or runs as a Foundry <strong>hosted agent</strong>.</p></div>
  <div class="card green"><h3>Agent Harness <span class="pill ok">GA</span></h3><p>Released July 2026 — includes Skills as a framework feature.</p></div>
</div>

<!--
Agent Framework is the open-source engine that unifies Semantic Kernel's enterprise foundations with AutoGen's orchestration. It hit 1.0 on April 3, 2026; the Python package is at 1.20 today.
Use it when you need code-first multi-agent orchestration — it's Microsoft's stated replacement for the retiring Foundry workflows.
It speaks MCP and A2A natively and deploys as a Foundry hosted agent, so you don't trade governance for flexibility.
-->

---

# Code — create a versioned prompt agent

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MCPTool, PromptAgentDefinition
from azure.identity import DefaultAzureCredential

project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())

learn = MCPTool(server_label="microsoft_learn",
                server_url="https://learn.microsoft.com/api/mcp",
                require_approval="never")

agent = project.agents.create_version(
    agent_name="foundry-guide",
    definition=PromptAgentDefinition(
        model="gpt-5.4-mini", instructions=INSTRUCTIONS, tools=[learn]),
)
```

<p class="codecap"><code>azure-ai-projects</code> 2.x · the demo also adds <code>CodeInterpreterTool</code> and runs this idempotently at startup — a failure never crashes the app, <code>/health/ready</code> reports it.</p>

<!--
This is the real startup code from the demo, trimmed. One AIProjectClient, one MCPTool pointing at the Microsoft Learn MCP server, and create_version with a PromptAgentDefinition.
Each call creates a new immutable version of foundry-guide, which is what you evaluate and roll back.
Note require_approval never is fine here because the Learn server is read-only; use always for tools with side effects.
-->

---

# Code — invoke the agent through the Responses API

```python
openai = project.get_openai_client()            # Responses API, v1 route
conversation = openai.conversations.create()

response = openai.responses.create(
    conversation=conversation.id,
    input="How do I enable tracing for a Foundry agent?",
    extra_body={"agent_reference": {"name": "foundry-guide",
                                    "type": "agent_reference"}},
)
print(response.output_text)

for item in response.output:                    # evidence of tool use
    if item.type == "mcp_call":
        print(item.server_label, item.name)
```

<p class="codecap">Same OpenAI client for agents and raw model calls — <code>responses.create(model="gpt-5.4-nano", …)</code> powers the demo's model compare.</p>

<!--
Invocation is the standard OpenAI Responses call. We create a server-side conversation, then reference the agent by name in extra_body.
The response contains the final text plus typed output items, including MCP calls — that's how the demo UI shows tool-call chips.
For the model-compare tab we call the same client with a model deployment name instead of an agent reference.
-->

---

# Reach users where they work

<div class="cols-60">
<div>
  <div class="card"><h3>Publish to Microsoft 365 Copilot and Teams <span class="pill ok">GA</span></h3>
  <ul>
    <li>Foundry portal → <strong>Publish → Teams and Microsoft Copilot</strong></li>
    <li>Auto-generates the Teams app manifest and submits it to the catalog</li>
    <li>Auto-creates an Azure Bot Service resource</li>
    <li>Scope: individual (<code>BotServiceRbac</code>) or organization (<code>BotServiceTenant</code>, admin approval)</li>
    <li>Requires the <strong>Foundry User</strong> role</li>
  </ul></div>
</div>
<div>
  <div class="card cyan"><h3>Or your own front end</h3><p>Any app that can call the Responses API — like the Vue + FastAPI demo — can host the same agent version.</p></div>
  <div class="card green mt-s"><h3>Or other agents</h3><p>Through A2A, your agent becomes a building block for agents on other platforms.</p></div>
</div>
</div>

<!--
Building the agent is half the job; adoption is the other half. Publishing to Microsoft 365 Copilot and Teams is GA and largely automated from the portal.
You choose individual or organization scope; organization scope goes through admin approval in the tenant.
The same agent version can simultaneously serve your own web app, which is what we'll show next.
-->

---

<!-- _class: section -->
<!-- _paginate: false -->

<span class="num">04</span>

# DEMO 1 — Foundry Guide

A keyless FastAPI + Vue app on Azure Container Apps, talking to a Foundry prompt agent with MCP and Code Interpreter.

<span class="time">15 min · 00:40 → 00:55</span>

<!--
[00:40 · Section 4 — Demo 1, 15 minutes]
Switch to the browser with the Foundry Guide app already open, plus the Foundry portal and Application Insights in separate tabs.
Fallback: the recorded walkthrough in docs/video/foundry-demo.mp4 if the network or the region misbehaves.
-->

---

# Foundry Guide — what you'll see

<div class="cols-4">
  <div class="card"><h3>Agent chat</h3><p>Ask about Foundry; the agent grounds answers in Microsoft Learn via MCP. Tool-call chips show every MCP or Code Interpreter call.</p></div>
  <div class="card cyan"><h3>Model compare</h3><p>The same prompt on <code>gpt-5.4-mini</code> and <code>gpt-5.4-nano</code> in parallel — output, latency and tokens side by side.</p></div>
  <div class="card green"><h3>Run history</h3><p>Last 200 runs: time, kind, model or agent, latency, tokens, status — search, sort, filter.</p></div>
  <div class="card amber"><h3>About</h3><p>Live <code>/api/info</code>: endpoint host, models, agent name and version, app version, region.</p></div>
</div>

<div class="cols-3 mt">
  <div class="kpi"><div class="v">0</div><div class="l">API keys — user-assigned managed identity end to end</div></div>
  <div class="kpi alt"><div class="v">2</div><div class="l">GA tools on the agent: MCP + Code Interpreter</div></div>
  <div class="kpi dark"><div class="v">1</div><div class="l">container: FastAPI API + Vue / Vuetify SPA, port 8000</div></div>
</div>

<!--
Here's the app. Four tabs: agent chat with tool-call chips, model compare between mini and nano, a run history table, and an About page with live configuration.
There are zero keys anywhere: the container uses a user-assigned managed identity to call Foundry.
Everything ships in a single container — FastAPI serves both the API and the built Vue SPA.
-->

---

# Demo 1 architecture

<div class="diagram">
<svg viewBox="0 0 1152 446" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Foundry Guide demo architecture">
  <defs>
    <linearGradient id="gAg4" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2e2a85"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>
    <marker id="a4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#565d7a"/></marker>
  </defs>
  <g font-size="12" font-weight="700" fill="#8a8fb0" letter-spacing="1.5">
    <text x="10" y="22">USER</text>
    <text x="190" y="22">CONTAINER APPS · France Central</text>
    <text x="560" y="22">FOUNDRY · Sweden Central</text>
    <text x="940" y="22">TOOLS</text>
  </g>
  <rect x="10" y="150" width="140" height="90" rx="12" fill="#fff" stroke="#0b1033" stroke-width="2"/>
  <text x="80" y="188" font-size="18" font-weight="700" fill="#0b1033" text-anchor="middle">Browser</text>
  <text x="80" y="210" font-size="13" fill="#565d7a" text-anchor="middle">Vue 3 + Vuetify SPA</text>
  <rect x="10" y="300" width="140" height="56" rx="10" fill="#f6f6fc" stroke="#c9cbe0"/>
  <text x="80" y="324" font-size="15" font-weight="700" fill="#0b1033" text-anchor="middle">Container Registry</text>
  <text x="80" y="343" font-size="12" fill="#565d7a" text-anchor="middle">image · AcrPull</text>
  <rect x="190" y="34" width="330" height="306" rx="14" fill="#f6f6fc" stroke="#e1e3f0"/>
  <rect x="210" y="54" width="290" height="190" rx="12" fill="#fff" stroke="#7c3aed" stroke-width="2"/>
  <text x="230" y="84" font-size="18" font-weight="700" fill="#0b1033">ca-foundrydemo-dev</text>
  <g font-size="14" fill="#2e2a85">
    <rect x="230" y="100" width="250" height="30" rx="8" fill="#f1ecff"/><text x="244" y="120">FastAPI · POST /api/agent/chat</text>
    <rect x="230" y="138" width="250" height="30" rx="8" fill="#f1ecff"/><text x="244" y="158">POST /api/models/compare</text>
    <rect x="230" y="176" width="250" height="30" rx="8" fill="#f1ecff"/><text x="244" y="196">GET /api/history · /api/info</text>
  </g>
  <text x="230" y="230" font-size="13" fill="#565d7a">static SPA · /health/live · /health/ready</text>
  <rect x="210" y="262" width="290" height="60" rx="10" fill="#0b1033"/>
  <text x="230" y="287" font-size="15" font-weight="700" fill="#fff">id-foundrydemo-dev</text>
  <text x="230" y="308" font-size="13" fill="#22d3ee">user-assigned MI · DefaultAzureCredential</text>
  <rect x="560" y="34" width="340" height="306" rx="14" fill="#fff" stroke="#7c3aed" stroke-width="2"/>
  <text x="580" y="64" font-size="16" font-weight="700" fill="#0b1033">Project · proj-foundrydemo-dev</text>
  <rect x="580" y="80" width="300" height="128" rx="12" fill="url(#gAg4)"/>
  <text x="600" y="112" font-size="19" font-weight="700" fill="#fff">Agent · foundry-guide</text>
  <text x="600" y="138" font-size="14" fill="#e6e8ff">prompt agent on gpt-5.4-mini</text>
  <text x="600" y="160" font-size="14" fill="#e6e8ff">instructions · MCP · Code Interpreter</text>
  <text x="600" y="188" font-size="13" fill="#c4b5fd">Responses API · conversations</text>
  <rect x="580" y="222" width="300" height="46" rx="10" fill="#e3f8fc"/>
  <text x="600" y="251" font-size="15" fill="#0e6f86"><tspan font-weight="700">gpt-5.4-nano</tspan> · fast model for compare</text>
  <text x="580" y="300" font-size="13" fill="#565d7a">Deployments: GlobalStandard · Sweden Central</text>
  <text x="580" y="322" font-size="13" fill="#565d7a">disableLocalAuth: true · Foundry User role</text>
  <rect x="940" y="80" width="212" height="84" rx="12" fill="#fff" stroke="#0891b2" stroke-width="2"/>
  <text x="1046" y="114" font-size="16" font-weight="700" fill="#0b1033" text-anchor="middle">Microsoft Learn MCP</text>
  <text x="1046" y="138" font-size="12" fill="#565d7a" text-anchor="middle">learn.microsoft.com/api/mcp</text>
  <rect x="940" y="184" width="212" height="84" rx="12" fill="#fff" stroke="#7c3aed" stroke-width="2" stroke-dasharray="6 4"/>
  <text x="1046" y="218" font-size="16" font-weight="700" fill="#0b1033" text-anchor="middle">Code Interpreter</text>
  <text x="1046" y="242" font-size="12" fill="#565d7a" text-anchor="middle">managed Python sandbox</text>
  <rect x="190" y="378" width="710" height="56" rx="12" fill="#e3f8fc" stroke="#0891b2"/>
  <text x="545" y="403" font-size="16" font-weight="700" fill="#0e6f86" text-anchor="middle">Application Insights + Log Analytics</text>
  <text x="545" y="423" font-size="13" fill="#0e6f86" text-anchor="middle">azure-monitor-opentelemetry · OpenAI / agent spans · structured JSON logs</text>
  <g fill="none" stroke="#565d7a" stroke-width="2" marker-end="url(#a4)">
    <path d="M150,195 H206"/>
    <path d="M500,130 H576"/>
    <path d="M500,190 C540,190 540,245 576,245"/>
    <path d="M880,122 H936"/>
    <path d="M880,180 C910,180 910,226 936,226"/>
    <path d="M150,328 H186"/>
  </g>
  <g fill="none" stroke="#0891b2" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#a4)">
    <path d="M355,340 V374"/><path d="M730,340 V374"/>
  </g>
  <g font-size="12" font-weight="700" text-anchor="middle" fill="#fff">
    <circle cx="178" cy="178" r="11" fill="#c026d3"/><text x="178" y="182">1</text>
    <circle cx="538" cy="114" r="11" fill="#c026d3"/><text x="538" y="118">2</text>
    <circle cx="908" cy="106" r="11" fill="#c026d3"/><text x="908" y="110">3</text>
    <circle cx="370" cy="357" r="11" fill="#c026d3"/><text x="370" y="361">4</text>
  </g>
</svg>
</div>

<div class="legend"><span><b style="background:#c026d3">1</b>HTTPS to the SPA + API</span><span><b style="background:#c026d3">2</b>Entra token from the managed identity — no keys</span><span><b style="background:#c026d3">3</b>agent calls MCP / Code Interpreter</span><span><b style="background:#c026d3">4</b>OpenTelemetry to App Insights</span></div>

<!--
Walk the numbers. One: the browser loads the SPA and calls the FastAPI backend, both in one container app.
Two: the backend gets an Entra token from its user-assigned managed identity and calls the Foundry project — agent chat goes to foundry-guide, compare calls go straight to the two deployments.
Three: the agent calls the Microsoft Learn MCP server and Code Interpreter. Four: everything is traced into Application Insights with OpenTelemetry.
-->

---

# Demo 1 — script

<div class="cols-60">
<div class="checklist">
  <ul>
    <li><strong>About</strong> tab — endpoint, region, agent name + version, app version</li>
    <li><strong>Agent chat</strong> — suggested prompt; point at the <em>microsoft_learn</em> MCP chip</li>
    <li>Follow-up in the same conversation; ask for a quick calculation → Code Interpreter</li>
    <li><strong>Model compare</strong> — same prompt on mini vs. nano; read latency + tokens</li>
    <li><strong>Run history</strong> — filter by kind, sort by latency</li>
    <li>Foundry portal — agent versions, then traces in <strong>Application Insights</strong></li>
  </ul>
</div>
<div>
  <div class="card dark"><h3>What to point out</h3>
  <ul>
    <li>No key in env vars — only <code>AZURE_CLIENT_ID</code></li>
    <li>Agent is code-defined and versioned</li>
    <li>Grounded answers carry Learn links</li>
    <li>Same client for agents and raw models</li>
  </ul></div>
  <div class="callout warn">Fallback: <code>docs/video/foundry-demo.mp4</code> and <code>docs/session/demo-runbook.md</code>.</div>
</div>
</div>

<!--
Follow the checklist; it maps one-to-one to the runbook in docs/session.
Start with About to prove the configuration is live, then chat, then compare, then history, then jump to the portal and App Insights to show the same run from the platform side.
If anything fails, switch to the recorded video and keep talking over it — the story doesn't change.
-->

---

# Under the hood — one chat turn

<div class="steps s5">
  <div><h3>UI</h3><p><code>POST /api/agent/chat</code> with the message and an optional conversation id.</p></div>
  <div><h3>Identity</h3><p>The managed identity selected by <code>AZURE_CLIENT_ID</code> gets an Entra token.</p></div>
  <div><h3>Conversation</h3><p>First turn creates a Foundry conversation; later turns reuse its id.</p></div>
  <div><h3>Agent run</h3><p><code>responses.create()</code> with an <code>agent_reference</code> — the agent picks its tools.</p></div>
  <div><h3>Result</h3><p>Text, conversation id, tool calls, token usage and latency — plus a trace.</p></div>
</div>

<div class="cols mt">
  <div class="card"><h3>Readiness, not just liveness</h3><p><code>/health/ready</code> returns 503 until configuration is present and the agent version exists — Container Apps won't route traffic before that.</p></div>
  <div class="card cyan"><h3>Fail soft</h3><p>Agent creation runs at startup but never crashes the app; errors surface in readiness and logs.</p></div>
</div>

<!--
This is the request path for a single chat turn. The UI posts to the API, the API authenticates with the managed identity, creates or reuses a Foundry conversation, and runs the agent through the Responses API.
The API returns text, the conversation id, the tool calls, token usage and latency, which feed the chips and the history table.
Readiness is tied to the agent existing, so a broken deployment never receives traffic.
-->

---

<!-- _class: section -->
<!-- _paginate: false -->

<span class="num">05</span>

# Observe, evaluate, govern

Tracing, evaluations, red teaming, guardrails, Foundry Control Plane — and the Entra, Defender and Purview integrations.

<span class="time">10 min · 00:55 → 01:05</span>

<!--
[00:55 · Section 5 — Observability and governance, 10 minutes]
The demo worked; now how do we know it's good, safe and compliant — and keep it that way?
This section is mostly preview features, so be precise about status.
-->

---

# Observability — traces you can actually use

<div class="cols">
<div>
  <div class="card"><h3>Tracing <span class="pill prev">Preview</span></h3>
  <ul>
    <li>OpenTelemetry-based, off by default</li>
    <li><strong>Server-side</strong> traces auto-logged once Application Insights is connected — 90-day retention</li>
    <li><strong>Client-side</strong>: OTel + Azure Monitor exporter, or OTLP to Datadog, Grafana Tempo, Jaeger, Honeycomb</li>
  </ul></div>
  <div class="card cyan mt-s"><h3>Agent monitoring dashboard <span class="pill prev">Preview</span></h3><p>Token usage, latency, success rate, evaluation scores and red-team results per agent.</p></div>
</div>
<div>

```python
from azure.monitor.opentelemetry import (
    configure_azure_monitor,
)

# reads APPLICATIONINSIGHTS_CONNECTION_STRING
configure_azure_monitor()
# + OpenAI / agent instrumentation:
#   one span per model call, agent run
#   and tool call
```

<div class="callout">In the demo, Bicep creates a project connection to Application Insights so the portal shows the same traces.</div>
</div>
</div>

<!--
Observability in Foundry is OpenTelemetry end to end. Connect Application Insights and server-side agent traces are captured automatically with 90-day retention.
On the client, the demo calls configure_azure_monitor and adds OpenAI and agent instrumentation, so each model call, agent run and tool call is a span.
Both tracing and the agent monitoring dashboard are preview today — fine for dev, call it out for production sign-off.
-->

---

# Evaluations and AI red teaming

<div class="cols-3">
  <div class="card green"><h3>Evaluations <span class="pill ok">GA</span></h3><p>Quality and safety evaluators on datasets or agent runs — compare agent versions before you promote one.</p></div>
  <div class="card"><h3>Continuous evaluation <span class="pill prev">Preview</span></h3><p>Recurring evaluations on live traffic, surfaced in the monitoring dashboard.</p></div>
  <div class="card red"><h3>AI Red Teaming Agent</h3><p>Built on open-source <strong>PyRIT</strong> + Foundry risk and safety evaluations; reports <strong>Attack Success Rate</strong>.</p></div>
</div>

<div class="cols mt">
  <div class="card amber"><h3>Agentic risk categories</h3><p>Prohibited actions, sensitive-data leakage, task adherence — cloud red teaming in East US 2, France Central, <strong>Sweden Central</strong>, Switzerland West, US North Central.</p></div>
  <div class="card navy"><h3>Ship gate</h3><p>Run evaluations on every new agent version in CI; block promotion on regressions; red-team before first exposure to users.</p></div>
</div>

<!--
Evaluations are GA: run them on datasets or on agent runs, and compare versions before promoting.
Continuous evaluation is preview and keeps scoring live traffic. The AI Red Teaming Agent builds on Microsoft's open-source PyRIT and reports an attack success rate; check its current status for your region before relying on it.
The agentic risk categories — prohibited actions, data leakage and task adherence — are available in a handful of regions, including Sweden Central where our demo runs.
-->

---

# Guardrails and controls

<div class="cols-60">
<div>

| Intervention point / control | Status |
|---|---|
| Guardrails framework · user input | <span class="pill ok">GA</span> |
| Tool call | <span class="pill prev">Preview</span> |
| Tool response | <span class="pill prev">Preview</span> |
| Prompt Shields (jailbreak / prompt injection) | <span class="pill ok">GA</span> |
| Task adherence · custom filtering | <span class="pill ok">GA</span> |
| Spotlighting (tag lower-trust content) | <span class="pill prev">Preview</span> |
| Guided guardrail set-up wizard | <span class="pill prev">Preview</span> |

</div>
<div>
  <div class="card"><h3>Why tool guardrails matter</h3><p>With MCP and web tools, the attack surface is the <strong>tool response</strong> — an injected instruction in a web page or a document.</p></div>
  <div class="card cyan mt-s"><h3>Defense in depth</h3><p>Guardrails in Foundry + <code>llm-content-safety</code> at the gateway + approval for side-effecting tools.</p></div>
</div>
</div>

<!--
Guardrails are GA for models and user input; guardrails on tool calls and tool responses — the agent-specific part — are still preview.
Prompt Shields, task adherence and custom filtering are GA; spotlighting, which tags lower-trust content to blunt indirect prompt injection, is preview.
For agents, assume the tool response is hostile: combine Foundry guardrails, gateway content safety and human approval for tools with side effects.
-->

---

# Foundry Control Plane and enterprise governance

<div class="cols-4">
  <div class="card"><h3>Foundry Control Plane</h3><p>Central governance surface for compliance and security settings — and registration of external A2A agents.</p></div>
  <div class="card cyan"><h3>Microsoft Entra Agent ID</h3><p>Identities for agents: blueprints, OAuth2 / MCP / A2A, adaptive access, lifecycle governance, audit — also for agents outside Azure.</p></div>
  <div class="card red"><h3>Defender for Cloud <span class="pill prev">Preview</span></h3><p>Threat protection for AI agents with OWASP-aligned LLM and agentic detections (Feb 2026).</p></div>
  <div class="card green"><h3>Microsoft Purview</h3><p>Toggle under <strong>Operate → Compliance</strong> <span class="pill prev">Preview</span>: Audit, DSPM for AI, DLM, eDiscovery, insider risk.</p></div>
</div>

<div class="callout warn mt"><strong>Licensing note:</strong> since July 1, 2026, Defender agent discovery and posture require a <strong>Microsoft Agent 365</strong> license; deeper cross-Microsoft 365 agent governance in Entra also needs Agent 365 (included in M365 E7, add-on elsewhere).</div>

<!--
Governance is where Foundry plugs into the rest of the Microsoft security stack. Control Plane is the central governance surface and can register external A2A agents.
Entra Agent ID gives agents real identities with lifecycle and audit; Defender adds threat protection for agents in preview; Purview brings audit, DSPM for AI and eDiscovery through a single toggle.
Flag the licensing change: agent discovery and posture in Defender moved to the Microsoft Agent 365 license on July 1, 2026.
-->

---

<!-- _class: section -->
<!-- _paginate: false -->

<span class="num">06</span>

# AI Gateway with Azure API Management

Token budgets, load balancing, content safety, semantic caching and MCP governance — in front of every Foundry endpoint.

<span class="time">10 min · 01:05 → 01:15 · includes DEMO 2</span>

<!--
[01:05 · Section 6 — AI Gateway, 10 minutes including Demo 2]
Foundry governs what happens inside a project; the AI Gateway governs traffic across teams, regions and providers.
We'll look at the policies, the architecture, then run the frkim/apim-demo client against a live gateway.
-->

---

# Why put a gateway in front of Foundry?

<div class="cols-3">
  <div class="card"><h3>Token budgets</h3><p>Tokens-per-minute and monthly quotas per team, product or subscription key — 429 on rate, 403 on quota.</p></div>
  <div class="card cyan"><h3>Resilience</h3><p>Backend pools across regions and projects with circuit breakers that honor <code>Retry-After</code>.</p></div>
  <div class="card green"><h3>Visibility &amp; chargeback</h3><p>Prompt, completion and total token metrics with custom dimensions in Application Insights.</p></div>
</div>
<div class="cols-3 mt">
  <div class="card red"><h3>Safety at the edge</h3><p>Content Safety categories, Prompt Shields and blocklists before a request reaches any model.</p></div>
  <div class="card amber"><h3>Cost</h3><p>Semantic caching answers repeated questions without calling the model.</p></div>
  <div class="card navy"><h3>MCP governance</h3><p>Expose REST APIs as MCP servers, or front existing ones, with the same auth and policies.</p></div>
</div>

<!--
A gateway turns AI consumption into a managed API product. Each team gets a token budget, traffic fails over across regions, and finance gets token metrics with dimensions for chargeback.
Safety is enforced centrally, caching reduces cost, and the same gateway governs MCP tools.
None of this requires changes in the app beyond pointing it at the gateway URL.
-->

---

# The GenAI gateway policies

| Capability | Policy / feature | Notes |
|---|---|---|
| Token rate limit + quota | `llm-token-limit` | `tokens-per-minute`, `token-quota`, `token-quota-period`; alias `azure-openai-token-limit` |
| Token metrics | `llm-emit-token-metric` | prompt / completion / total tokens, up to 5 custom dimensions |
| Semantic caching | `llm-semantic-cache-lookup` / `-store` | needs an embeddings deployment + Azure Managed Redis (RediSearch) |
| Content safety | `llm-content-safety` | harm categories, `shield-prompt`, blocklists — 403 on block |
| Load balancing | Backend pools | round-robin, weighted or priority |
| Failover | Circuit breaker on backends | dynamic trip duration honors `Retry-After` |
| MCP | MCP server in APIM <span class="pill ok">GA</span> | export a REST API as MCP, or pass through to an existing server |

<!--
These are the exact policy names to search for in the APIM docs. llm-token-limit enforces rate and quota; llm-emit-token-metric sends token counts to Application Insights.
Semantic caching uses a lookup and a store policy and needs an embeddings deployment plus Azure Managed Redis with RediSearch.
Load balancing and failover are backend features — pools plus circuit breakers — rather than policies, and MCP server support is GA across the classic and v2 tiers.
-->

---

# AI Gateway reference architecture

<div class="diagram">
<svg viewBox="0 0 1152 410" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="AI Gateway architecture">
  <defs>
    <marker id="a5" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#565d7a"/></marker>
    <linearGradient id="gF5" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#2e2a85"/><stop offset="1" stop-color="#7c3aed"/></linearGradient>
  </defs>
  <g font-size="12" font-weight="700" fill="#8a8fb0" letter-spacing="1.5"><text x="0" y="14">CONSUMERS</text><text x="760" y="14">BACKENDS</text></g>
  <g text-anchor="middle">
    <rect x="0" y="60" width="170" height="70" rx="12" fill="#0b1033"/><text x="85" y="91" font-size="16" font-weight="700" fill="#fff">Apps &amp; agents</text><text x="85" y="112" font-size="12" fill="#22d3ee">Foundry Guide, copilots</text>
    <rect x="0" y="170" width="170" height="70" rx="12" fill="#0b1033"/><text x="85" y="201" font-size="16" font-weight="700" fill="#fff">Teams / products</text><text x="85" y="222" font-size="12" fill="#22d3ee">Gold · Bronze budgets</text>
    <rect x="0" y="280" width="170" height="70" rx="12" fill="#0b1033"/><text x="85" y="311" font-size="16" font-weight="700" fill="#fff">MCP clients</text><text x="85" y="332" font-size="12" fill="#22d3ee">agents, IDEs</text>
  </g>
  <rect x="210" y="24" width="500" height="380" rx="14" fill="#f6f6fc" stroke="#7c3aed" stroke-width="2"/>
  <text x="230" y="54" font-size="17" font-weight="700" fill="#0b1033">Azure API Management · AI Gateway</text>
  <g font-size="15" fill="#2e2a85">
    <rect x="235" y="70" width="450" height="44" rx="9" fill="#fff" stroke="#c4b5fd"/><text x="252" y="98"><tspan font-weight="700">llm-token-limit</tspan> · TPM + quota per product</text>
    <rect x="235" y="124" width="450" height="44" rx="9" fill="#fff" stroke="#c4b5fd"/><text x="252" y="152"><tspan font-weight="700">llm-content-safety</tspan> · categories + Prompt Shields</text>
    <rect x="235" y="178" width="450" height="44" rx="9" fill="#fff" stroke="#c4b5fd"/><text x="252" y="206"><tspan font-weight="700">llm-semantic-cache</tspan> · lookup / store</text>
    <rect x="235" y="232" width="450" height="44" rx="9" fill="#fff" stroke="#c4b5fd"/><text x="252" y="260"><tspan font-weight="700">Backend pool</tspan> · priority / weighted + circuit breaker</text>
    <rect x="235" y="286" width="450" height="44" rx="9" fill="#fff" stroke="#c4b5fd"/><text x="252" y="314"><tspan font-weight="700">llm-emit-token-metric</tspan> · custom dimensions</text>
    <rect x="235" y="340" width="450" height="44" rx="9" fill="#e3f8fc" stroke="#0891b2"/><text x="252" y="368" fill="#0e6f86"><tspan font-weight="700">MCP server</tspan> · from REST API or passthrough</text>
  </g>
  <g fill="none" stroke="#565d7a" stroke-width="2" marker-end="url(#a5)">
    <path d="M170,95 H206"/><path d="M170,205 H206"/><path d="M170,315 H206"/>
    <path d="M685,254 C722,254 722,185 756,185"/><path d="M685,254 C722,254 722,275 756,275"/>
    <path d="M685,362 H756"/>
  </g>
  <path d="M685,308 H735 V322 H985 V230 H996" fill="none" stroke="#0891b2" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#a5)"/>
  <g text-anchor="middle">
    <rect x="760" y="150" width="200" height="70" rx="12" fill="url(#gF5)"/><text x="860" y="180" font-size="16" font-weight="700" fill="#fff">Foundry project</text><text x="860" y="202" font-size="13" fill="#e6e8ff">Sweden Central</text>
    <rect x="760" y="240" width="200" height="70" rx="12" fill="url(#gF5)"/><text x="860" y="270" font-size="16" font-weight="700" fill="#fff">Foundry project</text><text x="860" y="292" font-size="13" fill="#e6e8ff">France Central</text>
    <rect x="760" y="340" width="200" height="50" rx="12" fill="#fff" stroke="#0891b2" stroke-width="2"/><text x="860" y="371" font-size="15" font-weight="700" fill="#0b1033">Backend REST API</text>
    <rect x="1000" y="150" width="152" height="160" rx="12" fill="#e3f8fc" stroke="#0891b2"/><text x="1076" y="218" font-size="15" font-weight="700" fill="#0e6f86">Application</text><text x="1076" y="238" font-size="15" font-weight="700" fill="#0e6f86">Insights</text><text x="1076" y="262" font-size="12" fill="#0e6f86">token metrics</text>
  </g>
</svg>
</div>

<!--
Consumers on the left call one gateway URL. Requests flow through the token limit, content safety and the semantic cache, then a backend pool spreads load across Foundry projects in Sweden Central and France Central with circuit breakers.
Token metrics land in Application Insights for dashboards and chargeback.
The same gateway exposes an MCP server built from a REST API — tools get the same auth, limits and logging as models. This is exactly the frkim/apim-demo topology.
-->

---

# Policy as code — a token-aware inbound pipeline

```xml
<inbound>
  <base />
  <authentication-managed-identity resource="https://cognitiveservices.azure.com" />
  <set-backend-service backend-id="foundry-pool" />
  <llm-token-limit counter-key="@(context.Subscription.Id)"
                   tokens-per-minute="5000" token-quota="200000"
                   token-quota-period="Monthly" estimate-prompt-tokens="false" />
  <llm-content-safety backend-id="content-safety" shield-prompt="true" />
  <llm-emit-token-metric namespace="ai-gateway">
    <dimension name="Subscription ID" />
    <dimension name="API ID" />
  </llm-emit-token-metric>
</inbound>
```

<p class="codecap">Gateway → Foundry is keyless too: APIM's managed identity holds the Foundry User role on each backend. Full policies: <code>frkim/apim-demo/infra/policies/</code>.</p>

<!--
This is what a token-aware inbound section looks like. APIM authenticates to Foundry with its own managed identity, routes to the backend pool, enforces a per-subscription token rate and monthly quota, checks content safety and emits token metrics with two dimensions.
Order matters: reject early, before you spend tokens.
The full, deployable versions are in the apim-demo repo's policies folder.
-->

---

# Governing MCP tools with the gateway

<div class="cols">
<div>
  <div class="card"><h3>MCP server in API Management <span class="pill ok">GA</span></h3>
  <ul>
    <li>Export any managed REST API as an MCP server</li>
    <li>Or pass through to an existing MCP server</li>
    <li>Streamable HTTP (SSE deprecated); tools only — no resources or prompts yet</li>
    <li>Developer, Basic, Standard, Premium — classic and v2 tiers</li>
  </ul></div>
</div>
<div>
  <div class="card cyan"><h3>From the Foundry side <span class="pill prev">Preview</span></h3>
  <ul>
    <li><strong>Manage → AI Gateway</strong> pane: create one (Basic v2) or attach an existing v2-tier APIM in the same tenant and subscription</li>
    <li>“Govern MCP tools by using an AI gateway” — route agent tool traffic through APIM</li>
  </ul></div>
  <div class="callout">Same story for models and tools: identity, limits, logging, one place.</div>
</div>
</div>

<!--
MCP support in API Management is GA: export a REST API as an MCP server or proxy an existing one, over streamable HTTP. Today it exposes tools only.
From Foundry, the AI Gateway pane and MCP tool governance are preview: you can create a Basic v2 gateway or attach an existing v2 instance.
The message: treat tools exactly like models — authenticated, rate-limited and logged in one place.
-->

---

# DEMO 2 — AI Gateway in action

<div class="cols-60">
<div>

```text
# github.com/frkim/apim-demo — Bicep, no azd
az deployment sub what-if -n apimaigw-demo -l swedencentral `
  -f infra\main.bicep --result-format ResourceIdOnly
az deployment sub create -n apimaigw-demo -l swedencentral `
  -f infra\main.bicep

cd demo
python -m ai_gateway all
# or: chat | load-balance | token-limit | content-safety
#     | mcp | agent | metrics
```

</div>
<div>
  <div class="card"><h3>What it proves</h3><p>Keyless chat · load balancing across two Foundry projects · throttling · safety enforcement · MCP tools · a Responses API agent flow · token telemetry.</p></div>
  <div class="card cyan mt-s"><h3>Go deeper — AI-Gateway labs</h3><p><span class="tag">backend-pool-load-balancing</span><span class="tag">token-rate-limiting</span><span class="tag">token-metrics-emitting</span><span class="tag">semantic-caching</span><span class="tag">content-safety</span><span class="tag">model-context-protocol</span><span class="tag">mcp-from-api</span><span class="tag">ai-foundry-hosted-agents</span></p></div>
</div>
</div>

<p class="small mt-s">Labs: github.com/Azure-Samples/AI-Gateway · ~50 Jupyter labs with Bicep and APIM policies</p>

<!--
Switch to the terminal. The apim-demo repo deploys APIM Basic v2, two Foundry projects and all the policies with plain Bicep; the client runs each scenario.
Run "load-balance" to show requests alternating regions, "token-limit" to trigger a 429, "content-safety" for a 403, and "metrics" to show token counts in App Insights.
For self-study, point people to the Azure-Samples AI-Gateway labs listed here — each is a notebook with Bicep and policies.
-->

---

<!-- _class: section -->
<!-- _paginate: false -->

<span class="num">07</span>

# Ship it

Bicep for the Foundry resource, projects and deployments; GitHub Actions with OIDC; keyless RBAC everywhere.

<span class="time">5 min · 01:15 → 01:20</span>

<!--
[01:15 · Section 7 — Deploy and DevOps, 5 minutes]
Everything in Demo 1 was deployed from the repo by a GitHub Actions workflow — no portal clicks.
We'll look at the essential Bicep, the pipeline and the identity model.
-->

---

# Bicep — the Foundry resource and project

```bicep
resource foundry 'Microsoft.CognitiveServices/accounts@2026-07-01' = {
  name: accountName                        // aif-foundrydemo-dev-<suffix>
  location: location
  kind: 'AIServices'
  sku: { name: 'S0' }
  properties: {
    customSubDomainName: accountName       // custom subdomain for Entra ID auth
    allowProjectManagement: true           // enables child Foundry projects
    disableLocalAuth: true                 // Entra ID only — no keys
  }
}
resource project 'Microsoft.CognitiveServices/accounts/projects@2026-07-01' = {
  parent: foundry
  name: projectName                        // proj-foundrydemo-dev (+ location, identity)
}
```

<p class="codecap">Trimmed from <code>infra/modules/foundry.bicep</code> · the subscription-scope <code>main.bicep</code> creates <code>rg-foundrydemo-dev-swc</code> and wires outputs (<code>projectEndpoint</code>, <code>uamiClientId</code>…) into the container app.</p>

<!--
This is the heart of the infrastructure: an account of kind AIServices with allowProjectManagement set to true, which is what makes it a Foundry resource that can host projects.
disableLocalAuth true removes keys entirely; every caller must use Entra ID, which is why the custom subdomain is required.
The project is a child resource; its endpoint becomes FOUNDRY_PROJECT_ENDPOINT for the app through a Bicep output.
-->

---

# Bicep — model deployments and role assignments

```bicep
@batchSize(1) // deployments on one account must not run concurrently
resource deployments 'Microsoft.CognitiveServices/accounts/deployments@2026-07-01' = [for m in models: {
  parent: foundry
  name: m.name                                   // gpt-5.4-mini, gpt-5.4-nano
  sku: { name: 'GlobalStandard', capacity: m.capacity }
  properties: { model: { format: 'OpenAI', name: m.modelName, version: m.modelVersion } }
}]
resource appIsFoundryUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: foundry
  name: guid(foundry.id, appPrincipalId, foundryUserRoleId)
  properties: {
    principalId: appPrincipalId                  // user-assigned MI of the container app
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', foundryUserRoleId)
  }
}
```

<p class="codecap">The repo also sets <code>versionUpgradeOption: 'NoAutoUpgrade'</code> so a demo never changes model version underneath you.</p>

<!--
Deployments are a child array of the account; batchSize 1 serializes them because concurrent deployments on one account fail.
The role assignment gives the app's managed identity the Foundry User role scoped to the Foundry resource only — least privilege, no subscription-wide roles.
Look up the role ID from the official Foundry RBAC page or az role definition list rather than copying a GUID from a slide.
-->

---

# GitHub Actions — from push to a ready agent

<div class="diagram">
<svg viewBox="0 0 1152 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="CI/CD pipeline">
  <defs>
    <linearGradient id="gStep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7c3aed"/><stop offset="1" stop-color="#22d3ee"/></linearGradient>
    <marker id="a6" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7c3aed"/></marker>
  </defs>
  <g font-size="12" font-weight="700" fill="#8a8fb0" letter-spacing="1.5"><text x="0" y="16">ci.yml</text><text x="196" y="16">deploy.yml</text></g>
  <g fill="none" stroke="#7c3aed" stroke-width="2.5" marker-end="url(#a6)">
    <line x1="168" y1="110" x2="192" y2="110"/><line x1="364" y1="110" x2="388" y2="110"/><line x1="560" y1="110" x2="584" y2="110"/><line x1="756" y1="110" x2="780" y2="110"/><line x1="952" y1="110" x2="976" y2="110"/>
  </g>
  <g font-size="13" text-anchor="middle">
    <rect x="0" y="30" width="168" height="160" rx="12" fill="#0b1033"/>
    <circle cx="84" cy="62" r="16" fill="url(#gStep)"/><text x="84" y="67" fill="#fff" font-weight="700">1</text>
    <text x="84" y="104" font-size="17" font-weight="700" fill="#fff">Validate</text><text x="84" y="128" fill="#c9cdf5">ruff · mypy · pytest</text><text x="84" y="148" fill="#c9cdf5">web lint + build</text><text x="84" y="168" fill="#c9cdf5">bicep lint · what-if</text>
    <rect x="196" y="30" width="168" height="160" rx="12" fill="#fff" stroke="#7c3aed" stroke-width="2"/>
    <circle cx="280" cy="62" r="16" fill="url(#gStep)"/><text x="280" y="67" fill="#fff" font-weight="700">2</text>
    <text x="280" y="104" font-size="17" font-weight="700" fill="#0b1033">azure/login</text><text x="280" y="128" fill="#565d7a">OIDC federated</text><text x="280" y="148" fill="#565d7a">credential</text><text x="280" y="168" fill="#7c3aed">no stored secret</text>
    <rect x="392" y="30" width="168" height="160" rx="12" fill="#fff" stroke="#7c3aed" stroke-width="2"/>
    <circle cx="476" cy="62" r="16" fill="url(#gStep)"/><text x="476" y="67" fill="#fff" font-weight="700">3</text>
    <text x="476" y="104" font-size="17" font-weight="700" fill="#0b1033">Bicep</text><text x="476" y="128" fill="#565d7a">az deployment</text><text x="476" y="148" fill="#565d7a">sub create</text><text x="476" y="168" fill="#7c3aed">outputs → env</text>
    <rect x="588" y="30" width="168" height="160" rx="12" fill="#fff" stroke="#7c3aed" stroke-width="2"/>
    <circle cx="672" cy="62" r="16" fill="url(#gStep)"/><text x="672" y="67" fill="#fff" font-weight="700">4</text>
    <text x="672" y="104" font-size="17" font-weight="700" fill="#0b1033">az acr build</text><text x="672" y="128" fill="#565d7a">ACR Tasks</text><text x="672" y="148" fill="#565d7a">image tag =</text><text x="672" y="168" fill="#7c3aed">git SHA</text>
    <rect x="784" y="30" width="168" height="160" rx="12" fill="#fff" stroke="#7c3aed" stroke-width="2"/>
    <circle cx="868" cy="62" r="16" fill="url(#gStep)"/><text x="868" y="67" fill="#fff" font-weight="700">5</text>
    <text x="868" y="104" font-size="17" font-weight="700" fill="#0b1033">Deploy app</text><text x="868" y="128" fill="#565d7a">redeploy template</text><text x="868" y="148" fill="#565d7a">with new image</text><text x="868" y="168" fill="#7c3aed">new revision</text>
    <rect x="980" y="30" width="172" height="160" rx="12" fill="url(#gStep)"/>
    <circle cx="1066" cy="62" r="16" fill="#0b1033"/><text x="1066" y="67" fill="#fff" font-weight="700">6</text>
    <text x="1066" y="104" font-size="17" font-weight="700" fill="#fff">Smoke test</text><text x="1066" y="128" fill="#fff">GET /health/ready</text><text x="1066" y="148" fill="#fff">200 = agent</text><text x="1066" y="168" fill="#fff">version ready</text>
  </g>
  <rect x="0" y="222" width="1152" height="64" rx="12" fill="#f1ecff"/>
  <text x="576" y="250" font-size="16" text-anchor="middle" fill="#2e2a85"><tspan font-weight="700">Runtime identity:</tspan> id-foundrydemo-dev → Foundry User on the Foundry resource · AcrPull on the registry</text>
  <text x="576" y="273" font-size="14" text-anchor="middle" fill="#565d7a">Package installs in CI and Dockerfile go through the protected npm / PyPI feeds only</text>
</svg>
</div>

<div class="callout mt">The deck itself is built by a third workflow (<code>deck.yml</code>): Marp → HTML, PDF and PPTX → GitHub Pages.</div>

<!--
CI validates everything on each pull request: Python lint, types and tests, the Vue build, Bicep lint and a what-if against the subscription.
Deploy logs in with an OIDC federated credential, runs the subscription-scope Bicep, builds the image with ACR Tasks tagged with the commit SHA, redeploys the container app and smoke-tests the readiness endpoint, which only returns 200 when the agent version exists.
Even this deck is built by a workflow and published to GitHub Pages.
-->

---

# Keyless by design

<div class="cols-60">
<div>

| Principal | Role | Scope |
|---|---|---|
| App identity (`id-foundrydemo-dev`) | **Foundry User** · AcrPull | Foundry resource · registry |
| Presenter / deployer principals | Foundry User + Speech User | Foundry resource |
| APIM managed identity (Demo 2) | Foundry User | each Foundry backend |
| GitHub Actions | OIDC federated credential | subscription |

<p class="small mt-s">Foundry User = the renamed Azure AI User role — same role ID, same permissions, so existing assignments keep working.</p>

</div>
<div>

```python
# AZURE_CLIENT_ID picks the
# user-assigned identity
cred = DefaultAzureCredential()
project = AIProjectClient(
    endpoint=ENDPOINT,
    credential=cred)
```

<div class="card green mt-s"><h3>Result</h3><p><code>disableLocalAuth: true</code> on the account: there is no key to leak, rotate or store in Key Vault.</p></div>
</div>
</div>

<!--
This table is the entire access model. The app identity gets Foundry User on the account and AcrPull on the registry; presenters get Foundry User plus Speech User for the video pipeline; APIM uses its own identity in Demo 2.
Foundry User is the renamed Azure AI User role with the same ID, so nothing breaks after the rename.
The same code runs locally and in Azure — DefaultAzureCredential just picks a different identity.
-->

---

<!-- _class: section -->
<!-- _paginate: false -->

<span class="num">08</span>

# Roadmap, resources, Q&amp;A

Key dates to plan around, what to do next week, and where to learn more.

<span class="time">10 min · 01:20 → 01:30</span>

<!--
[01:20 · Section 8 — Roadmap and Q&A, 10 minutes]
Keep the roadmap to about three minutes and leave at least five minutes for questions.
The goal of this block is a short list of dated actions people can take back to their teams.
-->

---

# Key dates

<div class="diagram">
<svg viewBox="0 0 1152 400" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Foundry timeline">
  <defs><linearGradient id="gLine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#7c3aed"/><stop offset="0.68" stop-color="#22d3ee"/><stop offset="1" stop-color="#be123c"/></linearGradient></defs>
  <rect x="10" y="196" width="1132" height="8" rx="4" fill="url(#gLine)"/>
  <g stroke="#c9cbe0" stroke-width="1.5">
    <line x1="85" y1="170" x2="85" y2="196"/><line x1="208" y1="204" x2="208" y2="230"/><line x1="331" y1="170" x2="331" y2="196"/><line x1="454" y1="204" x2="454" y2="230"/><line x1="577" y1="170" x2="577" y2="196"/><line x1="700" y1="204" x2="700" y2="230"/><line x1="823" y1="170" x2="823" y2="196"/><line x1="946" y1="204" x2="946" y2="230"/><line x1="1069" y1="170" x2="1069" y2="196"/>
  </g>
  <g stroke="#fff" stroke-width="3">
    <circle cx="85" cy="200" r="10" fill="#7c3aed"/><circle cx="208" cy="200" r="10" fill="#7c3aed"/><circle cx="331" cy="200" r="10" fill="#7c3aed"/><circle cx="454" cy="200" r="10" fill="#7c3aed"/><circle cx="577" cy="200" r="10" fill="#7c3aed"/><circle cx="700" cy="200" r="10" fill="#7c3aed"/>
    <circle cx="823" cy="200" r="15" fill="#22d3ee"/>
    <circle cx="946" cy="200" r="10" fill="#be123c"/><circle cx="1069" cy="200" r="10" fill="#be123c"/>
  </g>
  <g font-size="14" text-anchor="middle">
    <rect x="10" y="58" width="150" height="112" rx="10" fill="#f6f6fc" stroke="#e1e3f0"/>
    <text x="85" y="84" font-weight="700" fill="#7c3aed">Oct 1, 2025</text><text x="85" y="108" fill="#1b1f3b">Agent Framework</text><text x="85" y="128" fill="#1b1f3b">announced</text><text x="85" y="148" fill="#565d7a" font-size="12">open source</text>
    <rect x="133" y="230" width="150" height="112" rx="10" fill="#f6f6fc" stroke="#e1e3f0"/>
    <text x="208" y="256" font-weight="700" fill="#7c3aed">Nov 2025</text><text x="208" y="280" fill="#1b1f3b">Ignite: the name</text><text x="208" y="300" fill="#1b1f3b">Microsoft Foundry</text><text x="208" y="320" fill="#565d7a" font-size="12">workflows preview</text>
    <rect x="256" y="58" width="150" height="112" rx="10" fill="#f6f6fc" stroke="#e1e3f0"/>
    <text x="331" y="84" font-weight="700" fill="#7c3aed">Mar 16, 2026</text><text x="331" y="108" fill="#1b1f3b">Agent Service GA</text><text x="331" y="128" fill="#1b1f3b">Responses API</text><text x="331" y="148" fill="#565d7a" font-size="12">+ evaluations GA</text>
    <rect x="379" y="230" width="150" height="112" rx="10" fill="#f6f6fc" stroke="#e1e3f0"/>
    <text x="454" y="256" font-weight="700" fill="#7c3aed">Apr 3, 2026</text><text x="454" y="280" fill="#1b1f3b">Agent Framework</text><text x="454" y="300" fill="#1b1f3b">1.0</text><text x="454" y="320" fill="#565d7a" font-size="12">stable APIs, LTS</text>
    <rect x="502" y="58" width="150" height="112" rx="10" fill="#f6f6fc" stroke="#e1e3f0"/>
    <text x="577" y="84" font-weight="700" fill="#7c3aed">Jun 2, 2026</text><text x="577" y="108" fill="#1b1f3b">Build 2026:</text><text x="577" y="128" fill="#1b1f3b">Foundry IQ GA</text><text x="577" y="148" fill="#565d7a" font-size="12">A2A inbound preview</text>
    <rect x="625" y="230" width="150" height="112" rx="10" fill="#f6f6fc" stroke="#e1e3f0"/>
    <text x="700" y="256" font-weight="700" fill="#7c3aed">Jul 1, 2026</text><text x="700" y="280" fill="#1b1f3b">Defender agent</text><text x="700" y="300" fill="#1b1f3b">posture → Agent 365</text><text x="700" y="320" fill="#565d7a" font-size="12">licensing change</text>
    <rect x="748" y="58" width="150" height="112" rx="10" fill="#0b1033"/>
    <text x="823" y="84" font-weight="700" fill="#22d3ee">Oct 2026 · today</text><text x="823" y="108" fill="#fff">Hosted agents</text><text x="823" y="128" fill="#fff">GA</text><text x="823" y="148" fill="#c9cdf5" font-size="12">Agent Framework 1.20</text>
    <rect x="871" y="230" width="150" height="112" rx="10" fill="#fde7ec" stroke="#f5b5c4"/>
    <text x="946" y="256" font-weight="700" fill="#be123c">Dec 1, 2026</text><text x="946" y="280" fill="#1b1f3b">Foundry workflows</text><text x="946" y="300" fill="#1b1f3b">(preview) retire</text><text x="946" y="320" fill="#565d7a" font-size="12">→ Agent Framework</text>
    <rect x="994" y="58" width="150" height="112" rx="10" fill="#fde7ec" stroke="#f5b5c4"/>
    <text x="1069" y="84" font-weight="700" fill="#be123c">Mar 31, 2027</text><text x="1069" y="108" fill="#1b1f3b">Classic agents</text><text x="1069" y="128" fill="#1b1f3b">(Assistants API)</text><text x="1069" y="148" fill="#565d7a" font-size="12">retire</text>
  </g>
</svg>
</div>

<div class="legend"><span><b style="background:#7c3aed"></b>shipped</span><span><b style="background:#22d3ee"></b>today</span><span><b style="background:#be123c"></b>retirement — plan your migration</span></div>

<!--
Read the timeline left to right: Agent Framework announced in October 2025, the Microsoft Foundry name at Ignite, Agent Service GA on the Responses API in March, Agent Framework 1.0 in April, Foundry IQ GA at Build, and hosted agents GA this autumn.
The two red dates are the ones to act on: Foundry workflows retire on December 1, 2026 — move to Agent Framework — and classic Assistants-based agents retire on March 31, 2027.
Anything else you may have read about broader classic retirement dates isn't confirmed by Microsoft documentation; check the official what's-new pages.
-->

---

# Call to action — next week, not next year

<div class="cols">
<div class="checklist">
  <ul>
    <li>Clone <strong>frkim/foundry-demo</strong> and deploy it to a sandbox subscription</li>
    <li>Inventory Assistants-API agents and hub projects; plan the move to Foundry projects before <strong>Mar 31, 2027</strong></li>
    <li>Replace any Foundry <strong>workflows</strong> with Agent Framework before <strong>Dec 1, 2026</strong></li>
    <li>Set <code>disableLocalAuth: true</code> and move every caller to Entra ID</li>
  </ul>
</div>
<div class="checklist">
  <ul>
    <li>Turn on tracing + Application Insights for every agent project</li>
    <li>Add evaluations to CI and gate promotion of new agent versions</li>
    <li>Put an <strong>AI Gateway</strong> in front of shared model capacity — start with token limits and metrics</li>
    <li>Install the Foundry skill in GitHub Copilot for your team</li>
  </ul>
</div>
</div>

<!--
Leave the room with eight concrete actions. The first is easy: clone and deploy the demo repo — it takes one workflow run.
The time-bound ones are the retirements: workflows by December 1, 2026 and classic Assistants-based agents by March 31, 2027.
The rest are hygiene: keyless auth, tracing, evaluation gates and a gateway for shared capacity.
-->

---

# Resources

<div class="cols">
<div class="card">
  <h3>Microsoft Learn</h3>
  <ul class="small">
    <li>learn.microsoft.com/azure/foundry/what-is-foundry</li>
    <li>learn.microsoft.com/azure/foundry/concepts/architecture</li>
    <li>learn.microsoft.com/azure/foundry/agents/overview</li>
    <li>learn.microsoft.com/azure/foundry/agents/concepts/tool-catalog</li>
    <li>learn.microsoft.com/azure/foundry/foundry-models/concepts/deployment-types</li>
    <li>learn.microsoft.com/azure/foundry/concepts/rbac-foundry</li>
    <li>learn.microsoft.com/azure/foundry/guardrails/guardrails-overview</li>
    <li>learn.microsoft.com/azure/api-management/llm-token-limit-policy</li>
    <li>learn.microsoft.com/azure/api-management/mcp-server-overview</li>
  </ul>
</div>
<div>
  <div class="card cyan">
    <h3>Code</h3>
    <ul class="small">
      <li><strong>github.com/frkim/foundry-demo</strong> — this session: app, Bicep, workflows, deck</li>
      <li>github.com/frkim/apim-demo — AI Gateway demo</li>
      <li>github.com/Azure-Samples/AI-Gateway — ~50 labs</li>
      <li>github.com/microsoft/agent-framework</li>
    </ul>
  </div>
  <div class="card mt-s">
    <h3>Announcements</h3>
    <ul class="small">
      <li>devblogs.microsoft.com/foundry/foundry-agent-service-ga</li>
      <li>devblogs.microsoft.com/foundry/agent-service-build2026</li>
    </ul>
  </div>
</div>
</div>

<!--
Everything on this slide is linked from the repo README, so people can just grab the repo URL.
The Learn pages are the source of truth for status labels — they change faster than any deck, including this one.
If you only open one link, open github.com/frkim/foundry-demo.
-->

---

<!-- _class: closing -->
<!-- _paginate: false -->
<!-- _header: '' -->

<span class="eyebrow">Q&amp;A · thank you</span>

# Questions?

### Thank you — now go **ship a governed agent**.

<div class="meta">Slides, app, Bicep and workflows: <strong>github.com/frkim/foundry-demo</strong><br/>AI Gateway demo: github.com/frkim/apim-demo · Labs: github.com/Azure-Samples/AI-Gateway<br/>[Speaker name] · [contact]</div>

<!--
[01:25 · Q&A] Open the floor. Good prompts if it's quiet: "How do I migrate an Assistants-based agent?", "When should I use hosted agents instead of prompt agents?", "Where does the AI Gateway sit versus Foundry guardrails?"
Use docs/session/qa-prep.md for prepared answers.
Close by thanking the audience and pointing once more at the repo URL.
-->

