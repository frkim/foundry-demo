"""Definition of the "Foundry Guide" prompt agent (Microsoft Foundry Agent Service, azure-ai-projects 2.x)."""

from __future__ import annotations

import hashlib
import json

from azure.ai.projects.models import (
    AutoCodeInterpreterToolParam,
    CodeInterpreterTool,
    MCPTool,
    PromptAgentDefinition,
)

LEARN_MCP_SERVER_LABEL = "microsoft_learn"
LEARN_MCP_SERVER_URL = "https://learn.microsoft.com/api/mcp"
AGENT_DESCRIPTION = "Foundry Guide - answers Microsoft Foundry questions with Microsoft Learn MCP and Code Interpreter."
FINGERPRINT_METADATA_KEY = "definition_sha256"

AGENT_INSTRUCTIONS = """You are **Foundry Guide**, a friendly expert on Microsoft Foundry (the new Foundry resource,
Foundry projects, Foundry Models, Foundry Agent Service, the Responses API, evaluations, observability and
governance).

Rules:
- Ground every factual answer about Microsoft products in Microsoft Learn: call the `microsoft_learn` MCP tools
  (search, then fetch when you need detail) and cite the Learn URLs you used as Markdown links.
- Always describe Microsoft Foundry (new). Never recommend Foundry (classic) hub-based projects, the Assistants API,
  `azure-ai-inference` or API keys; prefer Microsoft Entra ID with managed identities.
- Use the Code Interpreter tool for any arithmetic, cost estimate, data analysis or chart. Show the key numbers in a
  Markdown table, and when you draw a chart save it as a PNG file.
- Be concise: short paragraphs, bullet points, and code blocks when helpful. Say so when you are not sure.
"""


def build_agent_definition(model_deployment: str) -> PromptAgentDefinition:
    """Build the prompt agent definition: Microsoft Learn MCP server + Code Interpreter."""
    return PromptAgentDefinition(
        model=model_deployment,
        instructions=AGENT_INSTRUCTIONS,
        tools=[
            MCPTool(
                server_label=LEARN_MCP_SERVER_LABEL,
                server_url=LEARN_MCP_SERVER_URL,
                require_approval="never",
            ),
            CodeInterpreterTool(container=AutoCodeInterpreterToolParam()),
        ],
    )


def definition_fingerprint(definition: PromptAgentDefinition) -> str:
    """Stable SHA-256 of the definition, stored in agent metadata to make version creation idempotent."""
    canonical = json.dumps(definition.as_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


TOOL_LABELS = [f"MCP: {LEARN_MCP_SERVER_LABEL} ({LEARN_MCP_SERVER_URL})", "Code Interpreter"]
