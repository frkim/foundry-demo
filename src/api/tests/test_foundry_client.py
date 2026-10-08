from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock

from azure.core.exceptions import ResourceNotFoundError

from foundry_demo.agent_definition import (
    FINGERPRINT_METADATA_KEY,
    LEARN_MCP_SERVER_URL,
    build_agent_definition,
    definition_fingerprint,
)
from foundry_demo.foundry_client import FoundryClient


def _client(project: MagicMock, openai: MagicMock) -> FoundryClient:
    client = FoundryClient.__new__(FoundryClient)
    client._project = project
    client._openai = openai
    client._credential = MagicMock()
    client._timeout = 30.0
    return client


def test_should_define_prompt_agent_with_mcp_and_code_interpreter() -> None:
    definition = build_agent_definition("gpt-5.4-mini").as_dict()

    assert definition["kind"] == "prompt"
    assert definition["model"] == "gpt-5.4-mini"
    tools = definition["tools"]
    assert tools[0] == {
        "type": "mcp",
        "server_label": "microsoft_learn",
        "server_url": LEARN_MCP_SERVER_URL,
        "require_approval": "never",
    }
    assert tools[1] == {"type": "code_interpreter", "container": {"type": "auto"}}


def test_should_compute_stable_fingerprint() -> None:
    first = definition_fingerprint(build_agent_definition("gpt-5.4-mini"))
    second = definition_fingerprint(build_agent_definition("gpt-5.4-mini"))
    other = definition_fingerprint(build_agent_definition("gpt-5.4-nano"))

    assert first == second
    assert first != other


def test_should_reuse_latest_version_when_fingerprint_matches() -> None:
    project = MagicMock()
    project.agents.get.return_value = SimpleNamespace(
        versions=SimpleNamespace(latest=SimpleNamespace(version="7", metadata={FINGERPRINT_METADATA_KEY: "abc"}))
    )

    version, created = _client(project, MagicMock()).ensure_agent("foundry-guide", MagicMock(), "abc")

    assert (version, created) == ("7", False)
    project.agents.create_version.assert_not_called()


def test_should_create_version_when_agent_missing() -> None:
    project = MagicMock()
    project.agents.get.side_effect = ResourceNotFoundError("missing")
    project.agents.create_version.return_value = SimpleNamespace(version="1")
    definition = build_agent_definition("gpt-5.4-mini")

    version, created = _client(project, MagicMock()).ensure_agent("foundry-guide", definition, "abc")

    assert (version, created) == ("1", True)
    kwargs = project.agents.create_version.call_args.kwargs
    assert kwargs["agent_name"] == "foundry-guide"
    assert kwargs["definition"] is definition
    assert kwargs["metadata"][FINGERPRINT_METADATA_KEY] == "abc"


def test_should_create_new_version_when_definition_changed() -> None:
    project = MagicMock()
    project.agents.get.return_value = SimpleNamespace(
        versions=SimpleNamespace(latest=SimpleNamespace(version="2", metadata={FINGERPRINT_METADATA_KEY: "old"}))
    )
    project.agents.create_version.return_value = SimpleNamespace(version="3")

    assert _client(project, MagicMock()).ensure_agent("foundry-guide", MagicMock(), "new") == ("3", True)


def test_should_invoke_agent_with_agent_reference_and_conversation() -> None:
    openai = MagicMock()

    _client(MagicMock(), openai).respond_with_agent("foundry-guide", "3", "hi", "conv_1")

    openai.responses.create.assert_called_once_with(
        input="hi",
        conversation="conv_1",
        extra_body={"agent_reference": {"name": "foundry-guide", "type": "agent_reference", "version": "3"}},
        timeout=30.0,
    )


def test_should_call_model_deployment_directly() -> None:
    openai = MagicMock()

    _client(MagicMock(), openai).respond_with_model("gpt-5.4-nano", "hi")

    openai.responses.create.assert_called_once_with(model="gpt-5.4-nano", input="hi", timeout=30.0)


def test_should_create_conversation() -> None:
    openai = MagicMock()
    openai.conversations.create.return_value = SimpleNamespace(id="conv_9")

    assert _client(MagicMock(), openai).create_conversation() == "conv_9"
