from __future__ import annotations

from fastapi.testclient import TestClient
from openai import OpenAIError

from .conftest import FakeGateway


def test_should_call_both_models_when_comparing(client: TestClient, gateway: FakeGateway) -> None:
    response = client.post("/api/models/compare", json={"prompt": "Hello"})

    assert response.status_code == 200
    results = response.json()["results"]
    assert [r["model"] for r in results] == ["gpt-5.4-mini", "gpt-5.4-nano"]
    assert [r["role"] for r in results] == ["primary", "fast"]
    assert results[0]["output"] == "answer from gpt-5.4-mini"
    assert results[1]["input_tokens"] == 7
    assert results[1]["output_tokens"] == 3
    assert results[1]["total_tokens"] == 10
    assert sorted(call[0] for call in gateway.model_calls) == ["gpt-5.4-mini", "gpt-5.4-nano"]


def test_should_return_partial_results_when_one_model_fails(client: TestClient, gateway: FakeGateway) -> None:
    gateway.model_errors["gpt-5.4-nano"] = OpenAIError("quota exceeded")

    response = client.post("/api/models/compare", json={"prompt": "Hello"})

    assert response.status_code == 200
    results = response.json()["results"]
    assert results[0]["error"] is None
    assert "quota exceeded" in results[1]["error"]


def test_should_return_502_when_both_models_fail(client: TestClient, gateway: FakeGateway) -> None:
    gateway.model_errors = {"gpt-5.4-mini": OpenAIError("down"), "gpt-5.4-nano": OpenAIError("down")}

    response = client.post("/api/models/compare", json={"prompt": "Hello"})

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "upstream_error"


def test_should_reject_compare_prompt_when_too_long(client: TestClient) -> None:
    response = client.post("/api/models/compare", json={"prompt": "x" * 4001})

    assert response.status_code == 422
