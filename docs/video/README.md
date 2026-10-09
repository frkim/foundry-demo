# Demo video: Microsoft Foundry, from prompt to production agent

A narrated walkthrough (English, about 4 min 35 s) of the deployed **Foundry Guide** app. It covers a prompt agent in
Microsoft Foundry Agent Service grounded in Microsoft Learn through MCP, Code Interpreter, a model comparison, and run
history. Use it as a backup for the live demo (see [demo runbook](../session/demo-runbook.md), Demo 1) or share it
after the session.

| File | Description |
| --- | --- |
| [`foundry-demo.mp4`](foundry-demo.mp4) | 1920×1080, H.264 (yuv420p, 30 fps) + AAC 160 kbit/s mono, about 25 MB |
| [`foundry-demo.srt`](foundry-demo.srt) | English subtitles generated from the narration script |
| [`foundry-demo-poster.png`](foundry-demo-poster.png) | Poster frame (Code Interpreter cost table) |

## Chapters

| Time | Chapter | What is on screen |
| --- | --- | --- |
| 0:00 | Introduction | Title card "Microsoft Foundry — From prompt to production agent" |
| 0:24 | Architecture and deployment | **About** tab: Container Apps + FastAPI + Vue, keyless managed identity, live `/api/info` (Sweden Central, `gpt-5.4-mini` / `gpt-5.4-nano`, `foundry-guide` v1, MCP + Code Interpreter) |
| 1:09 | Agent + Microsoft Learn MCP | "What is the difference between prompt agents and hosted agents…? Cite Microsoft Learn." The answer shows MCP tool-call chips, a comparison table, and links to learn.microsoft.com, plus latency and tokens |
| 2:04 | Code Interpreter cost calculation | Same conversation: 2,000 conversations/day, 1,500 input + 500 output tokens at $0.40 / $1.60 per 1M tokens (illustrative). The answer has a Code Interpreter chip, a table ($2.80/day, $84/30 days, $1,022/365 days), and a generated bar chart |
| 3:06 | Model compare: gpt-5.4-mini vs gpt-5.4-nano | Same prompt to both deployments in parallel, with latency, input/output tokens, and the "Fastest" badge |
| 3:46 | Run history | All runs with sorting by latency and search for "compare" |
| 4:10 | Recap | Back on **About**, source repository link |

Chapter times come from the recorded take. Answers, latencies and token counts are live values and change on every
regeneration.

## Regenerate

The pipeline is in [`scripts/video`](../../scripts/video/README.md): Azure AI Speech narration (Entra ID token, no
keys), then a Playwright + Microsoft Edge capture of the live app, then ffmpeg merge.

```powershell
./scripts/video/run.ps1                                   # TTS (cached) -> capture -> merge
./scripts/video/run.ps1 -SkipTts -Url https://<containerAppFqdn>
```

Edit the spoken text in [`scripts/video/narration.md`](../../scripts/video/narration.md). The capture re-records a
take automatically if a live answer does not match what the narration says (for example, wrong cost figures). After
regenerating, update the chapter table from the chapter list `merge.py` prints.

## Notes

- The prompts are typed explicitly rather than clicked from the suggestion chips, so the recording does not depend on
  chip wording. Rerun the pipeline after UI changes to refresh it.
- The prices in the cost scene are illustrative, not list prices. Check the Azure pricing page for real numbers.
