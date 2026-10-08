from __future__ import annotations

from collections.abc import Callable

from azure.core.exceptions import ClientAuthenticationError
from fastapi.testclient import TestClient

from foundry_demo.config import Settings
from foundry_demo.main import create_app

from .conftest import FakeGateway, wait_for_agent


def test_should_return_live_when_app_is_running(unconfigured_client: TestClient) -> None:
    response = unconfigured_client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "live"}


def test_should_report_not_ready_when_config_missing(unconfigured_client: TestClient) -> None:
    response = unconfigured_client.get("/health/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["checks"]["config"] == {"ok": False, "missing": ["FOUNDRY_PROJECT_ENDPOINT"]}
    assert body["checks"]["agent"]["status"] == "not_configured"


def test_should_report_ready_when_agent_created(client: TestClient, gateway: FakeGateway) -> None:
    response = client.get("/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["checks"]["agent"]["version"] == "3"
    assert gateway.ensure_calls[0][0] == "foundry-guide"


def test_should_stay_up_and_report_error_when_agent_creation_fails(
    make_settings: Callable[..., Settings], gateway: FakeGateway
) -> None:
    gateway.ensure_error = ClientAuthenticationError("no token")
    app = create_app(make_settings(), gateway=gateway)

    with TestClient(app) as client:
        body = wait_for_agent(client)
        live = client.get("/health/live")
        ready = client.get("/health/ready")

    assert live.status_code == 200
    assert ready.status_code == 503
    assert body["checks"]["agent"]["status"] == "error"
    assert "Authentication to Microsoft Foundry failed" in body["checks"]["agent"]["error"]
    assert gateway.closed is True


def test_should_skip_bootstrap_when_disabled(make_settings: Callable[..., Settings], gateway: FakeGateway) -> None:
    app = create_app(make_settings(foundry_agent_bootstrap=False), gateway=gateway)

    with TestClient(app) as client:
        response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["checks"]["agent"]["status"] == "pending"
    assert gateway.ensure_calls == []
