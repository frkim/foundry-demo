from __future__ import annotations

from fastapi.testclient import TestClient


def test_should_return_deployment_info(client: TestClient) -> None:
    response = client.get("/api/info")

    assert response.status_code == 200
    body = response.json()
    assert body["endpoint_host"] == "aif-foundrydemo-dev-abcde.services.ai.azure.com"
    assert body["project_name"] == "proj-foundrydemo-dev"
    assert body["models"] == {"primary": "gpt-5.4-mini", "fast": "gpt-5.4-nano"}
    assert body["agent"]["name"] == "foundry-guide"
    assert body["agent"]["version"] == "3"
    assert body["agent"]["status"] == "ready"
    assert body["app_version"] == "test-sha"
    assert body["region"] == "swedencentral"
    assert body["configured"] is True
    assert body["telemetry_enabled"] is False


def test_should_return_info_when_not_configured(unconfigured_client: TestClient) -> None:
    body = unconfigured_client.get("/api/info").json()

    assert body["configured"] is False
    assert body["endpoint_host"] is None
    assert body["agent"]["status"] == "not_configured"


def test_should_set_security_and_correlation_headers(client: TestClient) -> None:
    response = client.get("/api/info", headers={"x-correlation-id": "abcdef12-3456"})

    assert response.headers["x-correlation-id"] == "abcdef12-3456"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "default-src 'self'" in response.headers["content-security-policy"]
