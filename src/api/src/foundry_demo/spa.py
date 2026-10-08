"""Serve the built single-page application with client-side routing fallback."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response

_RESERVED_PREFIXES = ("api", "health")


def register_spa(app: FastAPI, static_dir: Path) -> None:
    """Register a catch-all GET route. Must be called after every API route has been registered."""
    root = static_dir.resolve()
    index = root / "index.html"

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str) -> Response:
        first_segment = full_path.split("/", 1)[0]
        if first_segment in _RESERVED_PREFIXES:
            raise HTTPException(status_code=404, detail="Not Found")
        if not index.is_file():
            return JSONResponse(
                status_code=404,
                content={"detail": f"Web UI not found in {root}. Build src/web and set STATIC_DIR."},
            )
        if full_path:
            candidate = (root / full_path).resolve()
            if candidate.is_relative_to(root) and candidate.is_file():
                cache = "public, max-age=31536000, immutable" if full_path.startswith("assets/") else "no-cache"
                return FileResponse(candidate, headers={"Cache-Control": cache})
        return FileResponse(index, headers={"Cache-Control": "no-cache"})
