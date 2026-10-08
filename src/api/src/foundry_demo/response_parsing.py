"""Extract text, tool calls, citations, generated files and usage from a Responses API result.

Parsing is duck-typed (getattr) so it works with OpenAI SDK models, Foundry-specific item types and test fakes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

from .schemas import Citation, GeneratedFile, ToolCall, Usage

_TOOL_ITEM_TYPES = {"mcp_call", "mcp_list_tools", "code_interpreter_call", "mcp_approval_request"}


@dataclass
class ParsedResponse:
    text: str
    response_id: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    citations: list[Citation] = field(default_factory=list)
    files: list[GeneratedFile] = field(default_factory=list)
    usage: Usage = field(default_factory=Usage)


def _int_or_none(value: Any) -> int | None:
    return value if isinstance(value, int) else None


def extract_usage(response: Any) -> Usage:
    usage = getattr(response, "usage", None)
    if usage is None:
        return Usage()
    return Usage(
        input_tokens=_int_or_none(getattr(usage, "input_tokens", None)),
        output_tokens=_int_or_none(getattr(usage, "output_tokens", None)),
        total_tokens=_int_or_none(getattr(usage, "total_tokens", None)),
    )


def extract_text(response: Any) -> str:
    text = getattr(response, "output_text", None)
    if isinstance(text, str) and text:
        return text
    parts: list[str] = []
    for item in getattr(response, "output", None) or []:
        if getattr(item, "type", None) != "message":
            continue
        for content in getattr(item, "content", None) or []:
            value = getattr(content, "text", None)
            if isinstance(value, str):
                parts.append(value)
    return "".join(parts)


def file_url(container_id: str, file_id: str, filename: str) -> str:
    return f"/api/files/{quote(container_id, safe='')}/{quote(file_id, safe='')}?filename={quote(filename, safe='')}"


def _collect_annotations(item: Any, citations: dict[str, Citation], files: dict[str, GeneratedFile]) -> None:
    for content in getattr(item, "content", None) or []:
        for annotation in getattr(content, "annotations", None) or []:
            kind = getattr(annotation, "type", None)
            if kind == "url_citation":
                url = getattr(annotation, "url", None)
                if isinstance(url, str) and url not in citations:
                    citations[url] = Citation(url=url, title=getattr(annotation, "title", None))
            elif kind == "container_file_citation":
                container_id = getattr(annotation, "container_id", None)
                file_id = getattr(annotation, "file_id", None)
                filename = getattr(annotation, "filename", None) or file_id
                if isinstance(container_id, str) and isinstance(file_id, str) and file_id not in files:
                    files[file_id] = GeneratedFile(
                        container_id=container_id,
                        file_id=file_id,
                        filename=str(filename),
                        url=file_url(container_id, file_id, str(filename)),
                    )


def parse_response(response: Any) -> ParsedResponse:
    tool_calls: list[ToolCall] = []
    citations: dict[str, Citation] = {}
    files: dict[str, GeneratedFile] = {}
    for item in getattr(response, "output", None) or []:
        item_type = getattr(item, "type", None)
        if not isinstance(item_type, str):
            continue
        if item_type == "message":
            _collect_annotations(item, citations, files)
        elif item_type in _TOOL_ITEM_TYPES or item_type.endswith("_call"):
            tool_calls.append(
                ToolCall(
                    type=item_type,
                    name=getattr(item, "name", None),
                    server_label=getattr(item, "server_label", None),
                    status=getattr(item, "status", None),
                )
            )
    response_id = getattr(response, "id", None)
    return ParsedResponse(
        text=extract_text(response),
        response_id=response_id if isinstance(response_id, str) else None,
        tool_calls=tool_calls,
        citations=list(citations.values()),
        files=list(files.values()),
        usage=extract_usage(response),
    )
