# ADR-0005: Give the agent the public Microsoft Learn MCP server

- Status: Accepted
- Date: 2026-10-08

## Context

The `foundry-guide` agent answers questions about Microsoft Foundry and must ground its answers in current official
documentation, which the model's training data may not cover. Foundry Agent Service supports remote MCP servers
through the MCP tool. Microsoft publishes a public, read-only
[Microsoft Learn MCP server](https://learn.microsoft.com/training/support/mcp) at
`https://learn.microsoft.com/api/mcp` that searches and fetches Microsoft Learn content and requires no
authentication.

The MCP tool's `require_approval` defaults to `always`, which pauses each run until the client approves the tool
call. Microsoft guidance is to require approval for high-risk tools, especially those that write data or change
resources.

## Decision

Attach the MCP tool to the agent definition:

```python
MCPTool(
    server_label="microsoft_learn",
    server_url="https://learn.microsoft.com/api/mcp",
    require_approval="never",
)
```

`require_approval="never"` is acceptable here because the server:

- exposes only **read-only** search and fetch tools over **public** documentation,
- needs **no credentials**, so no secret or token is sent to it,
- cannot change data or resources in any system.

The only data sent to the server is the search query derived from the user's prompt; the demo handles public data
only (`dataClassification=public`), and presenters must not enter confidential information.

## Consequences

- Positive: grounded, up-to-date answers with citations and no approval round-trip, which keeps the live demo fluid.
- Positive: shows the MCP tool and the tool-call chips in the UI.
- Negative: prompt-derived queries leave the tenant boundary to a Microsoft public endpoint; acceptable for public data.
- Negative: answers depend on the server's availability and tool schema — see the fallback in
  [ADR-0004](0004-preview-features.md).
- Follow-up: any MCP server that is authenticated, writes data, or is not Microsoft-operated must use
  `require_approval="always"` (or an allow-list) and get its own ADR; consider governing MCP traffic through the AI
  Gateway (API Management).

## Alternatives considered

- **`require_approval="always"`** with an approval step in the UI — safer by default but adds friction and code with
  no security benefit for a read-only public server.
- **Bing grounding / web search tool** — broader, less authoritative results for Microsoft product questions.
- **File search over a copied docs corpus** — goes stale and adds storage and indexing cost.
