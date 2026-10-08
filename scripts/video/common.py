"""Shared paths and helpers for the demo video pipeline."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
WORK_DIR = REPO_ROOT / "tmp" / "video"
AUDIO_DIR = WORK_DIR / "audio"
RECORDING_DIR = WORK_DIR / "recording"
AUDIO_MANIFEST = AUDIO_DIR / "manifest.json"
TIMELINE_FILE = WORK_DIR / "timeline.json"
OUTPUT_DIR = REPO_ROOT / "docs" / "video"
NARRATION_FILE = SCRIPT_DIR / "narration.md"

_HEADING = re.compile(r"^##\s+([a-z0-9-]+)\s*$")
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


@dataclass(frozen=True)
class Scene:
    """One narrated scene: an id shared with capture.py and the spoken text."""

    scene_id: str
    text: str


def load_scenes(path: Path = NARRATION_FILE) -> list[Scene]:
    """Parse `## scene-id` sections of narration.md into scenes (HTML comments are dropped)."""
    content = _COMMENT.sub("", path.read_text(encoding="utf-8"))
    scenes: list[Scene] = []
    current: str | None = None
    lines: list[str] = []
    for line in content.splitlines():
        match = _HEADING.match(line)
        if match:
            if current:
                scenes.append(Scene(current, _join(lines)))
            current, lines = match.group(1), []
        elif current:
            lines.append(line)
    if current:
        scenes.append(Scene(current, _join(lines)))
    return [scene for scene in scenes if scene.text]


def _join(lines: list[str]) -> str:
    return " ".join(" ".join(lines).split())


def probe_duration(path: Path) -> float:
    """Return a media file duration in seconds using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def read_json(path: Path) -> Any:  # noqa: ANN401 - generic JSON loader
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
