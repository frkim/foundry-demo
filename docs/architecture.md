# Architecture

The **Foundry Guide** demo is a single container on Azure Container Apps that serves a Vue 3/Vuetify SPA and a
FastAPI backend. The backend calls a Microsoft Foundry (new) project keylessly through a user-assigned managed
identity. Infrastructure is Bicep at subscription scope, deployed by GitHub Actions. Decisions are recorded in
[`adr/`](adr/README.md).

## Components

```mermaid
flowchart LR
    user([Browser<br/>Vue 3 + Vuetify SPA])

    subgraph gh[GitHub]
        actions[GitHub Actions<br/>ci.yml · deploy.yml · deck.yml]
    end

    subgraph rg[Resource group rg-foundrydemo-dev-swc · swedencentral]
        subgraph cae[Container Apps environment cae-foundrydemo-dev · appLocation]
            app[Container App ca-foundrydemo-dev<br/>FastAPI + static SPA · port 8000]
        end
        uami[[User-assigned identity<br/>id-foundrydemo-dev]]
        acr[(Container Registry<br/>crfoundrydemodev*)]
        subgraph foundry[Foundry resource aif-foundrydemo-dev-*]
            project[Foundry project proj-foundrydemo-dev<br/>agent foundry-guide]
            mini[gpt-5.4-mini<br/>agent model]
            nano[gpt-5.4-nano<br/>fast / compare]
            ci[Code Interpreter<br/>sandbox]
        end
        appi[Application Insights<br/>appi-foundrydemo-dev]
        log[(Log Analytics<br/>log-foundrydemo-dev)]
    end

    mcp[Microsoft Learn MCP server<br/>learn.microsoft.com/api/mcp]

    user -- HTTPS --> app
    app -. uses .-> uami
    uami -- AcrPull --> acr
    uami -- Azure AI User --> foundry
    app -- Responses API<br/>Entra ID token --> project
    project --> mini
    project --> nano
    project -- MCP tool --> mcp
    project -- tool --> ci
    app -- OpenTelemetry --> appi
    appi --> log
    cae -- logs --> log
    actions -- Bicep deployment --> rg
    actions -- docker push --> acr
    actions -- new revision --> app
```

| Component | Purpose |
| --- | --- |
| Container App | Serves the SPA and the API (`/api/agent/chat`, `/api/models/compare`, `/api/history`, `/api/info`, `/health/*`). Scales to zero. The Container Apps environment is deployed to `appLocation` (parameter, defaults to `location`). The dev environment uses `francecentral` because Container Apps capacity in `swedencentral` was constrained (`AKSCapacityHeavyUsage`). Foundry, ACR, and monitoring stay in `swedencentral`. |
| User-assigned managed identity | Pulls the image (AcrPull) and calls Foundry (Azure AI User). `AZURE_CLIENT_ID` selects it for `DefaultAzureCredential`. |
| Foundry resource + project | Kind `AIServices`, `allowProjectManagement: true`, `disableLocalAuth: true`. Hosts the `foundry-guide` agent and both model deployments. |
| Microsoft Learn MCP server | Public, read-only documentation tools for grounding ([ADR-0005](adr/0005-mcp-tool-microsoft-learn.md)). |
| Code Interpreter | Sandboxed Python for calculations and charts ([ADR-0004](adr/0004-preview-features.md)). |
| Application Insights / Log Analytics | Traces (including OpenAI/agent spans), logs, and metrics. |
| GitHub Actions | CI (lint, type check, test, build, Bicep lint), deployment, and deck publishing ([ADR-0003](adr/0003-github-actions-azure-auth-exception.md) for Azure auth). |

## Agent chat request

```mermaid
sequenceDiagram
    autonumber
    actor U as Presenter (browser)
    participant SPA as Vue SPA
    participant API as FastAPI (Container App)
    participant ID as Managed identity (Entra ID)
    participant P as Foundry project (Responses API)
    participant A as Agent foundry-guide (gpt-5.4-mini)
    participant M as Microsoft Learn MCP
    participant AI as Application Insights

    U->>SPA: Type a question, click Send
    SPA->>API: POST /api/agent/chat {message, conversation_id?}
    API->>ID: DefaultAzureCredential.get_token()
    ID-->>API: Entra ID access token
    opt first message of a conversation
        API->>P: conversations.create()
        P-->>API: conversation_id
    end
    API->>P: responses.create(input, conversation,<br/>agent reference foundry-guide)
    P->>A: Run agent with conversation history
    A->>M: MCP tool call (search / fetch docs)
    M-->>A: Documentation excerpts
    opt calculation or chart needed
        A->>A: Code Interpreter
    end
    A-->>P: Final answer
    P-->>API: Response (output text, tool calls, usage)
    API->>AI: Spans, latency, token usage
    API->>API: Append run to in-memory history (last 200)
    API-->>SPA: {text, conversation_id, tool_calls, usage, latency_ms}
    SPA-->>U: Render answer with tool-call chips
```

## Configuration

The app reads its configuration from environment variables (see [`.env.example`](../.env.example)):
`FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL_DEPLOYMENT`, `FOUNDRY_FAST_MODEL_DEPLOYMENT`, `FOUNDRY_AGENT_NAME`,
`AZURE_CLIENT_ID`, `APPLICATIONINSIGHTS_CONNECTION_STRING`, and `APP_VERSION`. Bicep sets them on the Container App;
the deploy workflow sets `APP_VERSION` to the git SHA.
