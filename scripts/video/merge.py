"""Merge the Playwright recording and narration clips into docs/video/foundry-demo.mp4 (+ .srt and poster).

Each clip is placed at its scene start time (adelay) and mixed with amix (normalize=0). Video is trimmed to the
timeline and converted to H.264 yuv420p 30 fps; chapter start times are printed for docs/video/README.md.

Usage: uv run python merge.py [--crf 20] [--poster-scene ci-answer]
"""

from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from common import AUDIO_DIR, AUDIO_MANIFEST, OUTPUT_DIR, TIMELINE_FILE, WORK_DIR, probe_duration, read_json

OUTPUT_MP4 = OUTPUT_DIR / "foundry-demo.mp4"
OUTPUT_SRT = OUTPUT_DIR / "foundry-demo.srt"
OUTPUT_POSTER = OUTPUT_DIR / "foundry-demo-poster.png"
METADATA_FILE = WORK_DIR / "chapters.ffmeta"
MAX_CUE_CHARS = 90
CHAPTERS: dict[str, str] = {
    "title": "Introduction",
    "about": "Architecture and deployment",
    "agent-ask": "Agent + Microsoft Learn MCP",
    "ci-ask": "Code Interpreter cost calculation",
    "compare-ask": "Model compare: gpt-5.4-mini vs gpt-5.4-nano",
    "history": "Run history",
    "closing": "Recap",
}


@dataclass(frozen=True)
class Placed:
    """A narration clip positioned on the video timeline."""

    scene_id: str
    path: Path
    start: float
    duration: float
    text: str
    scene_end: float


def load_placements() -> tuple[list[Placed], dict]:
    timeline = read_json(TIMELINE_FILE)
    clips = {item["id"]: item for item in read_json(AUDIO_MANIFEST)}
    placed = [
        Placed(
            scene_id=scene["id"],
            path=AUDIO_DIR / clips[scene["id"]]["file"],
            start=float(scene["start"]),
            duration=float(clips[scene["id"]]["duration"]),
            text=str(clips[scene["id"]]["text"]),
            scene_end=float(scene["end"]),
        )
        for scene in timeline["scenes"]
    ]
    return placed, timeline


def video_offset(timeline: dict) -> float:
    """Seconds to skip at the start of the recording; corrects for late recorder start when measurable."""
    offset = float(timeline["video_offset"])
    try:
        lag = float(timeline["wall_duration"]) - probe_duration(Path(timeline["video"]))
    except (subprocess.CalledProcessError, ValueError):
        return offset
    print(f"recording length vs wall clock: {-lag:+.2f}s")
    return max(0.0, offset - lag) if 0 < lag < 2 else offset


# ---------------------------------------------------------------- subtitles


def split_cues(text: str) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    cues: list[str] = []
    for sentence in sentences:
        cues.extend(_split_long(sentence))
    return [cue for cue in cues if cue]


def _split_long(sentence: str) -> list[str]:
    if len(sentence) <= MAX_CUE_CHARS:
        return [sentence]
    parts = re.split(r"(?<=[,:;])\s+", sentence)
    chunks: list[str] = []
    current = ""
    for part in parts:
        candidate = f"{current} {part}".strip()
        if current and len(candidate) > MAX_CUE_CHARS:
            chunks.append(current)
            current = part
        else:
            current = candidate
    chunks.append(current)
    return chunks


def srt_time(seconds: float) -> str:
    millis = round(max(0.0, seconds) * 1000)
    hours, rest = divmod(millis, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    secs, millis = divmod(rest, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def wrap_cue(cue: str, width: int = 48) -> str:
    if len(cue) <= width:
        return cue
    middle = len(cue) // 2
    left, right = cue.rfind(" ", 0, middle + 1), cue.find(" ", middle)
    cut = left if right == -1 or (left != -1 and middle - left <= right - middle) else right
    return f"{cue[:cut]}\n{cue[cut + 1 :]}"


def write_srt(placed: list[Placed], path: Path) -> None:
    """Spread each clip's cues over its duration proportionally to character count."""
    blocks: list[str] = []
    for clip in placed:
        cues = split_cues(clip.text)
        total_chars = sum(len(cue) for cue in cues)
        cursor = clip.start
        for cue in cues:
            length = clip.duration * len(cue) / total_chars
            timing = f"{srt_time(cursor)} --> {srt_time(cursor + length - 0.05)}"
            blocks.append(f"{len(blocks) + 1}\n{timing}\n{wrap_cue(cue)}")
            cursor += length
    path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- chapters + ffmpeg


def chapter_list(placed: list[Placed]) -> list[tuple[float, str]]:
    starts = [(clip.start, CHAPTERS[clip.scene_id]) for clip in placed if clip.scene_id in CHAPTERS]
    starts[0] = (0.0, starts[0][1])
    return starts


def write_metadata() -> None:
    # Chapters are listed in docs/video/README.md rather than embedded: an MP4 chapter track adds a data stream.
    lines = [";FFMETADATA1", "title=Microsoft Foundry - From prompt to production agent", "artist=Foundry Guide demo"]
    METADATA_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_command(video: Path, offset: float, duration: float, placed: list[Placed], crf: int) -> list[str]:
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-stats"]
    cmd += ["-ss", f"{offset:.3f}", "-t", f"{duration:.3f}", "-i", str(video)]
    for clip in placed:
        cmd += ["-i", str(clip.path)]
    cmd += ["-i", str(METADATA_FILE)]
    fade_out = max(0.0, duration - 1.0)
    filters = [f"[0:v]fps=30,format=yuv420p,fade=t=in:st=0:d=0.6,fade=t=out:st={fade_out:.3f}:d=1[v]"]
    labels = []
    for index, clip in enumerate(placed, start=1):
        delay = round(clip.start * 1000)
        filters.append(f"[{index}:a]aresample=48000,adelay={delay}:all=1[a{index}]")
        labels.append(f"[a{index}]")
    filters.append(
        f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:dropout_transition=0,"
        f"apad=whole_dur={duration:.3f},atrim=0:{duration:.3f}[a]"
    )
    cmd += ["-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]"]
    cmd += ["-map_metadata", str(len(placed) + 1), "-map_chapters", "-1"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", str(crf), "-tune", "stillimage", "-pix_fmt", "yuv420p"]
    cmd += ["-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-movflags", "+faststart", "-t", f"{duration:.3f}"]
    return [*cmd, str(OUTPUT_MP4)]


def extract_poster(placed: list[Placed], scene_id: str, fraction: float) -> None:
    clip = next((c for c in placed if c.scene_id == scene_id), placed[-1])
    at = clip.start + (clip.scene_end - clip.start) * fraction
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{at:.2f}", "-i", str(OUTPUT_MP4), "-frames:v", "1",
         "-vf", "scale=1280:-2", str(OUTPUT_POSTER)],
        check=True,
    )  # fmt: skip


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--crf", type=int, default=20)
    parser.add_argument("--poster-scene", default="ci-answer")
    parser.add_argument("--poster-at", type=float, default=0.2, help="fraction of the poster scene")
    parser.add_argument("--poster-only", action="store_true", help="only re-extract the poster from the MP4")
    args = parser.parse_args()

    placed, timeline = load_placements()
    if args.poster_only:
        extract_poster(placed, args.poster_scene, args.poster_at)
        return
    duration = float(timeline["duration"])
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    chapters = chapter_list(placed)
    write_metadata()
    write_srt(placed, OUTPUT_SRT)
    offset = video_offset(timeline)
    subprocess.run(build_command(Path(timeline["video"]), offset, duration, placed, args.crf), check=True)
    extract_poster(placed, args.poster_scene, args.poster_at)

    size_mb = OUTPUT_MP4.stat().st_size / 1_048_576
    print(f"\n{OUTPUT_MP4} - {probe_duration(OUTPUT_MP4):.1f}s, {size_mb:.1f} MB (video offset {offset:.2f}s)")
    print("Chapters:")
    for start, title in chapters:
        print(f"  {int(start // 60)}:{int(start % 60):02d}  {title}")


if __name__ == "__main__":
    main()
