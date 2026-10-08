"""Application configuration loaded from environment variables (twelve-factor)."""

from __future__ import annotations

from functools import cached_property
from urllib.parse import urlparse

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

MAX_MESSAGE_LENGTH = 4000


class Settings(BaseSettings):
    """Runtime settings. Every field maps to an upper-case environment variable of the same name."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    foundry_project_endpoint: str = ""
    foundry_model_deployment: str = "gpt-5.4-mini"
    foundry_fast_model_deployment: str = "gpt-5.4-nano"
    foundry_agent_name: str = "foundry-guide"
    foundry_agent_bootstrap: bool = True
    applicationinsights_connection_string: str = ""
    app_version: str = "dev"
    azure_region: str = "swedencentral"
    static_dir: str = "/app/static"
    log_level: str = "INFO"
    request_timeout_seconds: float = Field(default=120.0, gt=0, le=600)

    def missing_settings(self) -> list[str]:
        """Return the names of required environment variables that are missing or invalid."""
        missing: list[str] = []
        endpoint = self.foundry_project_endpoint.strip()
        if not endpoint.startswith("https://") or "/api/projects/" not in endpoint:
            missing.append("FOUNDRY_PROJECT_ENDPOINT")
        for name in ("foundry_model_deployment", "foundry_fast_model_deployment", "foundry_agent_name"):
            if not str(getattr(self, name)).strip():
                missing.append(name.upper())
        return missing

    @property
    def is_configured(self) -> bool:
        return not self.missing_settings()

    @cached_property
    def endpoint_host(self) -> str | None:
        return urlparse(self.foundry_project_endpoint).hostname or None

    @cached_property
    def project_name(self) -> str | None:
        _, sep, tail = self.foundry_project_endpoint.partition("/api/projects/")
        return tail.strip("/").split("/")[0] or None if sep else None

    @property
    def telemetry_enabled(self) -> bool:
        return bool(self.applicationinsights_connection_string.strip())
