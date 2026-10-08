"""Thin synchronous gateway over the Foundry project client and its OpenAI (Responses API) client.

All network calls to Microsoft Foundry live here so the rest of the app can be tested with fakes.
"""

from __future__ import annotations

import logging
from typing import Any, Protocol

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from .agent_definition import AGENT_DESCRIPTION, FINGERPRINT_METADATA_KEY

logger = logging.getLogger(__name__)


class FoundryGateway(Protocol):
    """Operations the API needs from Microsoft Foundry."""

    def ensure_agent(self, agent_name: str, definition: PromptAgentDefinition, fingerprint: str) -> tuple[str, bool]:
        """Return (version, created). Reuses the latest version when its fingerprint matches."""
        ...

    def create_conversation(self) -> str: ...

    def respond_with_agent(self, agent_name: str, agent_version: str | None, message: str, conversation_id: str) -> Any:
        """Run the agent through the Responses API and return the OpenAI `Response` object."""
        ...

    def respond_with_model(self, deployment: str, prompt: str) -> Any:
        """Call a model deployment directly through the Responses API."""
        ...

    def get_container_file(self, container_id: str, file_id: str) -> bytes: ...

    def close(self) -> None: ...


class FoundryClient:
    """Production gateway: keyless (DefaultAzureCredential) access to a Foundry project."""

    def __init__(self, endpoint: str, timeout_seconds: float = 120.0) -> None:
        # DefaultAzureCredential honours AZURE_CLIENT_ID for the user-assigned managed identity.
        self._credential = DefaultAzureCredential()
        self._project = AIProjectClient(endpoint=endpoint, credential=self._credential)
        self._openai = self._project.get_openai_client()
        self._timeout = timeout_seconds

    def ensure_agent(self, agent_name: str, definition: PromptAgentDefinition, fingerprint: str) -> tuple[str, bool]:
        try:
            latest = self._project.agents.get(agent_name).versions.latest
            if (latest.metadata or {}).get(FINGERPRINT_METADATA_KEY) == fingerprint:
                return str(latest.version), False
        except ResourceNotFoundError:
            logger.info("agent_not_found", extra={"event": "agent_not_found", "agent_name": agent_name})
        created = self._project.agents.create_version(
            agent_name=agent_name,
            definition=definition,
            description=AGENT_DESCRIPTION,
            metadata={FINGERPRINT_METADATA_KEY: fingerprint, "managed_by": "foundry-demo"},
        )
        return str(created.version), True

    def create_conversation(self) -> str:
        return str(self._openai.conversations.create(timeout=self._timeout).id)

    def respond_with_agent(self, agent_name: str, agent_version: str | None, message: str, conversation_id: str) -> Any:
        agent_reference: dict[str, str] = {"name": agent_name, "type": "agent_reference"}
        if agent_version:
            agent_reference["version"] = agent_version
        return self._openai.responses.create(
            input=message,
            conversation=conversation_id,
            extra_body={"agent_reference": agent_reference},
            timeout=self._timeout,
        )

    def respond_with_model(self, deployment: str, prompt: str) -> Any:
        return self._openai.responses.create(model=deployment, input=prompt, timeout=self._timeout)

    def get_container_file(self, container_id: str, file_id: str) -> bytes:
        content = self._openai.containers.files.content.retrieve(
            file_id, container_id=container_id, timeout=self._timeout
        )
        return bytes(content.read())

    def close(self) -> None:
        for resource in (self._openai, self._project, self._credential):
            try:
                resource.close()
            except Exception:
                logger.debug("close_failed", exc_info=True)
