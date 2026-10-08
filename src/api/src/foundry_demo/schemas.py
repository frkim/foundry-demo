"""Request and response models (the public HTTP contract)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .config import MAX_MESSAGE_LENGTH

ID_PATTERN = r"^[A-Za-z0-9_\-]{1,200}$"


def _not_blank(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("must not be blank")
    return stripped


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH, description="User message for the agent.")
    conversation_id: str | None = Field(
        default=None, pattern=ID_PATTERN, description="Existing Foundry conversation id; omit to start a new one."
    )

    @field_validator("message")
    @classmethod
    def _message_not_blank(cls, value: str) -> str:
        return _not_blank(value)


class CompareRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH, description="Prompt sent to both models.")

    @field_validator("prompt")
    @classmethod
    def _prompt_not_blank(cls, value: str) -> str:
        return _not_blank(value)


class ToolCall(BaseModel):
    type: str
    name: str | None = None
    server_label: str | None = None
    status: str | None = None


class Usage(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


class GeneratedFile(BaseModel):
    container_id: str
    file_id: str
    filename: str
    url: str


class Citation(BaseModel):
    url: str
    title: str | None = None


class ChatResponse(BaseModel):
    text: str
    conversation_id: str
    response_id: str | None = None
    agent_name: str
    agent_version: str | None = None
    tool_calls: list[ToolCall]
    citations: list[Citation] = Field(default_factory=list)
    files: list[GeneratedFile] = Field(default_factory=list)
    usage: Usage
    latency_ms: int


class ModelResult(BaseModel):
    model: str
    role: Literal["primary", "fast"]
    output: str
    latency_ms: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    error: str | None = None


class CompareResponse(BaseModel):
    prompt: str
    results: list[ModelResult]


class RunRecord(BaseModel):
    id: str
    timestamp: datetime
    kind: Literal["agent", "compare"]
    target: str
    prompt_preview: str
    latency_ms: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    tool_calls: int = 0
    status: Literal["ok", "error"]
    error: str | None = None


class HistoryResponse(BaseModel):
    items: list[RunRecord]
    count: int
    capacity: int


class AgentInfo(BaseModel):
    name: str
    version: str | None = None
    status: str
    error: str | None = None
    tools: list[str]


class ModelsInfo(BaseModel):
    primary: str
    fast: str


class InfoResponse(BaseModel):
    app_name: str = "Foundry Guide"
    app_version: str
    region: str
    endpoint_host: str | None
    project_name: str | None
    configured: bool
    telemetry_enabled: bool
    models: ModelsInfo
    agent: AgentInfo


class ErrorBody(BaseModel):
    code: str
    message: str
    correlation_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody
