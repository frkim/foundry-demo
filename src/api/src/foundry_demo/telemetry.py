"""Optional Azure Monitor / OpenTelemetry configuration."""

from __future__ import annotations

import logging

from .config import Settings

logger = logging.getLogger(__name__)


def configure_telemetry(settings: Settings) -> bool:
    """Enable Azure Monitor export and GenAI instrumentation when a connection string is configured.

    Must run before the FastAPI application is instantiated so the FastAPI instrumentation applies.
    Returns True when telemetry was enabled.
    """
    if not settings.telemetry_enabled:
        logger.info("telemetry_disabled", extra={"event": "telemetry_disabled"})
        return False
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(
            connection_string=settings.applicationinsights_connection_string,
            logger_name="foundry_demo",
        )
    except Exception:
        logger.exception("telemetry_configuration_failed", extra={"event": "telemetry_configuration_failed"})
        return False

    try:
        from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor

        OpenAIInstrumentor().instrument()  # type: ignore[no-untyped-call]
    except Exception:
        logger.warning("openai_instrumentation_unavailable", extra={"event": "openai_instrumentation_unavailable"})

    try:
        from azure.ai.projects.telemetry import AIProjectInstrumentor

        AIProjectInstrumentor().instrument()
    except Exception:
        logger.warning("agents_instrumentation_unavailable", extra={"event": "agents_instrumentation_unavailable"})

    logger.info("telemetry_enabled", extra={"event": "telemetry_enabled"})
    return True
