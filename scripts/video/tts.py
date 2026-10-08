"""Synthesize narration.md scene by scene with Azure AI Speech (Entra ID auth only, no keys).

Usage: uv run python tts.py [--voice en-US-AndrewMultilingualNeural] [--force]
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
from dataclasses import dataclass
from xml.sax.saxutils import escape

import requests
from azure.identity import AzureCliCredential, ChainedTokenCredential, DefaultAzureCredential

from common import AUDIO_DIR, AUDIO_MANIFEST, Scene, load_scenes, probe_duration, read_json, write_json

SCOPE = "https://cognitiveservices.azure.com/.default"
CUSTOM_DOMAIN_URL = "https://aif-foundrydemo-dev-egl6j.cognitiveservices.azure.com/tts/cognitiveservices/v1"
REGIONAL_URL = "https://swedencentral.tts.speech.microsoft.com/cognitiveservices/v1"
RESOURCE_ID = (
    "/subscriptions/bb766161-890c-4a8e-9c63-981b510e4e38/resourceGroups/rg-foundrydemo-dev-swc"
    "/providers/Microsoft.CognitiveServices/accounts/aif-foundrydemo-dev-egl6j"
)
DEFAULT_VOICE = "en-US-AndrewMultilingualNeural"
FALLBACK_VOICES = ("en-US-AndrewNeural", "en-US-GuyNeural")
OUTPUT_FORMAT = "riff-24khz-16bit-mono-pcm"
RETRY_STATUSES = {401, 403, 429, 500, 502, 503, 504}
MAX_ATTEMPTS = 8
# narration.md keeps the on-screen spelling (also used for subtitles); SSML <sub> makes the voice say it naturally.
PRONUNCIATIONS = {
    "gpt-5.4-mini": "G P T five point four mini",
    "gpt-5.4-nano": "G P T five point four nano",
    "learn.microsoft.com": "learn dot microsoft dot com",
}


@dataclass(frozen=True)
class AuthMode:
    """How to call the Speech REST API with an Entra ID token."""

    name: str
    url: str
    use_resource_prefix: bool

    def header(self, token: str) -> str:
        return f"Bearer aad#{RESOURCE_ID}#{token}" if self.use_resource_prefix else f"Bearer {token}"


AUTH_MODES = (
    AuthMode("custom-domain bearer", CUSTOM_DOMAIN_URL, use_resource_prefix=False),
    AuthMode("regional aad#resourceId#token", REGIONAL_URL, use_resource_prefix=True),
)


def build_ssml(text: str, voice: str) -> str:
    body = escape(text)
    for written, spoken in PRONUNCIATIONS.items():
        body = body.replace(written, f"<sub alias='{spoken}'>{written}</sub>")
    return (
        "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>"
        f"<voice name='{voice}'><prosody rate='-3%'>{body}</prosody></voice></speak>"
    )


def text_hash(text: str, voice: str) -> str:
    return hashlib.sha256(build_ssml(text, voice).encode()).hexdigest()[:16]


class Synthesizer:
    """Calls Azure AI Speech TTS, remembering the auth mode and voice that worked."""

    def __init__(self, voice: str) -> None:
        self.credential = ChainedTokenCredential(AzureCliCredential(), DefaultAzureCredential())
        self.voices = [voice, *[v for v in FALLBACK_VOICES if v != voice]]
        self.mode: AuthMode | None = None

    def synthesize(self, text: str) -> tuple[bytes, str]:
        """Return (audio bytes, voice used); tries auth modes and fallback voices until one works."""
        modes = [self.mode] if self.mode else list(AUTH_MODES)
        errors: list[str] = []
        for voice in self.voices:
            for mode in modes:
                audio, error = self._call_with_retry(mode, voice, text)
                if audio is not None:
                    if self.mode is None:
                        print(f"  auth mode: {mode.name}; voice: {voice}")
                    self.mode, self.voices = mode, [voice]
                    return audio, voice
                errors.append(f"{mode.name}/{voice}: {error}")
        raise RuntimeError("TTS failed: " + " | ".join(errors))

    def _call_with_retry(self, mode: AuthMode, voice: str, text: str) -> tuple[bytes | None, str]:
        error = ""
        for attempt in range(1, MAX_ATTEMPTS + 1):
            token = self.credential.get_token(SCOPE).token
            response = requests.post(
                mode.url,
                headers={
                    "Authorization": mode.header(token),
                    "Content-Type": "application/ssml+xml",
                    "X-Microsoft-OutputFormat": OUTPUT_FORMAT,
                    "User-Agent": "foundry-demo-video",
                },
                data=build_ssml(text, voice).encode("utf-8"),
                timeout=120,
            )
            if response.ok and response.content:
                return response.content, ""
            error = f"HTTP {response.status_code} {response.text[:200]}"
            if response.status_code not in RETRY_STATUSES or (self.mode is None and attempt >= 2):
                # While probing auth modes, fail fast and try the next mode; retry longer once one has worked.
                break
            wait = min(10 * attempt, 60)
            print(f"  {mode.name}: {error.strip()} - retry {attempt}/{MAX_ATTEMPTS} in {wait}s", file=sys.stderr)
            time.sleep(wait)
        return None, error


def load_manifest() -> dict[str, dict[str, object]]:
    if not AUDIO_MANIFEST.exists():
        return {}
    return {item["id"]: item for item in read_json(AUDIO_MANIFEST)}


def synthesize_scene(scene: Scene, synth: Synthesizer, cached: dict[str, object] | None, force: bool) -> dict:
    path = AUDIO_DIR / f"{scene.scene_id}.wav"
    digest = text_hash(scene.text, synth.voices[0])
    if not force and cached and cached.get("hash") == digest and path.exists():
        print(f"- {scene.scene_id}: cached ({cached['duration']:.2f}s)")
        return cached
    audio, voice = synth.synthesize(scene.text)
    path.write_bytes(audio)
    duration = probe_duration(path)
    print(f"- {scene.scene_id}: {duration:.2f}s ({len(scene.text.split())} words)")
    return {
        "id": scene.scene_id,
        "file": path.name,
        "duration": round(duration, 3),
        "voice": voice,
        "hash": text_hash(scene.text, voice),
        "text": scene.text,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--voice", default=DEFAULT_VOICE)
    parser.add_argument("--force", action="store_true", help="re-synthesize even if cached")
    args = parser.parse_args()

    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    cache = load_manifest()
    synth = Synthesizer(args.voice)
    manifest = [synthesize_scene(s, synth, cache.get(s.scene_id), args.force) for s in load_scenes()]
    write_json(AUDIO_MANIFEST, manifest)
    total = sum(float(item["duration"]) for item in manifest)
    print(f"Wrote {len(manifest)} clips, {total:.1f}s of narration -> {AUDIO_MANIFEST}")


if __name__ == "__main__":
    main()
