"""In-memory, bounded history of agent and model runs (newest first)."""

from __future__ import annotations

import threading
import uuid
from collections import deque
from datetime import UTC, datetime
from typing import Literal

from .schemas import RunRecord, Usage

HISTORY_CAPACITY = 200
PREVIEW_LENGTH = 120


class RunHistory:
    """Thread-safe ring buffer of the last `capacity` runs."""

    def __init__(self, capacity: int = HISTORY_CAPACITY) -> None:
        self.capacity = capacity
        self._items: deque[RunRecord] = deque(maxlen=capacity)
        self._lock = threading.Lock()

    def record(
        self,
        *,
        kind: Literal["agent", "compare"],
        target: str,
        prompt: str,
        latency_ms: int,
        usage: Usage | None = None,
        tool_calls: int = 0,
        error: str | None = None,
    ) -> RunRecord:
        usage = usage or Usage()
        preview = prompt if len(prompt) <= PREVIEW_LENGTH else prompt[: PREVIEW_LENGTH - 1] + "…"
        entry = RunRecord(
            id=uuid.uuid4().hex,
            timestamp=datetime.now(tz=UTC),
            kind=kind,
            target=target,
            prompt_preview=preview,
            latency_ms=latency_ms,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            total_tokens=usage.total_tokens,
            tool_calls=tool_calls,
            status="error" if error else "ok",
            error=error,
        )
        with self._lock:
            self._items.append(entry)
        return entry

    def list(self, limit: int | None = None) -> list[RunRecord]:
        with self._lock:
            items = list(reversed(self._items))
        return items[:limit] if limit else items

    def __len__(self) -> int:
        with self._lock:
            return len(self._items)
