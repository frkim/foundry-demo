<#
.SYNOPSIS
  Regenerates the narrated Foundry Guide demo video: TTS -> capture -> merge.

.DESCRIPTION
  1. tts.py      synthesizes narration.md with Azure AI Speech (Entra ID token, no keys) into tmp/video/audio.
  2. capture.py  records the live app with Playwright + Microsoft Edge, paced to the narration clips.
  3. merge.py    builds docs/video/foundry-demo.mp4, foundry-demo.srt and foundry-demo-poster.png with ffmpeg.

.EXAMPLE
  ./scripts/video/run.ps1
  ./scripts/video/run.ps1 -SkipTts -Url https://<containerAppFqdn>
#>
[CmdletBinding()]
param(
  [string]$Url = 'https://ca-foundrydemo-dev.bravesea-b93d5bb2.francecentral.azurecontainerapps.io',
  [string]$Voice = 'en-US-AndrewMultilingualNeural',
  [int]$Crf = 20,
  [switch]$SkipTts,
  [switch]$SkipCapture,
  [switch]$ForceTts,
  [switch]$Headed
)

$ErrorActionPreference = 'Stop'
$env:PYTHONUNBUFFERED = '1'

foreach ($tool in 'uv', 'ffmpeg', 'ffprobe') {
  if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "$tool is required on PATH." }
}

function Invoke-Step([string]$Name, [string[]]$Arguments) {
  Write-Host "`n=== $Name ===" -ForegroundColor Cyan
  & uv run --project $PSScriptRoot python @Arguments
  if ($LASTEXITCODE -ne 0) { throw "$Name failed (exit $LASTEXITCODE)." }
}

Push-Location $PSScriptRoot
try {
  if (-not $SkipTts) {
    $ttsArgs = @('tts.py', '--voice', $Voice)
    if ($ForceTts) { $ttsArgs += '--force' }
    Invoke-Step 'Narration (Azure AI Speech)' $ttsArgs
  }
  if (-not $SkipCapture) {
    $captureArgs = @('capture.py', '--url', $Url)
    if ($Headed) { $captureArgs += '--headed' }
    Invoke-Step 'Screen capture (Playwright + Edge)' $captureArgs
  }
  Invoke-Step 'Merge (ffmpeg)' @('merge.py', '--crf', "$Crf")
}
finally {
  Pop-Location
}
