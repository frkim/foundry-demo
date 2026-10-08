from __future__ import annotations

from types import SimpleNamespace

import pytest
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError, ServiceRequestError
from openai import OpenAIError

from foundry_demo.config import Settings
from foundry_demo.errors import describe_upstream_error
from foundry_demo.response_parsing import extract_text, parse_response


def test_should_fallback_to_message_content_when_output_text_missing() -> None:
    response = SimpleNamespace(
        output=[SimpleNamespace(type="message", content=[SimpleNamespace(text="a"), SimpleNamespace(text="b")])]
    )

    assert extract_text(response) == "ab"


def test_should_handle_response_without_usage_or_output() -> None:
    parsed = parse_response(SimpleNamespace(id="r1", output_text="", output=None, usage=None))

    assert parsed.text == ""
    assert parsed.tool_calls == []
    assert parsed.usage.total_tokens is None


def test_should_capture_unknown_tool_call_types() -> None:
    parsed = parse_response(SimpleNamespace(output=[SimpleNamespace(type="web_search_call", status="completed")]))

    assert parsed.tool_calls[0].type == "web_search_call"


@pytest.mark.parametrize(
    ("exc", "expected"),
    [
        (ClientAuthenticationError("x"), "Authentication to Microsoft Foundry failed"),
        (HttpResponseError(message="deployment missing"), "deployment missing"),
        (ServiceRequestError("dns failure"), "Could not connect to Microsoft Foundry"),
        (OpenAIError("boom"), "boom"),
        (RuntimeError("secret internals"), "Unexpected error"),
    ],
)
def test_should_describe_upstream_errors_safely(exc: Exception, expected: str) -> None:
    assert expected in describe_upstream_error(exc)


def test_should_list_missing_settings() -> None:
    settings = Settings(_env_file=None, foundry_project_endpoint="http://not-a-project", foundry_agent_name=" ")

    assert settings.missing_settings() == ["FOUNDRY_PROJECT_ENDPOINT", "FOUNDRY_AGENT_NAME"]
    assert settings.is_configured is False
