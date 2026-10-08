"""FastAPI application factory and ASGI entry point (`uvicorn foundry_demo.main:app`)."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import re
import time
import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

from . import __version__
from .config import Settings
from .errors import AppError
from .foundry_client import FoundryClient, FoundryGateway
from .history import RunHistory
from .logging_config import configure_logging, correlation_id_var
from .routes import api_router, health_router
from .runtime import AgentManager, FileRegistry, Runtime
from .schemas import ErrorBody, ErrorResponse
from .spa import register_spa
from .telemetry import configure_telemetry

logger = logging.getLogger("foundry_demo")

_CORRELATION_RE = re.compile(r"^[A-Za-z0-9\-]{8,64}$")
CONTENT_SECURITY_POLICY = (
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
    "font-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
)


def _error_response(status_code: int, code: str, message: str, request: Request) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", None)
    body = ErrorResponse(error=ErrorBody(code=code, message=message, correlation_id=correlation_id))
    return JSONResponse(status_code=status_code, content=body.model_dump())


def _build_gateway(settings: Settings) -> FoundryGateway | None:
    if not settings.is_configured:
        logger.warning(
            "foundry_not_configured",
            extra={"event": "foundry_not_configured", "missing": settings.missing_settings()},
        )
        return None
    try:
        return FoundryClient(settings.foundry_project_endpoint, settings.request_timeout_seconds)
    except Exception:
        logger.exception("foundry_client_init_failed", extra={"event": "foundry_client_init_failed"})
        return None


def create_app(settings: Settings | None = None, gateway: FoundryGateway | None = None) -> FastAPI:
    """Build the application. Pass `gateway` to inject a fake Foundry gateway (tests)."""
    settings = settings or Settings()
    configure_logging(settings.log_level)
    telemetry_enabled = configure_telemetry(settings)
    if gateway is None:
        gateway = _build_gateway(settings)
    runtime = Runtime(
        settings=settings,
        gateway=gateway,
        agent=AgentManager(gateway, settings.foundry_agent_name, settings.foundry_model_deployment),
        history=RunHistory(),
        files=FileRegistry(),
        telemetry_enabled=telemetry_enabled,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        logger.info(
            "app_starting",
            extra={"event": "app_starting", "app_version": settings.app_version, "configured": settings.is_configured},
        )
        task: asyncio.Task[None] | None = None
        if runtime.gateway is not None and settings.foundry_agent_bootstrap:
            task = asyncio.create_task(runtime.agent.bootstrap(), name="agent-bootstrap")
        try:
            yield
        finally:
            if task is not None:
                task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await task
            if runtime.gateway is not None:
                runtime.gateway.close()
            logger.info("app_stopped", extra={"event": "app_stopped"})

    app = FastAPI(
        title="Foundry Guide API",
        version=__version__,
        description="Microsoft Foundry Agent Service demo: agent chat, model compare and run history.",
        docs_url="/api/docs",
        redoc_url=None,
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    app.state.runtime = runtime

    @app.middleware("http")
    async def correlation_and_security(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        incoming = request.headers.get("x-correlation-id", "")
        correlation_id = incoming if _CORRELATION_RE.match(incoming) else uuid.uuid4().hex
        request.state.correlation_id = correlation_id
        token = correlation_id_var.set(correlation_id)
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception("request_failed", extra={"event": "request_failed", "path": request.url.path})
            raise
        finally:
            correlation_id_var.reset(token)
        duration_ms = int((time.perf_counter() - start) * 1000)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        if not request.url.path.startswith("/api/docs"):
            response.headers["Content-Security-Policy"] = CONTENT_SECURITY_POLICY
        if not request.url.path.startswith("/health"):
            logger.info(
                "http_request",
                extra={
                    "event": "http_request",
                    "correlation_id": correlation_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
        return response

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(exc.status_code, exc.code, exc.message, request)

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        return _error_response(500, "internal_error", "An unexpected error occurred.", request)

    app.include_router(health_router)
    app.include_router(api_router)
    register_spa(app, Path(settings.static_dir))
    return app


app = create_app()
