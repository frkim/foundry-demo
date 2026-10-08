from __future__ import annotations

from types import SimpleNamespace

from azure.core.exceptions import HttpResponseError
from fastapi.testclient import TestClient

from .conftest import FakeGateway, make_response


def _tool_rich_response() -> SimpleNamespace:
    output = [
        SimpleNamespace(type="mcp_list_tools", server_label="microsoft_learn", tools=[]),
        SimpleNamespace(
            type="mcp_call", name="microsoft_docs_search", server_label="microsoft_learn", status="completed"
        ),
        SimpleNamespace(type="code_interpreter_call", status="completed", code="print(1)"),
        SimpleNamespace(
            type="message",
            content=[
                SimpleNamespace(
                    type="output_text",
                    text="See chart",
                    annotations=[
                        SimpleNamespace(
                            type="url_citation", url="https://learn.microsoft.com/azure/foundry", title="Foundry"
                        ),
                        SimpleNamespace(
                            type="container_file_citation",
                            container_id="cntr_1",
                            file_id="cfile_1",
                            filename="chart.png",
                        ),
                    ],
                )
            ],
        ),
    ]
    return make_response(text="See chart", output=output, usage=(100, 50))


def test_should_answer_and_return_tool_calls_when_agent_succeeds(client: TestClient, gateway: FakeGateway) -> None:
    gateway.agent_response = _tool_rich_response()

    response = client.post("/api/agent/chat", json={"message": "  What is Foundry?  "})

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "See chart"
    assert body["conversation_id"] == "conv_1"
    assert body["agent_name"] == "foundry-guide"
    assert body["agent_version"] == "3"
    assert body["usage"] == {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150}
    assert [c["type"] for c in body["tool_calls"]] == ["mcp_list_tools", "mcp_call", "code_interpreter_call"]
    assert body["tool_calls"][1] == {
        "type": "mcp_call",
        "name": "microsoft_docs_search",
        "server_label": "microsoft_learn",
        "status": "completed",
    }
    assert body["citations"] == [{"url": "https://learn.microsoft.com/azure/foundry", "title": "Foundry"}]
    assert body["files"][0]["url"] == "/api/files/cntr_1/cfile_1?filename=chart.png"
    assert body["latency_ms"] >= 0
    assert gateway.agent_calls == [
        {
            "agent_name": "foundry-guide",
            "agent_version": "3",
            "message": "What is Foundry?",
            "conversation_id": "conv_1",
        }
    ]


def test_should_reuse_conversation_when_id_provided(client: TestClient, gateway: FakeGateway) -> None:
    response = client.post("/api/agent/chat", json={"message": "follow-up", "conversation_id": "conv_existing"})

    assert response.status_code == 200
    assert response.json()["conversation_id"] == "conv_existing"
    assert gateway.conversations_created == 0


def test_should_reject_message_when_too_long(client: TestClient) -> None:
    response = client.post("/api/agent/chat", json={"message": "x" * 4001})

    assert response.status_code == 422


def test_should_reject_message_when_blank(client: TestClient) -> None:
    response = client.post("/api/agent/chat", json={"message": "   "})

    assert response.status_code == 422


def test_should_reject_conversation_id_when_malformed(client: TestClient) -> None:
    response = client.post("/api/agent/chat", json={"message": "hi", "conversation_id": "../../etc"})

    assert response.status_code == 422


def test_should_return_502_without_stack_trace_when_upstream_fails(client: TestClient, gateway: FakeGateway) -> None:
    gateway.agent_error = HttpResponseError(message="Model deployment not found")

    response = client.post("/api/agent/chat", json={"message": "hi"})

    assert response.status_code == 502
    error = response.json()["error"]
    assert error["code"] == "upstream_error"
    assert "Model deployment not found" in error["message"]
    assert error["correlation_id"]
    assert "Traceback" not in response.text
    history = client.get("/api/history").json()["items"]
    assert history[0]["status"] == "error"


def test_should_return_503_when_not_configured(unconfigured_client: TestClient) -> None:
    response = unconfigured_client.post("/api/agent/chat", json={"message": "hi"})

    assert response.status_code == 503
    assert "FOUNDRY_PROJECT_ENDPOINT" in response.json()["error"]["message"]


def test_should_download_registered_file_only(client: TestClient, gateway: FakeGateway) -> None:
    gateway.agent_response = _tool_rich_response()
    client.post("/api/agent/chat", json={"message": "chart"})

    ok = client.get("/api/files/cntr_1/cfile_1")
    unknown = client.get("/api/files/cntr_1/cfile_other")

    assert ok.status_code == 200
    assert ok.headers["content-type"] == "image/png"
    assert ok.content == gateway.file_bytes
    assert unknown.status_code == 404
