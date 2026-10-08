"""HTTP routes: health probes and the /api surface."""

from __future__ import annotations

import asyncio
import logging
import mimetypes
import re
import time
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse, Response

from .agent_definition import TOOL_LABELS
from .errors import UPSTREAM_EXCEPTIONS, NotFoundError, ServiceNotReadyError, UpstreamError, describe_upstream_error
from .foundry_client import FoundryGateway
from .history import HISTORY_CAPACITY
from .response_parsing import parse_response
from .runtime import AgentStatus, Runtime
from .schemas import (
    AgentInfo,
    ChatRequest,
    ChatResponse,
    CompareRequest,
    CompareResponse,
    ErrorResponse,
    HistoryResponse,
    InfoResponse,
    ModelResult,
    ModelsInfo,
)

logger = logging.getLogger(__name__)

_ID_RE = re.compile(r"^[A-Za-z0-9_\-]{1,200}$")
_SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9._\-]")
_ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    502: {"model": ErrorResponse, "description": "Microsoft Foundry call failed"},
    503: {"model": ErrorResponse, "description": "Foundry not configured or agent not ready"},
}


def get_runtime(request: Request) -> Runtime:
    runtime: Runtime = request.app.state.runtime
    return runtime


RuntimeDep = Annotated[Runtime, Depends(get_runtime)]

health_router = APIRouter(prefix="/health", tags=["health"])
api_router = APIRouter(prefix="/api", tags=["api"])


def _elapsed_ms(start: float) -> int:
    return int((time.perf_counter() - start) * 1000)


def _require_gateway(runtime: Runtime) -> FoundryGateway:
    if runtime.gateway is None:
        missing = ", ".join(runtime.settings.missing_settings()) or "Foundry client"
        raise ServiceNotReadyError(f"Microsoft Foundry is not configured (missing: {missing}).")
    return runtime.gateway


@health_router.get("/live", summary="Liveness probe")
async def live() -> dict[str, str]:
    return {"status": "live"}


@health_router.get("/ready", summary="Readiness probe (configuration + agent)")
async def ready(runtime: RuntimeDep) -> JSONResponse:
    missing = runtime.settings.missing_settings()
    agent = runtime.agent.state
    checks = {
        "config": {"ok": not missing, "missing": missing},
        "agent": {
            "ok": agent.status is AgentStatus.READY,
            "name": runtime.agent.agent_name,
            "status": agent.status.value,
            "version": agent.version,
            "attempts": agent.attempts,
            "error": agent.error,
        },
    }
    is_ready = all(check["ok"] for check in checks.values())
    return JSONResponse(
        status_code=200 if is_ready else 503,
        content={"status": "ready" if is_ready else "not_ready", "checks": checks},
    )


@api_router.get("/info", response_model=InfoResponse, summary="Deployment information")
async def info(runtime: RuntimeDep) -> InfoResponse:
    settings = runtime.settings
    agent = runtime.agent.state
    return InfoResponse(
        app_version=settings.app_version,
        region=settings.azure_region,
        endpoint_host=settings.endpoint_host,
        project_name=settings.project_name,
        configured=settings.is_configured,
        telemetry_enabled=runtime.telemetry_enabled,
        models=ModelsInfo(primary=settings.foundry_model_deployment, fast=settings.foundry_fast_model_deployment),
        agent=AgentInfo(
            name=settings.foundry_agent_name,
            version=agent.version,
            status=agent.status.value,
            error=agent.error,
            tools=TOOL_LABELS,
        ),
    )


@api_router.post("/agent/chat", response_model=ChatResponse, responses=_ERROR_RESPONSES, summary="Chat with the agent")
async def chat(body: ChatRequest, runtime: RuntimeDep) -> ChatResponse:
    gateway = _require_gateway(runtime)
    state = runtime.agent.state
    if state.status is not AgentStatus.READY:
        detail = f" Last error: {state.error}" if state.error else ""
        raise ServiceNotReadyError(f"The agent is not ready yet (status: {state.status.value}).{detail}")

    agent_name = runtime.agent.agent_name
    target = f"{agent_name}:{state.version}" if state.version else agent_name
    start = time.perf_counter()
    try:
        conversation_id: str
        if body.conversation_id:
            conversation_id = body.conversation_id
        else:
            conversation_id = await asyncio.to_thread(gateway.create_conversation)
        response = await asyncio.to_thread(
            gateway.respond_with_agent, agent_name, state.version, body.message, conversation_id
        )
    except UPSTREAM_EXCEPTIONS as exc:
        message = describe_upstream_error(exc)
        runtime.history.record(
            kind="agent", target=target, prompt=body.message, latency_ms=_elapsed_ms(start), error=message
        )
        logger.warning(
            "agent_chat_failed",
            extra={"event": "agent_chat_failed", "error": message, "error_type": type(exc).__name__},
        )
        raise UpstreamError(message) from exc

    latency_ms = _elapsed_ms(start)
    parsed = parse_response(response)
    for generated in parsed.files:
        runtime.files.register(generated.container_id, generated.file_id, generated.filename)
    runtime.history.record(
        kind="agent",
        target=target,
        prompt=body.message,
        latency_ms=latency_ms,
        usage=parsed.usage,
        tool_calls=len(parsed.tool_calls),
    )
    logger.info(
        "agent_chat_completed",
        extra={
            "event": "agent_chat_completed",
            "latency_ms": latency_ms,
            "tool_calls": len(parsed.tool_calls),
            "total_tokens": parsed.usage.total_tokens,
        },
    )
    return ChatResponse(
        text=parsed.text,
        conversation_id=conversation_id,
        response_id=parsed.response_id,
        agent_name=agent_name,
        agent_version=state.version,
        tool_calls=parsed.tool_calls,
        citations=parsed.citations,
        files=parsed.files,
        usage=parsed.usage,
        latency_ms=latency_ms,
    )


async def _run_model(
    runtime: Runtime, gateway: FoundryGateway, role: Literal["primary", "fast"], deployment: str, prompt: str
) -> ModelResult:
    start = time.perf_counter()
    try:
        response = await asyncio.to_thread(gateway.respond_with_model, deployment, prompt)
    except UPSTREAM_EXCEPTIONS as exc:
        message = describe_upstream_error(exc)
        latency_ms = _elapsed_ms(start)
        runtime.history.record(kind="compare", target=deployment, prompt=prompt, latency_ms=latency_ms, error=message)
        logger.warning(
            "model_call_failed",
            extra={"event": "model_call_failed", "model": deployment, "error": message},
        )
        return ModelResult(model=deployment, role=role, output="", latency_ms=latency_ms, error=message)
    latency_ms = _elapsed_ms(start)
    parsed = parse_response(response)
    runtime.history.record(kind="compare", target=deployment, prompt=prompt, latency_ms=latency_ms, usage=parsed.usage)
    return ModelResult(
        model=deployment,
        role=role,
        output=parsed.text,
        latency_ms=latency_ms,
        input_tokens=parsed.usage.input_tokens,
        output_tokens=parsed.usage.output_tokens,
        total_tokens=parsed.usage.total_tokens,
    )


@api_router.post(
    "/models/compare", response_model=CompareResponse, responses=_ERROR_RESPONSES, summary="Compare two models"
)
async def compare(body: CompareRequest, runtime: RuntimeDep) -> CompareResponse:
    gateway = _require_gateway(runtime)
    settings = runtime.settings
    results = await asyncio.gather(
        _run_model(runtime, gateway, "primary", settings.foundry_model_deployment, body.prompt),
        _run_model(runtime, gateway, "fast", settings.foundry_fast_model_deployment, body.prompt),
    )
    if all(result.error for result in results):
        raise UpstreamError(f"Both model calls failed. {results[0].error}")
    return CompareResponse(prompt=body.prompt, results=list(results))


@api_router.get("/history", response_model=HistoryResponse, summary="Recent runs (newest first)")
async def history(
    runtime: RuntimeDep, limit: Annotated[int, Query(ge=1, le=HISTORY_CAPACITY)] = HISTORY_CAPACITY
) -> HistoryResponse:
    items = runtime.history.list(limit)
    return HistoryResponse(items=items, count=len(items), capacity=runtime.history.capacity)


@api_router.get(
    "/files/{container_id}/{file_id}", responses=_ERROR_RESPONSES, summary="Download a Code Interpreter file"
)
async def download_file(container_id: str, file_id: str, runtime: RuntimeDep) -> Response:
    if not (_ID_RE.match(container_id) and _ID_RE.match(file_id)):
        raise NotFoundError("File not found.")
    filename = runtime.files.get(container_id, file_id)
    if filename is None:
        raise NotFoundError("File not found.")
    gateway = _require_gateway(runtime)
    try:
        content = await asyncio.to_thread(gateway.get_container_file, container_id, file_id)
    except UPSTREAM_EXCEPTIONS as exc:
        raise UpstreamError(describe_upstream_error(exc)) from exc
    safe_name = _SAFE_FILENAME_RE.sub("_", filename.rsplit("/", 1)[-1]) or "file"
    media_type = mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
    disposition = "inline" if media_type.startswith("image/") else "attachment"
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'{disposition}; filename="{safe_name}"',
            "Cache-Control": "private, max-age=3600",
        },
    )
