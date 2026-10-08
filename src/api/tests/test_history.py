from __future__ import annotations

from fastapi.testclient import TestClient

from foundry_demo.history import RunHistory
from foundry_demo.schemas import Usage


def test_should_list_runs_newest_first(client: TestClient) -> None:
    client.post("/api/agent/chat", json={"message": "first"})
    client.post("/api/models/compare", json={"prompt": "second"})

    body = client.get("/api/history").json()

    assert body["count"] == 3
    assert body["capacity"] == 200
    kinds = [item["kind"] for item in body["items"]]
    assert kinds[-1] == "agent"
    assert set(kinds[:2]) == {"compare"}
    assert body["items"][-1]["prompt_preview"] == "first"
    assert body["items"][-1]["target"] == "foundry-guide:3"
    assert body["items"][-1]["total_tokens"] == 15


def test_should_limit_history_results(client: TestClient) -> None:
    client.post("/api/models/compare", json={"prompt": "x"})

    body = client.get("/api/history", params={"limit": 1}).json()

    assert body["count"] == 1


def test_should_reject_invalid_limit(client: TestClient) -> None:
    assert client.get("/api/history", params={"limit": 0}).status_code == 422
    assert client.get("/api/history", params={"limit": 201}).status_code == 422


def test_should_keep_only_capacity_runs() -> None:
    history = RunHistory(capacity=200)
    for index in range(250):
        history.record(kind="agent", target="a", prompt=str(index), latency_ms=1, usage=Usage())

    items = history.list()

    assert len(items) == 200
    assert items[0].prompt_preview == "249"
    assert items[-1].prompt_preview == "50"


def test_should_truncate_long_prompt_preview() -> None:
    history = RunHistory()

    record = history.record(kind="compare", target="m", prompt="y" * 500, latency_ms=1, error="boom")

    assert len(record.prompt_preview) == 120
    assert record.status == "error"
