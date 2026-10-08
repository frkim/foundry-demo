# Microsoft Foundry session deck

Marp source for the 90-minute technical session **"Microsoft Foundry: build, ship and govern AI agents"**.
The deck covers the Foundry resource and projects, the model catalog, Foundry Agent Service, Microsoft Agent
Framework, observability and governance, the AI Gateway (Azure API Management) and the Bicep + GitHub Actions
delivery pipeline used by the **Foundry Guide** demo in this repository.

| File | Purpose |
|---|---|
| `foundry-session.md` | The deck (54 slides). Speaker notes are HTML comments (`<!-- … -->`) on every slide. |
| `themes/foundry.css` | Custom Marp theme `foundry` (navy/indigo surfaces, violet → cyan accents, Segoe UI). |
| `.marprc.yml` | Marp CLI defaults: HTML enabled, local files allowed, theme set `./themes`. |
| `package.json` / `package-lock.json` | Pinned `@marp-team/marp-cli`; all tarballs resolve through the protected npm feed. |
| `.npmrc` | `registry=https://packagefeedproxy.microsoft.io/npm/` — never point it at a public registry. |
| `assets/` | Optional images for the deck (diagrams are inline SVG, so none are required today). |

## Prerequisites

- Node.js **24+** (`engines` is enforced through `engine-strict=true` in `.npmrc`).
- A Chromium-based browser (Chrome or Edge) for PDF, PPTX and PNG output. Marp finds it automatically; set
  `CHROME_PATH` if it does not.

## Build

```powershell
cd docs/presentations
npm ci
npm run build:all      # dist/foundry-session.html, .pdf (with notes) and .pptx
```

| Script | Output |
|---|---|
| `npm run build:html` | `dist/foundry-session.html` — self-contained HTML deck with presenter view |
| `npm run build:pdf` | `dist/foundry-session.pdf` — includes speaker notes as PDF annotations |
| `npm run build:pptx` | `dist/foundry-session.pptx` — slides as images, speaker notes as PowerPoint notes |
| `npm run build:all` | All three |
| `npm run preview` | Opens a live-reloading preview window while you edit |

`dist/` is git-ignored. The `deck` GitHub Actions workflow builds the same outputs on every push to `main` that
touches this folder and publishes them to GitHub Pages; `ci.yml` builds the HTML on pull requests.

To review layout, render every slide as PNG into the git-ignored `tmp/` folder at the repository root:

```powershell
npx marp foundry-session.md --images png --allow-local-files --html --theme-set themes -o ../../tmp/deck-png/slide.png
```

## Present

1. Open `dist/foundry-session.html` in a browser.
2. Press **P** to open the presenter view (current/next slide, speaker notes, timer).
3. Press **F** for full screen. Arrow keys or the space bar navigate.

Each section divider's notes carry the planned time window (for example `[00:25 · Section 3 — Agents, 15 minutes]`),
so you can check your pace from the presenter view. Replace the `[Speaker name]` placeholders on slides 2 and 54
before presenting. The demo runbook and Q&A prep live in `docs/session/`.

## Theme reference (`themes/foundry.css`)

Use the theme with `theme: foundry` in the front matter and `--theme-set themes` on the CLI.

### Slide classes

| Class | Use | Example |
|---|---|---|
| `lead` | Title slide — dark gradient, large title | `<!-- _class: lead -->` |
| `section` | Section divider — big gradient number (`<span class="num">03</span>`) and timing pill (`<span class="time">…</span>`) | `<!-- _class: section -->` |
| `closing` | Q&A / thank-you slide (same look as `lead`) | `<!-- _class: closing -->` |

Content slides need no class: the `# H1` becomes the slide title with a gradient underline.

### Building blocks

| Class | Description |
|---|---|
| `eyebrow`, `meta` | Pill label above the title and the muted meta line on `lead` / `closing` slides |
| `kicker` | Lead-in sentence below the title |
| `cols`, `cols-3`, `cols-4`, `cols-60`, `cols-40` | Grid layouts (2 equal, 3, 4, 60/40, 40/60 columns) |
| `card` + `cyan` / `teal`, `green`, `amber`, `red`, `navy`, `dark` | Content card with a coloured top border (`dark` = filled navy) |
| `kpi` + `alt`, `warn`, `dark` | Metric tile: `<div class="v">` value, `<div class="l">` label, `<div class="d">` date/source |
| `pill` + `ok`, `prev`, `todo`, `ret`, `info` | Status pills — GA, Preview, to-do, Retiring, info |
| `callout` + `warn`, `violet` | Highlighted note with a coloured left border |
| `steps` (+ `s3`, `s5`) | Numbered process steps (4 columns by default) |
| `checklist` | Checkbox list — wrap a `<ul>` in `<div class="checklist">` |
| `agenda` | Agenda grid: `.n` number badge (add `demo` for demo blocks), `.t` title, `.m` minutes |
| `diagram`, `legend` | Container for inline SVG diagrams and its numbered legend |
| `tag`, `small`, `muted`, `codecap`, `mt`, `mt-s` | Small chips, muted text, caption under code, spacing helpers |

### Authoring rules

- Keep code blocks to **15 lines or fewer** and ~100 characters per line (full width) or ~45 (in a column).
- Every content slide carries 2–5 sentences of talk track in an HTML comment — Marp exports these as notes.
- Do not leave blank lines inside raw HTML blocks (`<div>`, `<svg>`): Markdown would end the HTML block there.
- Label every feature with its status pill and only state facts confirmed in Microsoft Learn or official blogs.

## Supply chain

- Packages are installed only from `https://packagefeedproxy.microsoft.io/npm/`; every `resolved` URL in
  `package-lock.json` points at that feed. Do not "fix" a failed install by switching to a public registry.
- `overrides` pins patched versions of vulnerable transitive dependencies (`@xmldom/xmldom`, `basic-ftp`, `katex`).
- `npm audit` still reports `extract-zip` (pulled in by `puppeteer-core` → `@puppeteer/browsers`) because no patched
  version exists. It is only used to download browsers, which the build never does (it uses the installed Chrome or
  Edge), so the risk is accepted for this documentation-only tool.
