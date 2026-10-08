"""Application runtime state: agent lifecycle (background bootstrap), run history and generated-file registry."""

from __future__ import annotations

import asyncio
import logging
import threading
from collections import OrderedDict
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from .agent_definition import build_agent_definition, definition_fingerprint
from .config import Settings
from .errors import describe_upstream_error
from .foundry_client import FoundryGateway
from .history import RunHistory

logger = logging.getLogger(__name__)


class AgentStatus(StrEnum):
    NOT_CONFIGURED = "not_configured"
    PENDING = "pending"
    CREATING = "creating"
    READY = "ready"
    ERROR = "error"


@dataclass
class AgentState:
    status: AgentStatus
    version: str | None = None
    created: bool | None = None
    error: str | None = None
    attempts: int = 0
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=UTC))


class AgentManager:
    """Creates (or reuses) the agent version in the background with exponential backoff; never raises."""

    def __init__(
        self,
        gateway: FoundryGateway | None,
        agent_name: str,
        model_deployment: str,
        *,
        retry_initial_seconds: float = 2.0,
        retry_max_seconds: float = 60.0,
    ) -> None:
        self._gateway = gateway
        self.agent_name = agent_name
        self._model = model_deployment
        self._retry_initial = retry_initial_seconds
        self._retry_max = retry_max_seconds
        self._state = AgentState(status=AgentStatus.PENDING if gateway else AgentStatus.NOT_CONFIGURED)

    @property
    def state(self) -> AgentState:
        return self._state

    @property
    def is_ready(self) -> bool:
        return self._state.status is AgentStatus.READY

    def _set(self, **changes: Any) -> None:
        self._state = replace(self._state, updated_at=datetime.now(tz=UTC), **changes)

    async def bootstrap(self) -> None:
        if self._gateway is None:
            return
        definition = build_agent_definition(self._model)
        fingerprint = definition_fingerprint(definition)
        delay = self._retry_initial
        while True:
            self._set(status=AgentStatus.CREATING, attempts=self._state.attempts + 1)
            try:
                version, created = await asyncio.to_thread(
                    self._gateway.ensure_agent, self.agent_name, definition, fingerprint
                )
            except Exception as exc:  # never crash the app on bootstrap failures
                message = describe_upstream_error(exc)
                self._set(status=AgentStatus.ERROR, error=message)
                logger.warning(
                    "agent_bootstrap_failed",
                    extra={
                        "event": "agent_bootstrap_failed",
                        "agent_name": self.agent_name,
                        "error": message,
                        "error_type": type(exc).__name__,
                        "error_detail": str(exc)[:500],
                        "retry_in_seconds": delay,
                    },
                )
                await asyncio.sleep(delay)
                delay = min(delay * 2, self._retry_max)
                continue
            self._set(status=AgentStatus.READY, version=version, created=created, error=None)
            logger.info(
                "agent_ready",
                extra={"event": "agent_ready", "agent_name": self.agent_name, "version": version, "created": created},
            )
            return


class FileRegistry:
    """Bounded allow-list of Code Interpreter files produced by this app, so only those can be downloaded."""

    def __init__(self, capacity: int = 500) -> None:
        self._capacity = capacity
        self._items: OrderedDict[tuple[str, str], str] = OrderedDict()
        self._lock = threading.Lock()

    def register(self, container_id: str, file_id: str, filename: str) -> None:
        with self._lock:
            self._items[(container_id, file_id)] = filename
            self._items.move_to_end((container_id, file_id))
            while len(self._items) > self._capacity:
                self._items.popitem(last=False)

    def get(self, container_id: str, file_id: str) -> str | None:
        with self._lock:
            return self._items.get((container_id, file_id))


@dataclass
class Runtime:
    settings: Settings
    gateway: FoundryGateway | None
    agent: AgentManager
    history: RunHistory
    files: FileRegistry
    telemetry_enabled: bool = False
