"""Domain errors and translation of upstream (Foundry / OpenAI / Azure) failures."""

from __future__ import annotations

from azure.core.exceptions import (
    AzureError,
    ClientAuthenticationError,
    HttpResponseError,
    ServiceRequestError,
    ServiceResponseError,
)
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAIError

UPSTREAM_EXCEPTIONS: tuple[type[Exception], ...] = (OpenAIError, AzureError)
_MAX_DETAIL = 300


class AppError(Exception):
    """Error with a safe, user-facing message and an HTTP status code."""

    status_code = 500
    code = "internal_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class UpstreamError(AppError):
    status_code = 502
    code = "upstream_error"


class ServiceNotReadyError(AppError):
    status_code = 503
    code = "not_ready"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


def _truncate(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= _MAX_DETAIL else text[: _MAX_DETAIL - 1] + "…"


def describe_upstream_error(exc: BaseException) -> str:
    """Summarise an upstream exception without leaking stack traces or credentials."""
    if isinstance(exc, APITimeoutError):
        return "Microsoft Foundry did not respond in time."
    if isinstance(exc, APIConnectionError | ServiceRequestError | ServiceResponseError):
        return "Could not connect to Microsoft Foundry."
    if isinstance(exc, APIStatusError):
        return _truncate(f"Microsoft Foundry returned HTTP {exc.status_code}: {exc.message}")
    if isinstance(exc, ClientAuthenticationError):
        return "Authentication to Microsoft Foundry failed (check the managed identity and its RBAC role assignment)."
    if isinstance(exc, HttpResponseError):
        status = f"HTTP {exc.status_code}" if exc.status_code else "an error"
        return _truncate(f"Microsoft Foundry returned {status}: {exc.message or exc.reason or ''}".rstrip(": "))
    if isinstance(exc, UPSTREAM_EXCEPTIONS):
        return _truncate(f"Microsoft Foundry request failed: {exc}")
    return "Unexpected error while calling Microsoft Foundry."
