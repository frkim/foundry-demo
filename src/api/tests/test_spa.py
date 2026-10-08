from __future__ import annotations

from collections.abc import Callable

from fastapi.testclient import TestClient

from foundry_demo.config import Settings
from foundry_demo.main import create_app


def test_should_serve_index_at_root(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "<div id='app'>" in response.text
    assert response.headers["cache-control"] == "no-cache"


def test_should_fallback_to_index_for_client_routes(client: TestClient) -> None:
    response = client.get("/history/some/deep/link")

    assert response.status_code == 200
    assert "<div id='app'>" in response.text


def test_should_serve_static_assets(client: TestClient) -> None:
    response = client.get("/assets/app.js")

    assert response.status_code == 200
    assert "console.log" in response.text
    assert "immutable" in response.headers["cache-control"]


def test_should_not_serve_files_outside_static_dir(client: TestClient) -> None:
    response = client.get("/..%2Fsecret.txt")

    assert "top secret" not in response.text


def test_should_return_404_for_unknown_api_routes(client: TestClient) -> None:
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/json")


def test_should_return_404_when_ui_not_built(make_settings: Callable[..., Settings], tmp_path_factory) -> None:  # type: ignore[no-untyped-def]
    empty = tmp_path_factory.mktemp("empty")
    app = create_app(make_settings(static_dir=str(empty), foundry_project_endpoint=""))

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 404
    assert "Web UI not found" in response.json()["detail"]


def test_should_serve_openapi_under_api_prefix(client: TestClient) -> None:
    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    assert "/api/agent/chat" in response.json()["paths"]
