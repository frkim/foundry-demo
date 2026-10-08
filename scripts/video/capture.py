"""Record the Foundry Guide walkthrough with Playwright (installed Microsoft Edge), paced to the narration clips.

Each scene lasts at least as long as its narration clip (plus a small pad) and as long as its live action needs
(agent responses vary between ~10 and ~40 s). Scene start/end times, relative to the trimmed video start, are written
to tmp/video/timeline.json so merge.py can place each narration clip with adelay.

Usage: uv run python capture.py [--url https://...] [--headed]
"""

from __future__ import annotations

import argparse
import re
import shutil
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from playwright.sync_api import Browser, Locator, Page, sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from common import AUDIO_MANIFEST, RECORDING_DIR, TIMELINE_FILE, read_json, write_json

DEFAULT_URL = "https://ca-foundrydemo-dev.bravesea-b93d5bb2.francecentral.azurecontainerapps.io"
VIEWPORT = {"width": 1920, "height": 1080}
SCENE_PAD_S = 0.8
AGENT_TIMEOUT_MS = 180_000
MAX_AGENT_ATTEMPTS = 3

# Exact prompts from docs/session/demo-runbook.md (Demo 1). Typed with fill(); suggestion chips are not used.
MCP_PROMPT = (
    "What is the difference between prompt agents and hosted agents in Microsoft Foundry Agent Service? "
    "Cite Microsoft Learn."
)
CI_PROMPT = (
    "Use Code Interpreter: 2,000 conversations/day, 1,500 input + 500 output tokens each, at $0.40/$1.60 per 1M "
    "tokens. Calculate daily, 30-day and 365-day cost; show a table and a bar chart."
)
COMPARE_PROMPT = "In three bullets, explain why teams put an AI gateway in front of their models."
# The narration states these results, so a take is only kept if the answer shows them.
CI_EXPECTED = (r"2\.80", r"\b84(\.00)?\b", r"1,?022")
MAX_TAKES = 4

TITLE_HTML = """
<div id="fg-title" style="position:fixed;inset:0;z-index:2147483646;display:flex;flex-direction:column;
  align-items:center;justify-content:center;color:#fff;font-family:'Segoe UI Variable','Segoe UI',sans-serif;
  background:linear-gradient(135deg,#2a1a6e 0%,#6B46FF 45%,#3b6cf6 75%,#00b4d8 100%);transition:opacity .9s ease">
  <div style="font-size:30px;letter-spacing:6px;text-transform:uppercase;opacity:.85">Microsoft Foundry</div>
  <div style="font-size:84px;font-weight:700;margin-top:18px">From prompt to production agent</div>
  <div style="width:160px;height:4px;background:#fff;opacity:.7;margin:40px 0;border-radius:2px"></div>
  <div style="font-size:30px;opacity:.92">
    Foundry Guide &middot; Foundry Agent Service &middot; Azure Container Apps</div>
  <div style="font-size:22px;opacity:.75;margin-top:18px">
    gpt-5.4-mini &middot; Microsoft Learn MCP &middot; Code Interpreter &middot; keyless with Entra ID</div>
</div>
"""

# Headless recordings have no visible pointer, so draw one that follows mouse events.
CURSOR_SCRIPT = """
(() => {
  const install = () => {
    if (document.getElementById('fg-cursor')) return;
    const c = document.createElement('div');
    c.id = 'fg-cursor';
    c.innerHTML = '<svg width="28" height="28" viewBox="0 0 24 24"><path d="M4 2l16 9.5-7 1.6L9.6 20z" ' +
      'fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
    Object.assign(c.style, {position: 'fixed', left: '0', top: '0', zIndex: 2147483647, pointerEvents: 'none',
      transform: 'translate(-100px,-100px)', filter: 'drop-shadow(0 2px 3px rgba(0,0,0,.35))'});
    document.body.appendChild(c);
    document.addEventListener('mousemove', e => {
      c.style.transform = `translate(${e.clientX - 4}px, ${e.clientY - 2}px)`;
    }, true);
    document.addEventListener('mousedown', e => {
      const r = document.createElement('div');
      Object.assign(r.style, {position: 'fixed', left: `${e.clientX - 22}px`, top: `${e.clientY - 22}px`,
        width: '44px', height: '44px', borderRadius: '50%', border: '3px solid #6B46FF', zIndex: 2147483646,
        pointerEvents: 'none', transition: 'all .5s ease-out', opacity: '1'});
      document.body.appendChild(r);
      requestAnimationFrame(() => { r.style.transform = 'scale(1.8)'; r.style.opacity = '0'; });
      setTimeout(() => r.remove(), 600);
    }, true);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install);
  else install();
})();
"""

PAN_SCRIPT = """
async (el, [from, to, ms]) => {
  const start = performance.now();
  await new Promise(resolve => {
    const step = now => {
      const t = Math.min(1, (now - start) / ms);
      const eased = t < .5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
      el.scrollTop = from + (to - from) * eased;
      t < 1 ? requestAnimationFrame(step) : resolve();
    };
    requestAnimationFrame(step);
  });
}
"""


@dataclass
class SceneClock:
    """Pacing helper: `at(fraction)` waits until that fraction of the narration clip has elapsed."""

    page: Page
    start: float
    budget: float

    def elapsed(self) -> float:
        return time.monotonic() - self.start

    def at(self, fraction: float) -> None:
        remaining = self.start + self.budget * fraction - time.monotonic()
        if remaining > 0:
            self.page.wait_for_timeout(remaining * 1000)

    def remaining(self) -> float:
        return max(0.0, self.start + self.budget - time.monotonic())


@dataclass
class Recorder:
    page: Page
    url: str
    origin: float = 0.0
    entries: list[dict[str, object]] = field(default_factory=list)


# ---------------------------------------------------------------- UI helpers


def glide_to(page: Page, locator: Locator, steps: int = 25) -> None:
    locator.scroll_into_view_if_needed()
    box = locator.bounding_box()
    if box:
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, steps=steps)


def click(page: Page, locator: Locator) -> None:
    glide_to(page, locator)
    page.wait_for_timeout(200)
    locator.click()


def by_test_id(page: Page, test_id: str) -> Locator:
    return page.locator(f'[data-testid="{test_id}"]')


def ask_agent(page: Page, prompt: str) -> None:
    """Type a prompt, send it and wait for a new assistant message (retrying on an error bubble)."""
    for attempt in range(1, MAX_AGENT_ATTEMPTS + 1):
        answers = by_test_id(page, "assistant-message").count()
        errors = by_test_id(page, "error-message").count()
        click(page, by_test_id(page, "prompt-input"))
        by_test_id(page, "prompt-input").fill(prompt)
        page.wait_for_timeout(900)
        click(page, by_test_id(page, "send-btn"))
        page.wait_for_function(
            """([a, e]) => {
              const q = s => document.querySelectorAll(`[data-testid="${s}"]`).length;
              return (q('assistant-message') > a || q('error-message') > e) && !q('thinking-indicator');
            }""",
            arg=[answers, errors],
            timeout=AGENT_TIMEOUT_MS,
        )
        if by_test_id(page, "assistant-message").count() > answers:
            return
        print(f"  agent returned an error (attempt {attempt}/{MAX_AGENT_ATTEMPTS}); retrying in 15 s")
        page.wait_for_timeout(15_000)
    raise RuntimeError("Agent did not answer after retries")


def wait_for_images(page: Page, scope: Locator) -> None:
    try:
        page.wait_for_function(
            "el => [...el.querySelectorAll('img')].every(i => i.complete && i.naturalWidth > 0)",
            arg=scope.element_handle(),
            timeout=30_000,
        )
    except PlaywrightTimeoutError:
        print("  warning: chart image did not load within 30 s")


class RetakeError(RuntimeError):
    """The live answer did not match what the narration says; the whole take must be recorded again."""


def check_answer(message: Locator, chip_text: str, expected: tuple[str, ...], need_link: str | None = None) -> None:
    """Fail the take unless the latest answer used the expected tool and matches the expected patterns."""
    chips = " ".join(message.locator('[data-testid="tool-call-chip"]').all_inner_texts())
    text = " ".join(message.inner_text().split())
    problems = [] if chip_text in chips else [f"no '{chip_text}' tool chip (chips: {chips or 'none'})"]
    problems += [f"missing /{pattern}/" for pattern in expected if not re.search(pattern, text)]
    if need_link and not message.locator(f'a[href*="{need_link}"]').count():
        problems.append(f"no {need_link} link")
    if problems:
        raise RetakeError("; ".join(problems))


def pan(scroller: Locator, target: float, seconds: float) -> None:
    current = scroller.evaluate("(s) => s.scrollTop")
    if abs(target - current) > 2:
        scroller.evaluate(PAN_SCRIPT, [current, target, seconds * 1000])


def show_latest_answer_top(page: Page) -> None:
    """Scroll the chat so the latest assistant message starts at the top of the scroller."""
    scroller = page.locator(".fg-scroll")
    message = by_test_id(page, "assistant-message").last.element_handle()
    top = scroller.evaluate(
        "(s, m) => s.scrollTop + m.getBoundingClientRect().top - s.getBoundingClientRect().top - 8", message
    )
    pan(scroller, max(0.0, top), 1.2)


def pan_chat_to_bottom(clock: SceneClock, fraction: float) -> None:
    """Glide the chat to the bottom, finishing at the given fraction of the clip."""
    scroller = clock.page.locator(".fg-scroll")
    bottom = scroller.evaluate("(s) => s.scrollHeight - s.clientHeight")
    pan(scroller, bottom, max(1.5, clock.budget * fraction - clock.elapsed()))


def wander(clock: SceneClock, targets: list[Locator], until: float) -> None:
    """Point at a few elements, evenly spread over the given fraction of the clip."""
    for index, target in enumerate(targets, start=1):
        if target.count():
            glide_to(clock.page, target.first, steps=35)
        clock.at(until * index / len(targets))


# ---------------------------------------------------------------- scenes


def scene_title(clock: SceneClock) -> None:
    clock.at(1.0)


def scene_about(clock: SceneClock) -> None:
    page = clock.page
    page.evaluate("document.getElementById('fg-title').style.opacity = '0'")
    page.wait_for_timeout(1000)
    page.evaluate("document.getElementById('fg-title').remove()")
    click(page, by_test_id(page, "tab-about"))
    by_test_id(page, "deployment-info").wait_for()
    wander(
        clock,
        [
            page.locator(".v-timeline-item").nth(0),
            page.locator(".v-timeline-item").nth(1),
            page.get_by_text("swedencentral").first,
            page.get_by_text("gpt-5.4-mini").first,
            page.get_by_text("gpt-5.4-nano").first,
            page.locator(".v-list-item", has_text="Agent tools"),
            page.locator(".v-timeline-item").nth(4),
        ],
        until=0.95,
    )


def scene_agent_ask(clock: SceneClock) -> None:
    page = clock.page
    click(page, by_test_id(page, "tab-agent"))
    page.wait_for_timeout(800)
    ask_agent(page, MCP_PROMPT)
    check_answer(by_test_id(page, "assistant-message").last, "MCP", (), need_link="learn.microsoft.com")


def scene_agent_answer(clock: SceneClock) -> None:
    page = clock.page
    message = by_test_id(page, "assistant-message").last
    show_latest_answer_top(page)
    point_at(page, message.locator('[data-testid="tool-call-chip"]'))
    clock.at(0.4)
    pan_chat_to_bottom(clock, 0.85)
    point_at(page, message.locator('[data-testid="message-meta"]'))


def point_at(page: Page, locator: Locator) -> None:
    """Move the pointer to an element only if it is inside the viewport (avoids re-scrolling the chat)."""
    if not locator.count():
        return
    box = locator.first.bounding_box()
    if box and 0 <= box["y"] <= VIEWPORT["height"] - 20:
        page.mouse.move(box["x"] + min(box["width"] / 2, 120), box["y"] + box["height"] / 2, steps=30)


def scene_ci_ask(clock: SceneClock) -> None:
    page = clock.page
    ask_agent(page, CI_PROMPT)
    message = by_test_id(page, "assistant-message").last
    wait_for_images(page, message)
    check_answer(message, "Code Interpreter", CI_EXPECTED)
    if not message.locator("img").count():
        raise RetakeError("no chart image rendered")


def scene_ci_answer(clock: SceneClock) -> None:
    page = clock.page
    message = by_test_id(page, "assistant-message").last
    show_latest_answer_top(page)
    point_at(page, message.locator('[data-testid="tool-call-chip"]'))
    clock.at(0.3)
    pan_chat_to_bottom(clock, 0.8)
    point_at(page, message.locator("img"))


def scene_compare_ask(clock: SceneClock) -> None:
    page = clock.page
    click(page, by_test_id(page, "tab-compare"))
    page.wait_for_timeout(800)
    click(page, by_test_id(page, "compare-input"))
    by_test_id(page, "compare-input").fill(COMPARE_PROMPT)
    clock.at(0.55)
    click(page, by_test_id(page, "compare-btn"))
    page.wait_for_function(
        """() => {
          if (document.querySelector('[data-testid="compare-error"]')) return true;
          const cards = [0, 1].map(i => document.querySelector(`[data-testid="compare-result-${i}"]`));
          const done = c => c && c.querySelector('.fg-markdown, .v-alert') && !c.querySelector('.v-skeleton-loader');
          return cards.every(done);
        }""",
        timeout=AGENT_TIMEOUT_MS,
    )


def scene_compare_result(clock: SceneClock) -> None:
    page = clock.page
    wander(
        clock,
        [
            by_test_id(page, "compare-result-0").locator(".v-chip").first,
            by_test_id(page, "compare-result-1").locator(".v-chip").first,
            page.locator(".v-chip", has_text="Fastest"),
            by_test_id(page, "compare-result-1").locator(".fg-markdown"),
        ],
        until=0.9,
    )


def scene_history(clock: SceneClock) -> None:
    page = clock.page
    click(page, by_test_id(page, "tab-history"))
    page.locator('[data-testid="history-table"] tbody tr').first.wait_for()
    clock.at(0.35)
    latency_header = by_test_id(page, "history-table").locator("th", has_text="Latency")
    click(page, latency_header)
    page.wait_for_timeout(900)
    click(page, latency_header)
    clock.at(0.6)
    search = by_test_id(page, "history-search").locator("input")
    click(page, search)
    search.press_sequentially("compare", delay=90)
    clock.at(0.9)
    search.fill("")


def scene_closing(clock: SceneClock) -> None:
    page = clock.page
    click(page, by_test_id(page, "tab-about"))
    clock.at(0.55)
    glide_to(page, page.locator(".v-list-item", has_text="Source code"), steps=40)


SCENES: dict[str, Callable[[SceneClock], None]] = {
    "title": scene_title,
    "about": scene_about,
    "agent-ask": scene_agent_ask,
    "agent-answer": scene_agent_answer,
    "ci-ask": scene_ci_ask,
    "ci-answer": scene_ci_answer,
    "compare-ask": scene_compare_ask,
    "compare-result": scene_compare_result,
    "history": scene_history,
    "closing": scene_closing,
}

# ---------------------------------------------------------------- runner


def run_scene(recorder: Recorder, scene_id: str, clip: float) -> None:
    page = recorder.page
    start = time.monotonic()
    clock = SceneClock(page, start, clip)
    SCENES[scene_id](clock)
    remaining = start + clip + SCENE_PAD_S - time.monotonic()
    if remaining > 0:
        page.wait_for_timeout(remaining * 1000)
    end = time.monotonic()
    entry = {
        "id": scene_id,
        "start": round(start - recorder.origin, 3),
        "end": round(end - recorder.origin, 3),
        "clip": clip,
    }
    recorder.entries.append(entry)
    print(f"- {scene_id}: {entry['start']:.1f}s -> {entry['end']:.1f}s (clip {clip:.1f}s)")


def open_app(page: Page, url: str) -> None:
    page.goto(url, wait_until="networkidle")
    page.locator('[data-testid="agent-status"]', has_text="Agent ready").wait_for(timeout=60_000)
    page.evaluate("html => document.body.insertAdjacentHTML('beforeend', html)", TITLE_HTML)
    page.mouse.move(VIEWPORT["width"] * 0.7, VIEWPORT["height"] * 0.75)
    page.wait_for_timeout(500)


def record_take(browser: Browser, url: str, manifest: list[dict]) -> dict[str, object]:
    """Record one full take into a fresh recording directory; raises RetakeError if an answer is off-script."""
    shutil.rmtree(RECORDING_DIR, ignore_errors=True)
    RECORDING_DIR.mkdir(parents=True)
    context = browser.new_context(
        viewport=VIEWPORT,
        record_video_dir=str(RECORDING_DIR),
        record_video_size=VIEWPORT,
        color_scheme="light",
        locale="en-US",
        timezone_id="Europe/Paris",
    )
    try:
        context.add_init_script(CURSOR_SCRIPT)
        page = context.new_page()
        page_created = time.monotonic()
        open_app(page, url)
        recorder = Recorder(page, url, origin=time.monotonic())
        for item in manifest:
            run_scene(recorder, item["id"], float(item["duration"]))
        wall_end = time.monotonic()
        video_path = page.video.path() if page.video else None
    finally:
        context.close()
    return {
        "url": url,
        "video": str(video_path),
        "video_offset": round(recorder.origin - page_created, 3),
        "wall_duration": round(wall_end - page_created, 3),
        "duration": round(wall_end - recorder.origin, 3),
        "scenes": recorder.entries,
    }


def capture(url: str, headed: bool, max_takes: int) -> None:
    manifest = read_json(AUDIO_MANIFEST)
    missing = [item["id"] for item in manifest if item["id"] not in SCENES]
    if missing:
        raise SystemExit(f"narration scenes without a capture function: {missing}")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="msedge", headless=not headed)
        try:
            for take in range(1, max_takes + 1):
                print(f"Take {take}/{max_takes}")
                try:
                    timeline = record_take(browser, url, manifest)
                    break
                except RetakeError as error:
                    print(f"  answer did not match the narration ({error}); recording a new take")
            else:
                raise SystemExit(f"No usable take after {max_takes} attempts")
        finally:
            browser.close()

    write_json(TIMELINE_FILE, timeline)
    print(f"Recorded {timeline['video']}; timeline -> {TIMELINE_FILE}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--headed", action="store_true", help="show the browser window")
    parser.add_argument("--max-takes", type=int, default=MAX_TAKES)
    args = parser.parse_args()
    capture(args.url.rstrip("/"), args.headed, args.max_takes)


if __name__ == "__main__":
    main()
