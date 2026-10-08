"""Structured JSON logging with a per-request correlation id."""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)

_RESERVED = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {"message", "asctime", "color_message"}


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON documents."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "event": getattr(record, "event", None) or record.getMessage(),
            "message": record.getMessage(),
        }
        correlation_id = correlation_id_var.get()
        if correlation_id:
            payload["correlation_id"] = correlation_id
        for key, value in record.__dict__.items():
            if key not in _RESERVED and key != "event" and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Route the root logger (and uvicorn's loggers) through a single JSON handler on stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())
    for name in ("uvicorn", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True
    # Requests are logged by our own middleware with a correlation id.
    logging.getLogger("uvicorn.access").disabled = True
    for noisy in ("azure.core.pipeline.policies.http_logging_policy", "azure.identity", "httpx", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
