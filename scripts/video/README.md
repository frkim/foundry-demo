# Demo video pipeline

Builds the narrated walkthrough of the deployed **Foundry Guide** app: `docs/video/foundry-demo.mp4`, its subtitles
(`foundry-demo.srt`) and a poster frame. Three steps run in order:

| Step | Script | What it does | Output (scratch, gitignored) |
| --- | --- | --- | --- |
| 1 | `tts.py` | Synthesizes each scene of [`narration.md`](narration.md) with **Azure AI Speech** (REST, SSML, `en-US-AndrewMultilingualNeural`) using an **Entra ID token only** | `tmp/video/audio/*.wav` + `manifest.json` (durations from ffprobe) |
| 2 | `capture.py` | Drives the live app with Playwright + installed **Microsoft Edge** (`channel="msedge"`, headless, 1920×1080, `record_video_dir`). Each scene lasts at least as long as its narration clip; scene start/end times are logged | `tmp/video/recording/*.webm` + `timeline.json` |
| 3 | `merge.py` | ffmpeg: trims the recording, converts it to H.264 (yuv420p, 30 fps, CRF 20), places each clip at its scene start (`adelay` + `amix normalize=0`), AAC 160k, writes SRT and a poster | `docs/video/foundry-demo.{mp4,srt}`, `foundry-demo-poster.png` |

`run.ps1` runs all three steps.

## Prerequisites

- Windows with **Microsoft Edge** installed (Playwright uses it directly, so no `playwright install` is needed).
- `uv`, `ffmpeg` and `ffprobe` on `PATH`; Python 3.12+ (uv resolves it).
- Packages resolve **only** through the CFS proxy feed configured in [`pyproject.toml`](pyproject.toml)
  (`https://packagefeedproxy.microsoft.io/pypi/simple`).
- `az login` with an identity that has **Cognitive Services Speech User** (or Cognitive Services User) on the Foundry
  resource `aif-foundrydemo-dev-egl6j`. The resource has `disableLocalAuth: true`, so keys are never used.
- The app must be deployed and its agent ready (`GET /api/info` → `agent.status = ready`).

## Usage

```powershell
# Full run (TTS clips are cached by text hash; only changed scenes are re-synthesized)
./scripts/video/run.ps1

# Different deployment, re-record only
./scripts/video/run.ps1 -SkipTts -Url https://<containerAppFqdn>

# Watch the browser while recording, or force new TTS
./scripts/video/run.ps1 -Headed -ForceTts

# Individual steps
cd scripts/video
uv run python tts.py
uv run python capture.py --max-takes 4
uv run python merge.py --crf 22
```

A full run takes about 5 minutes for capture plus 2 minutes for encoding.

## How it works

- **Authentication.** `tts.py` gets a token for `https://cognitiveservices.azure.com/.default` from
  `AzureCliCredential` (falling back to `DefaultAzureCredential`) and calls
  `https://aif-foundrydemo-dev-egl6j.cognitiveservices.azure.com/tts/cognitiveservices/v1` with
  `Authorization: Bearer <token>`. If that is rejected, it falls back to the regional endpoint
  `https://swedencentral.tts.speech.microsoft.com/cognitiveservices/v1` with `Bearer aad#<resourceId>#<token>`.
  401/403 responses are retried with backoff because role assignments take a few minutes to propagate. Tokens are
  never printed.
- **Alignment.** Live agent latency varies from about 5 to 40 seconds. Each scene therefore waits for
  `max(narration clip, live action) + 0.8 s`, and `timeline.json` records where each scene starts. `merge.py` places
  every clip at that offset, so narration and picture stay aligned whatever the latency. The title card is an HTML
  overlay drawn in the page, so it is part of the recording.
- **Takes.** The narration states concrete results, so `capture.py` checks each live answer: an MCP tool chip and a
  `learn.microsoft.com` link for the grounded question; a Code Interpreter chip, `$2.80`, `$84` and `$1,022` plus a
  rendered chart for the cost question. If a check fails (model answers vary), the whole take is re-recorded with a
  fresh conversation, up to `--max-takes` times.
- **Prompts** are typed with `fill()` into `prompt-input` / `compare-input` and match
  [`docs/session/demo-runbook.md`](../../docs/session/demo-runbook.md); the suggestion chips are not used.
- **Subtitles** are generated from the narration text: each clip is split into sentence cues, timed in proportion to
  character count within the clip.

## Editing the narration

Edit [`narration.md`](narration.md). Each `## <scene-id>` must match a key of `SCENES` in `capture.py`. If you change
a result the narration states, update `CI_EXPECTED` in `capture.py` too. Then rerun `run.ps1`. Only changed scenes
are re-synthesized. Update the chapter table in `docs/video/README.md` from the chapter list `merge.py` prints.

## Lint

```powershell
cd scripts/video; uv run ruff check .; uv run ruff format --check .
```
