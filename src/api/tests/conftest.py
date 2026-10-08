"""Shared fixtures: a fake Foundry gateway (no Azure calls) and app factories."""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from foundry_demo.config import Settings
from foundry_demo.main import create_app

ENDPOINT = "https://aif-foundrydemo-dev-abcde.services.ai.azure.com/api/projects/proj-foundrydemo-dev"


def make_response(
    text: str = "Hello from Foundry",
    output: list[Any] | None = None,
    usage: tuple[int, int] | None = (10, 5),
    response_id: str = "resp_123",
) -> SimpleNamespace:
    return SimpleNamespace(
        id=response_id,
        output_text=text,
        output=output or [],
        usage=SimpleNamespace(input_tokens=usage[0], output_tokens=usage[1], total_tokens=sum(usage))
        if usage
        else None,
    )


class FakeGateway:
    """In-memory stand-in for FoundryClient that records calls."""

    def __init__(self) -> None:
        self.ensure_calls: list[tuple[str, str]] = []
        self.agent_calls: list[dict[str, Any]] = []
        self.model_calls: list[tuple[str, str]] = []
        self.conversations_created = 0
        self.ensure_error: Exception | None = None
        self.agent_error: Exception | None = None
        self.model_errors: dict[str, Exception] = {}
        self.agent_response: Any = make_response()
        self.file_bytes = b"\x89PNG fake"
        self.closed = False

    def ensure_agent(self, agent_name: str, definition: Any, fingerprint: str) -> tuple[str, bool]:
        self.ensure_calls.append((agent_name, fingerprint))
        if self.ensure_error:
            raise self.ensure_error
        return "3", True

    def create_conversation(self) -> str:
        self.conversations_created += 1
        return f"conv_{self.conversations_created}"

    def respond_with_agent(self, agent_name: str, agent_version: str | None, message: str, conversation_id: str) -> Any:
        self.agent_calls.append(
            {
                "agent_name": agent_name,
                "agent_version": agent_version,
                "message": message,
                "conversation_id": conversation_id,
            }
        )
        if self.agent_error:
            raise self.agent_error
        return self.agent_response

    def respond_with_model(self, deployment: str, prompt: str) -> Any:
        self.model_calls.append((deployment, prompt))
        if deployment in self.model_errors:
            raise self.model_errors[deployment]
        return make_response(text=f"answer from {deployment}", usage=(7, 3))

    def get_container_file(self, container_id: str, file_id: str) -> bytes:
        return self.file_bytes

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def static_dir(tmp_path: Path) -> Path:
    root = tmp_path / "static"
    (root / "assets").mkdir(parents=True)
    (root / "index.html").write_text("<!doctype html><div id='app'></div>", encoding="utf-8")
    (root / "assets" / "app.js").write_text("console.log('hi')", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("top secret", encoding="utf-8")
    return root


@pytest.fixture
def make_settings(static_dir: Path) -> Callable[..., Settings]:
    def factory(**overrides: Any) -> Settings:
        values: dict[str, Any] = {
            "foundry_project_endpoint": ENDPOINT,
            "foundry_model_deployment": "gpt-5.4-mini",
            "foundry_fast_model_deployment": "gpt-5.4-nano",
            "foundry_agent_name": "foundry-guide",
            "applicationinsights_connection_string": "",
            "app_version": "test-sha",
            "azure_region": "swedencentral",
            "static_dir": str(static_dir),
            "log_level": "WARNING",
        }
        values.update(overrides)
        return Settings(_env_file=None, **values)

    return factory


@pytest.fixture
def gateway() -> FakeGateway:
    return FakeGateway()


def wait_for_agent(client: TestClient, timeout: float = 3.0) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    body: dict[str, Any] = {}
    while time.monotonic() < deadline:
        body = client.get("/health/ready").json()
        if body["checks"]["agent"]["status"] in {"ready", "error"}:
            return body
        time.sleep(0.02)
    return body


@pytest.fixture
def client(make_settings: Callable[..., Settings], gateway: FakeGateway) -> Iterator[TestClient]:
    app = create_app(make_settings(), gateway=gateway)
    with TestClient(app) as test_client:
        wait_for_agent(test_client)
        yield test_client


@pytest.fixture
def unconfigured_client(make_settings: Callable[..., Settings]) -> Iterator[TestClient]:
    app = create_app(make_settings(foundry_project_endpoint=""))
    with TestClient(app) as test_client:
        yield test_client
