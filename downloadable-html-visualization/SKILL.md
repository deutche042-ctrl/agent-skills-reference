---
name: downloadable-html-visualization
description: >
  Produce ONE self-contained, downloadable .html file for visual or interactive
  deliverables: data reports, dashboards, infographics, posters, HTML slide decks,
  interactive apps/tools/games, charts, and node-link diagrams
  (timelines, flowcharts, org/family trees, relationship graphs, mind maps). Enforces
  Layout Archetypes, genre-first font/color rotation, palette-themed charts, diagram
  geometry, interactive-JS safety, and data accuracy. Use when the user explicitly asks
  for a downloadable, standalone, exportable or saveable HTML file, or wants something
  to open, host, print, or share outside the chat; the file is delivered as an
  attachment via NotifyHuman. For ordinary in-chat visuals, use `dola-visualization`
  instead — this is the file-deliverable supplement, not the default path.
  Triggers: visualize, data report, dashboard, chart, infographic, html report,
  html slide deck, interactive app/tool/calculator/game, flowchart, org tree, mind map.
metadata:
  version: "6.3.0"
  category: visualization
  tags: "html, visualization, dashboard, chart, infographic, slides, diagram, downloadable, artifact, archetype"
  delivery: downloadable-file
  based_on: "Web Design & Visualization Handbook — Downloadable HTML Edition"
---

# Web Design & Visualization Handbook — Downloadable HTML (MoA Edition)

When a request calls for a visual or interactive deliverable, produce a **self-contained HTML artifact** and deliver it as a downloadable file via `NotifyHuman`. HTML is the most universally accessible format, so prefer it for visual work.

This is the **file-deliverable supplement, not the default visual path.** It owns the request once the user asks for a downloadable, standalone, exportable or shareable HTML file, or wants something to open, host, print, or share outside the chat — or when the environment has no streaming renderer. Ordinary in-chat visuals belong to the default visualization skill. Everything below assumes you are already on the file path.

### What to build as an HTML artifact

Once on this path, an HTML artifact is the right shape for anything fundamentally visual or interactive, including:
- Visualizations, infographics, posters, charts/dashboards, data reports
- HTML slide decks / web presentations
- Interactive apps, tools, calculators, configurators, simulators, mini-games
- Diagrams: timelines, flowcharts, org/family trees, relationship graphs, mind maps

For these, an HTML artifact is the deliverable. Do NOT answer such requests with only a Markdown table, an ASCII chart, or a plain text description when an HTML artifact would serve the user better.

**Build decks as HTML sections, not with a slide framework.** This skill covers a deck only when the deck itself is meant to be HTML — a web deck, an HTML presentation, or slides inside a downloadable page. Render it as a sequence of styled slide `<section>`s in one document (see the Slides/Deck archetype) rather than pulling in reveal.js or Impress.js.

**When the user names a different file format, give them that format, not HTML.** An explicit ask for an editable `.pptx`, a PDF, a Word document, or a spreadsheet is a request for that artifact, not for a web page — produce it with the tooling that owns that format and hand it over the same way. This skill applies when HTML is the deliverable.

### Delivery model (CRITICAL — read first) — MoA artifact pipeline

The deliverable is ONE **self-contained `.html` file written into your agent workspace and handed off via `NotifyHuman`**; the MoA harness collects it as an artifact and presents it to the user. Do **NOT** paste a large HTML block into your final message, and do **NOT** emit a ` type="renderer" ` fence — those are for other environments and will not be captured as an artifact here.

1. **Write the file with `Write`** (or a `Bash` heredoc) to your artifacts directory — `<<ARTIFACTS_DIR>>` if your prompt exposes it, otherwise the agent workspace root. One standalone `.html` file, at an **absolute path** (steps 2 and 3 both need one).
2. **Self-check before delivery (mandatory, but render ONCE).** Use **exactly this** two-step contract — the gate requires you to *render with `artifact-preview` AND `Read` its output*:

   ```bash
   # Step A — render ONCE (positional path; do NOT pass --width/--height or other invented flags):
   <<SKILL_REMOTE_LOCATION>>/artifact-preview/bin/preview render /abs/path/to/your.html
   # → prints JSON with: output_dir, thumbnail, pages:[".../pages/p001.png", ...], collages

   # Step B — Read the render's OWN output (thumbnail first; a page/collage only if you need detail):
   # Read <output_dir>/thumb.jpg
   ```
   Reading **artifact-preview's own output** is what satisfies the gate; reading some other image does not. Also run `verifier-hub` on the file. Fix everything you spot in that **single** pass, then deliver.

   - **Render ONCE — do NOT loop** render→tweak→re-render (each render is a full headless-browser pass, very slow); one visual check is enough.
   - **Use ONLY `artifact-preview` for screenshots — never build your own pipeline.** Do NOT use `selenium`, `playwright`, raw `chromium-browser`/`google-chrome` (it fails in this sandbox), `node` scripts, `pip install`/`npm install`, or `python -m http.server` to capture the page — those rabbit holes waste many turns and the gate won't credit them anyway.
   - For `verifier-hub`, the family is `verifier file <subcmd> ...` (e.g. `verifier file validate <path>`) — don't guess subcommands like `verifier check`.
   - **If the render genuinely fails to produce an image, skip the visual check and deliver anyway** (note "preview render unavailable" in your summary). This includes the case where `<<SKILL_REMOTE_LOCATION>>` reaches you **unsubstituted** or no binary sits at that path — do not hunt for it and do not roll your own screenshot tooling.
3. **Deliver via `NotifyHuman`**, attaching the `.html` file. Briefly describe what the artifact contains in your message text; the file itself is the deliverable. Never end the task without the saved file delivered through `NotifyHuman`.

The user opens the file in a **real browser**, so the artifact must be a complete standalone HTML document (see relaxed rules below). It needs internet access when opened (CDN libraries and web fonts load remotely).

### Workflow for data-driven artifacts (search → compute → build)

When the artifact depends on real information or numbers, follow this order — **do not** jump straight to writing HTML with guessed values:

1. **Gather information** — use `general_search` / `web.fetch` (and other available retrieval tools) to collect the facts, figures, and source data the artifact needs. Capture exact numbers and their sources. **Use at most ~10 search turns total** — gather enough to be accurate, then stop and build; do not over-search.
2. **Compute in the sandbox** — use `Bash` (run Python: numpy / pandas / scipy, etc.) or the code-execution tool to download/parse the data and do any calculation, aggregation, statistics, date math, currency/unit conversion, sorting/filtering. **Print** the results so you can reference exact values when writing the HTML. This step is **MANDATORY** whenever the artifact involves: >5 data points needing transformation, date/time math, statistical measures, conversions, or sorting/aggregating a dataset.
3. **Build the HTML** — use `Write` to assemble the self-contained `.html`, embedding the **computed** values from step 2 (and search facts from step 1) as JS variables / table cells. Then self-check (`artifact-preview` + `verifier-hub`) and deliver via `NotifyHuman`.

**Data accuracy is non-negotiable:** every number in the artifact must trace back to step-1 search results, step-2 sandbox output, or explicit user input. **Hardcoding guessed/fabricated numbers is forbidden** — label any unavoidable sample data as a placeholder in both the UI and your reply.

### Writing the file safely (avoid escape corruption)

**Prefer the `Write` tool** to save the `.html` — it writes your content verbatim, so there is **no Python-string escaping hazard** (LaTeX `\frac`/`\theta`, CSS, regex survive intact). This is the recommended path in MoA.

**The one thing you must never type out is image data.** `Write` emits whatever you author, so authoring a `data:image/...;base64,…` payload dumps hundreds of KB into your own output and back into your context on every later turn. Write `__IMG1__`-style placeholders where the pictures go and let a short Python step swap in the base64 (Step D of *Icon & Visual Enrichment*). That is the only way to satisfy both "author the HTML verbatim" and "keep the payload out of your output."

Only if you generate the HTML programmatically (a `Bash` heredoc running Python, e.g. to inject many computed values) does the escape hazard apply: Python interprets `\t`, `\f`, `\r`, `\n`, `\b` inside ordinary strings as control characters, which **destroys LaTeX, CSS, and regex** embedded in your HTML. In that case:

- Put the HTML in a **raw triple-quoted string** (`r"""..."""`) and write with UTF-8.
- Compute values as Python variables first and inject via `str.replace("__PLACEHOLDER__", value)` or concatenation — avoid f-strings/`.format` directly around CSS `{...}` braces and LaTeX backslashes.

```python
peak = 5230                                    # Phase 1: produced by real computation, never guessed
html = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>Artifact Title</title>
<style> ... palette + layout CSS ... </style></head>
<body>
... full document ...
<span id="peak">__PEAK__</span>                <!-- content lives in <body>, never in <head> -->
</body></html>"""                              # Phase 2: RAW string, values injected by replace
out = "/abs/path/to/workspace/visualization.html"   # absolute — preview + NotifyHuman both need one
with open(out, "w", encoding="utf-8") as f:
    f.write(html.replace("__PEAK__", f"{peak:,}"))
print("saved", out)
```

Then run `artifact-preview` + `verifier-hub` on the file and deliver it via `NotifyHuman` (see *Delivery model* above).

### Standalone-document rules — what is RELAXED here

Because the artifact runs as a normal page in a real browser (NOT a sandboxed streaming iframe renderer), the streaming-renderer restrictions are **lifted**. In this environment you SHOULD:

- Write a **complete document**: `<!DOCTYPE html><html><head>…</head><body>…</body></html>`. `<head>` and `<body>` are expected (not forbidden).
- Put CSS in a normal `<style>` block in `<head>` (the `document.createElement('style')` injection hack is unnecessary — but still fine).
- Use `100vh`, `min-height:100vh`, `height:100%`, and fixed heights freely — there is a real viewport, no infinite-growth ResizeObserver problem.
- Use normal script placement and `DOMContentLoaded` / `window.onload` if convenient — the page loads normally, so listeners fire.
- Write the whole artifact in one file — there is **no 250/300-line block limit** and no block-splitting; a single interactive app keeps its DOM and script together naturally.
- Do NOT use a renderer fence (the `type="renderer"` HTML block from the streaming environment) and do NOT rely on streaming `nth-child` reveal timing — those were renderer-only mechanics.
- **NOT relaxed**: there is still no build step, so JSX, TypeScript, and bundler-style `import` from bare package names cannot compile — stay on vanilla HTML/CSS/JS. A framework is viable only as a browser-ready CDN build, and is rarely worth its weight in a single-file artifact.

Everything below (design system, fonts, colors, charts, diagrams) still applies — it is what makes the artifact look professional.

---

### Core Design Philosophy

**Make creative, distinctive frontends that surprise and delight.** Fight the instinct to converge toward generic output. Every artifact should feel intentionally designed for its specific context — a financial report should look different from a biology tutorial or a travel guide, and the Layout Archetype System is the enforcement mechanism, since structure is chosen per genre. Lean toward the bold and unexpected over the safe and conventional; include hover effects, animation, and interactive chart elements. Content is king — all design serves clarity and comprehension.

### Style Auto-Inference (do this BEFORE choosing an archetype)

When the user does not name a style — "just make me an html report" — you still have to choose a distinctive one. **Never default to a generic look.** Infer archetype and category from the content:

| Content pattern | Archetype | Category |
|---|---|---|
| News / current events / daily digest | Editorial / Newspaper | News/Editorial |
| Paper summary / research / key findings | Document / Handbook | Science/Research |
| Rankings / KPIs / benchmarks / market data / "A vs B" | Dashboard / Report | Finance/Markets or the subject's category |
| Tutorial / how-to / explainer / study notes | Document / Handbook | Education/Learning |
| Travel / food / lifestyle / gallery / resume / portfolio | Magazine / Showcase | Travel/Geography, Food/Lifestyle, or Creative/Design |
| Algorithm / system diagram / relationship / scientific process | Canvas-first / Diagram | Science/Research or Education/Learning |
| Game / puzzle / quiz / interactive challenge | Game / Interactive | Education/Learning or Entertainment/Media |
| Calculator / converter / configurator / form | App / Tool | Technology/Engineering or the subject's category |
| Timeline / chronology / historical progression | Editorial / Newspaper | History/Culture or News/Editorial |
| Sports stats / match results | Dashboard / Report | Sports/Events |
| Financial report / stock analysis | Dashboard / Report | Finance/Markets |
| Health metrics / fitness / medical info | Dashboard / Report | Health/Nature |
| Code / API documentation | Document / Handbook | Technology/Engineering |
| Pitch / lesson / conference talk | Slides / Deck | the subject's category |

**The inference rule**: imagine the user HAD specified a style — what would they most naturally have said? A news roundup user would have said "newspaper style"; a research summary user would have said "academic paper style"; a metrics comparison user would have said "dashboard." Pick THAT. Omitting the style hint is not permission to produce bland output — it means the decision is yours to make. When the user DOES specify a style, use their choice directly and skip the inference.

**Then pick the FORM of expression** — the archetype sets page structure, the form sets what the dominant element actually is:

| User intent signal | Best form | Wrong form |
|---|---|---|
| "show me the difference intuitively" / "visualize the gap" | Animated comparison, race, side-by-side scale | Static bar chart with no narrative |
| "step by step" / "dynamically demonstrate" / "process" | Animated SVG/Canvas with play/pause and staged reveal | Static diagram showing all steps at once |
| "timeline" / "chronology" / "history of" | Dated nodes along a scrollable timeline | Bullet list or plain table |
| "visual card" / "flashcard" / "summary card" | Compact card layout of key-value pairs with icons | Dense paragraph |
| "academic table" / "three-line table" | Bordered table with header/footer rules, serif, no zebra striping | Colorful dashboard cards |
| "comparison" / "A versus B" | Split-screen or side-by-side columns sharing metrics | Single merged list |
| "interactive" / "try it" / "play" | Working controls with immediate visual feedback | Static mockup that looks interactive |

### Layout Archetype System (MANDATORY — choose BEFORE writing any HTML)

Pick the archetype by what the artifact **IS** (its genre), not what it is **ABOUT** (its subject). An AI news digest is Editorial, not a Technology dashboard; a finance-themed puzzle is a Game, not a Finance report.

| Archetype | Typical requests | Structure recipe |
|-----------|------------------|------------------|
| **Editorial / Newspaper** | news digests, briefings, essays, reviews | Masthead + dateline → kicker + serif headline → lede → article blocks separated by 1px hairlines (NO card boxes) → pull quotes → colophon footer |
| **Dashboard / Report** | data analysis, KPI summaries, financial reports | hero → metric cards → charts → tables → footer |
| **Document / Handbook** | study notes, tutorials, outlines, plans | Title block → table of contents → prose sections in a narrow reading column (`max-width:48rem;margin:0 auto`) with headings, callout boxes, code blocks |
| **Game / Interactive** | puzzles, quizzes, games, simulators | Start screen (title + tagline + Start button) → gameplay screen (board/play area front and center + HUD + tactile controls with pressed states) → end/result overlay. No hero, no metric cards |
| **Magazine / Showcase** | travel, food, lifestyle, galleries | Lead image (verified + inlined per *Icon & Visual Enrichment*) or a bold typographic/CSS hero → captioned content blocks interleaved with short prose → sparse highlight cards. The layout must still hold up on type, color, and SVG alone if no image survives verification |
| **Canvas-first / Diagram** | relationship graphs, maps, flowcharts, 3D | One-line title → the visualization as the dominant element (generous height, 500–650px) → compact legend → nothing else |
| **App / Tool** | calculators, converters, configurators, forms | Input controls + live output side by side (flex-wrap) → brief explanation below |
| **Slides / Deck** | HTML decks, web presentations, pitch decks | A sequence of full-width slide `<section>`s (one idea each: title slide, agenda, content slides, closing); large type, generous padding, consistent footer/slide number; optional keyboard/arrow nav |

**Anti-convergence rules:**
- Metric-card rows are **exclusive to the Dashboard/Report archetype.** Elsewhere, highlight numbers with a `<dl>`, bold inline text, or a styled `<table>` — not flex-wrap hover cards.
- Outside Dashboard, also avoid monospace `01`-numbered section headers and the 44×44 gradient-icon hero.
- **Template self-check** before output: if swapping in text on any other topic would leave the page looking equally appropriate, you produced a generic template — restructure per the archetype.

### Game / Interactive Screen Flow

For games, puzzles, quizzes, and simulators, the player must land on a **Start Screen** before entering the active play state — never dump them into a running game. Required screens:

| Screen | Purpose | Required elements |
|--------|---------|-------------------|
| **Start / Landing** | Introduce the game and let the player opt in | Large game title; one-line tagline; prominent **Start** primary button; optional compact rules / difficulty selector; muted footer/credits |
| **Gameplay** | The active interactive experience | Compact HUD (score, timer, lives, level) at top or overlaid; main play area centered; tactile controls with `:active` pressed states; pause/restart accessible |
| **Pause (optional)** | Suspend without losing state | Resume / Restart / Quit buttons, dimmed backdrop |
| **Game Over / Result** | Celebrate or summarize the outcome | Final score/stats; high-score persistence (`localStorage`); **Play Again** primary button; optional share/quit. For endless or casual games this becomes a session summary — count, time played, personal best |

**Hard rules for the Start screen:**

- The **Start screen must block the game world** on first load. The play area, HUD, score, and controls are either hidden (`display:none`) or visually covered by the start overlay until the player clicks Start.
- **State machine `start | playing | paused | ended`** drives every screen, HUD, and overlay from one variable (this is Interactive JS Safety rule C1). The initial render is `state === 'start'`, before any `requestAnimationFrame` loop or auto-spawner runs; the move to `playing` happens only via an explicit click on Start.
- Button labels should be action verbs indicating the beginning of play (e.g., **Start / Play / Deploy / Begin**). Avoid labels that imply clearing, resetting, or administrative actions — those belong inside gameplay (Pause) or at the end (Play Again).
- **No emoji** in the title, tagline, buttons, or instructions on any game screen. Use inline SVG icons or Lucide/Remix icons instead.

**Minimal pattern:**

```html
<style>.hidden{display:none}</style>
<div id="stage" style="position:relative">
  <div id="playArea" class="hidden">…board / canvas…</div>
  <div id="hud" class="hidden">…score / timer…</div>
  <div id="startScreen"><h1>Title</h1><p>tagline</p><button id="startBtn">Start</button></div>
  <div id="gameOver" class="hidden">…final score…<button id="againBtn">Play Again</button></div>
</div>
<script>
(function(){
  var state = 'start';                        // start | playing | paused | ended
  var screens = {
    startScreen: document.getElementById('startScreen'),
    gameOver:    document.getElementById('gameOver'),
    hud:         document.getElementById('hud'),
    playArea:    document.getElementById('playArea')
  };
  var visibleIn = {                           // which states each element belongs to
    startScreen: ['start'], gameOver: ['ended'],
    hud: ['playing','paused'], playArea: ['playing','paused','ended']
  };

  function startLoop(){ /* rAF loop, spawners, timers — registered centrally (A5) */ }
  function stopLoop(){  /* cancelAnimationFrame + clear every registered timer (A5) */ }
  function resetGame(){ /* factory reset: state, timers, arrays, generated DOM (C3) */ }

  function setState(next) {
    state = next;
    Object.keys(screens).forEach(function(k){
      screens[k].classList.toggle('hidden', visibleIn[k].indexOf(state) === -1);
    });
    if (state === 'playing') startLoop();     // loops/spawners start ONLY here
    else stopLoop();                          // and are cleared on every other transition
  }

  document.getElementById('startBtn').addEventListener('click', function(){ setState('playing'); });
  document.getElementById('againBtn').addEventListener('click', function(){ resetGame(); setState('playing'); });
  setState('start');                          // initial render: start screen blocks the game world
})();
</script>
```

### Font Rotation System (MANDATORY)

**BANNED**: `Manrope`, `Outfit`, `Inter`, `Roboto`, `Arial`, `Plus Jakarta Sans`, `Space Grotesk` — NEVER use.

Pick the category by the **genre-first rule**, then pick **ONE** font deterministically: count ALL characters of the artifact's title (including spaces and punctuation; each non-Latin character counts as one) and take the count modulo 3 → 0 = first option, 1 = second, 2 = third. Do NOT default to the first option.

| Category | Font options (0 · 1 · 2) |
|----------|--------------|
| Finance/Markets | `Cormorant Garamond` · `Spectral` · `Newsreader` |
| Science/Research | `IBM Plex Sans` · `Source Sans 3` · `Public Sans` |
| Creative/Design | `Syne` · `Archivo` · `Bricolage Grotesque` |
| Health/Nature | `Nunito` · `Figtree` · `Karla` |
| Education/Learning | `Fredoka` · `Baloo 2` · `Comfortaa` |
| Technology/Engineering | `Sora` · `Chakra Petch` · `Red Hat Display` |
| Sports/Events | `Unbounded` · `Oswald` · `Saira` |
| Food/Lifestyle | `Quicksand` · `Josefin Sans` · `Epilogue` |
| Travel/Geography | `DM Sans` · `Albert Sans` · `Work Sans` |
| History/Culture | `Playfair Display` · `EB Garamond` · `Crimson Pro` |
| Math/Statistics | `Source Serif 4` · `Fraunces` · `Zilla Slab` |
| News/Editorial | `Lora` · `Noto Serif` · `Frank Ruhl Libre` |
| Entertainment/Media | `Urbanist` · `Bricolage Grotesque` · `Red Hat Display` |

Load via `<link href="https://fonts.googleapis.com/css2?family=FONT:wght@400;500;600;700&display=swap" rel="stylesheet">` — **spaces in the font name become `+`** (`family=Cormorant+Garamond`), or the request 404s and the page silently falls back to a system font. For Editorial/Magazine/History you may add ONE neutral body font (`Source Sans 3` · `Public Sans` · `Karla`) chosen by the same rule; two `<link>` tags max.

### Color Rotation System (MANDATORY)

**BANNED as `--bg`**: `#0f172a`, `#020617`, `#0a0a0f`. Technology/Engineering is ONLY for hardware/software-engineering/networking subjects — AI/ML, math/physics sims, algorithm explainers, tech earnings, tech news, paper summaries each map to their own row (Education, Science, Finance, News, Science respectively).

Every category defines a primary AND a secondary accent — use `--accent2` for chart series #2, duotone gradients, comparison layouts, and gradient text.

| Category | --bg | --card | --text | --muted | --accent | --accent-soft | --accent2 | --accent2-soft | --border |
|----------|------|--------|--------|---------|----------|---------------|-----------|----------------|----------|
| Finance/Markets | `#1c1f2e` | `#262a3a` | `#e8ecf4` | `#8b9ab8` | `#c9923c` | `rgba(201,146,60,.14)` | `#4d8b7a` | `rgba(77,139,122,.14)` | `rgba(139,154,184,.16)` |
| Science/Research | `#f8fafb` | `#ffffff` | `#0f172a` | `#64748b` | `#2d7eb5` | `rgba(45,126,181,.14)` | `#c85a3a` | `rgba(200,90,58,.14)` | `rgba(15,23,42,.08)` |
| Creative/Design | `#1f1f21` | `#2a2a2d` | `#f4f4f5` | `#a1a1a8` | `#7aac2b` | `rgba(122,172,43,.14)` | `#c4a87c` | `rgba(196,168,124,.14)` | `rgba(161,161,168,.18)` |
| Health/Nature | `#f7fcf9` | `#ffffff` | `#0f172a` | `#64748b` | `#0d9669` | `rgba(13,150,105,.14)` | `#d4724a` | `rgba(212,114,74,.14)` | `rgba(15,23,42,.08)` |
| Education/Learning | `#faf9f4` | `#ffffff` | `#0f172a` | `#64748b` | `#297a2e` | `rgba(41,122,46,.14)` | `#d97706` | `rgba(217,119,6,.14)` | `rgba(15,23,42,.08)` |
| Technology/Engineering | `#202024` | `#2a2a2f` | `#e8e5df` | `#9a978f` | `#c47046` | `rgba(196,112,70,.14)` | `#7ba8b8` | `rgba(123,168,184,.14)` | `rgba(232,229,223,.12)` |
| Sports/Events | `#faf9f7` | `#ffffff` | `#0f172a` | `#64748b` | `#dc4a38` | `rgba(220,74,56,.14)` | `#2563ab` | `rgba(37,99,171,.14)` | `rgba(15,23,42,.07)` |
| Food/Lifestyle | `#fefcf8` | `#ffffff` | `#0f172a` | `#64748b` | `#ea580c` | `rgba(234,88,12,.14)` | `#16a34a` | `rgba(22,163,74,.14)` | `rgba(15,23,42,.07)` |
| Travel/Geography | `#f6fbf9` | `#ffffff` | `#0f172a` | `#64748b` | `#0d9488` | `rgba(13,148,136,.14)` | `#c4693d` | `rgba(196,105,61,.14)` | `rgba(15,23,42,.07)` |
| History/Culture | `#fcfaf6` | `#ffffff` | `#0f172a` | `#64748b` | `#b45309` | `rgba(180,83,9,.14)` | `#2d6b8a` | `rgba(45,107,138,.14)` | `rgba(15,23,42,.07)` |
| Math/Statistics | `#f9f9f8` | `#ffffff` | `#0f172a` | `#64748b` | `#ba3b5b` | `rgba(186,59,91,.14)` | `#0d8a7d` | `rgba(13,138,125,.14)` | `rgba(15,23,42,.08)` |
| News/Editorial | `#f9f9fa` | `#ffffff` | `#0f172a` | `#64748b` | `#dc2626` | `rgba(220,38,38,.14)` | `#1e40af` | `rgba(30,64,175,.14)` | `rgba(15,23,42,.07)` |
| Entertainment/Media | `#fdf9fb` | `#ffffff` | `#0f172a` | `#64748b` | `#bd3193` | `rgba(189,49,147,.14)` | `#0891b2` | `rgba(8,145,178,.14)` | `rgba(15,23,42,.07)` |

- Both `-soft` variants are 14%-alpha derivatives of their accent — use them for icon backgrounds, soft fills, gradient tails, and chart area fills. Use `var(--border)` for ALL card borders, dividers, and table rules (not neutral gray `rgba(128,128,128,...)`, which reads muddy on tinted backgrounds). Define the palette once as CSS variables in `<head>` (`:root{--bg:…}`); charts cannot read CSS variables, so hardcode the SAME hex values in chart options.
- **Light-palette preference**: 10 of 13 categories are light by default; only Finance, Creative, and Technology are dark. When the user names no visual tone, use the row as-is and never darken a light category on your own initiative.
- **Accent contrast — these accents are mid-tone, so small text needs care.** On `var(--accent-soft)`, small text is always `color:var(--text)`: `var(--accent)` reaches 4.5:1 on its own soft fill in NO category, so tinting a small label accent is the most common contrast bug here — add `border:1px solid var(--accent)` when the control needs accent presence. Icon glyphs need only 3:1 and always pass. On a solid accent fill, `#fff` works for Education, Entertainment, History, Math, and News, `var(--bg)` for the dark-background rows Finance and Creative, and `var(--text)` for Health, Food, and Travel; Science, Technology, and Sports clear 4.5:1 against no label color at all, so either set the label ≥18px bold to fall under the 3:1 large-text bar or use the soft fill instead.

### Icon & Visual Enrichment

**Real images: source them, verify them, then embed the bytes.** For topics with real-world entities the user wants to SEE (travel, landmarks, food, architecture, people, products), photos are worth having. Three sources are eligible, in this order:

- **Step A — user-supplied URLs**: image URLs the user gave you in this conversation. Most reliable.
- **Step B — `<uri>` tags in search results**: some `<image>` elements contain a `<uri>` with a real HTTP URL. Use it **verbatim, entire query string included** — signed URLs carry `?lk3s=…&x-expires=…&x-signature=…` and dropping any part is an instant 403. An `<image reference_id="…">` with **no** `<uri>` is a chat-UI display reference, not an embeddable URL. Never recall a URL from memory (Wikipedia, Unsplash, brand CDNs) and never construct one that merely looks like a signed path — fabricated URLs are the single biggest source of broken images.
- **Step B2 — generate one with `image_gen`, when search comes up empty and the slot is decorative.** If A and B yield nothing usable and `image_gen` is available to you, generating the picture beats shipping a hole. Legitimate uses are conceptual or atmospheric: a hero backdrop, a section header, mood imagery for a travel or food piece, character and scene art for a game. Illegitimate uses are anything a reader would take as evidence — a specific person, a real building or place, a news event, an actual product. Inventing those is fabrication in picture form, no different from inventing a statistic; in factual or journalistic content, a generated image must be labeled as an illustration in its caption. Prompt it to match what you are building — name the palette's accent color, the genre, and the aspect ratio the slot needs — and ask only for photographic or illustrative content: image models render text, labels, charts, logos, and UI as garbled nonsense, so never generate anything that carries type or data. Use `image_edit` to adapt a picture you already have — recrop or extend a hero to the aspect ratio the slot needs, or restyle a user-supplied image to sit with the palette — but never to change what a real photograph depicts, which turns a true picture into a false claim as surely as generating a fake one. Budget one or two generated images for the slots that carry the page, not one per card.
- **No source at all = no image.** Cut the slot from the layout. Never substitute an emoji, a gray placeholder box, or a "no image" icon — a text-only card beats a broken one.

**Step C — verify in the sandbox, on two axes. Both are mandatory; neither substitutes for the other.**

*Reachable?* (anything you hold as a URL, including a generated image handed back as one; a file already on disk skips this.) Fetch the URL in CI and keep only the ones returning `200` — this catches truncated signatures, expired links, and fabricated paths. It cannot detect Referer-based hotlink protection, which is why guessed URLs on official sites stay out even when they return 200.

*Right picture?* (every image, generated ones included.) A 200 only proves that **something** is there, and search engines routinely return an image adjacent to the query rather than the thing itself, so **you must look at it before you use it**: save each surviving image to a temp path and `Read` it (a `small` or `medium` thumbnail is plenty — you are judging subject matter, not print quality). Cut the image, and its slot, when the subject is not what the surrounding text claims; when it is a collage, a chart screenshot, or a wall of text rather than a photograph; when a stock watermark or agency overlay covers it; when it is too small or blurry for the size your layout gives it; or when it looks AI-generated in a context that implies a real photograph (news, documentary, product shots). Generated images get the same scrutiny — check for mangled text, malformed hands and faces, and a style that clashes with the rest of the page. Do not rewrite the caption to fit a mismatched picture, and do not go looking for a replacement — just cut it.

Captions must not assert more than the image supports. If you cannot confirm the specific person, building, or event pictured, write a general caption rather than a confident false one, and never invent a photographer or agency credit.

**Step D — inline the bytes. This is what makes the downloadable case different.** A signed search URL expires, often within hours, and this file gets opened next week, possibly from `file://`, long after the signature died. A remote `<img src>` that works during your self-check will be broken by the time it matters. So encode the images you kept as `data:` URIs. Keep the base64 inside the script — it must never pass through your own output, or the payload re-enters your context on every later turn.

```python
import base64, io, os, requests
from PIL import Image

def fetch(url, path, max_w=1200, quality=82):      # Step C: download + normalise, then Read(path)
    r = requests.get(url, timeout=10); r.raise_for_status()
    im = Image.open(io.BytesIO(r.content)).convert("RGB")
    if im.width > max_w: im = im.resize((max_w, round(im.height * max_w / im.width)))
    im.save(path, "JPEG", quality=quality, optimize=True)
    return path, os.path.getsize(path) // 1024     # print sizes only, never the payload

def to_data_uri(path):                             # Step D: only for images you looked at and kept
    return "data:image/jpeg;base64," + base64.b64encode(open(path, "rb").read()).decode()

doc = open(out, encoding="utf-8").read()           # the file you wrote with `Write`, carrying __IMG1__
doc = doc.replace("__IMG1__", to_data_uri("/tmp/img1.jpg"))
open(out, "w", encoding="utf-8").write(doc)
```

Budget roughly six images, each under ~400 KB after downscaling, total file under ~5 MB. Without Pillow, embed the original bytes with the correct MIME type and skip the resize. Note that `.convert("RGB")` flattens transparency to **black** — for a logo or cut-out with an alpha channel, skip the JPEG re-encode and inline the original PNG bytes as `image/png`. One attempt per image: if any step fails, drop it and move on rather than re-searching, since repeated image searches burn context and usually fail for the same reason. This is deliberately the opposite of the CDN-library rule above — libraries are large, stable, and permanently addressable so they stay remote; images are small and served from expiring signed URLs, so they come with you.

Every `<img>` still gets `alt` text and `onerror="this.style.display='none'"` as a last line of defence (plus `loading="lazy"` on any image that has to stay remote because it will not fit the inline budget). If most slots end up empty, redesign the section around typography, color, SVG, and charts rather than leaving holes.

**Icons — use a real icon system, never emoji.** Pick ONE system per artifact (never mix), by icon count:

1. **Icon-heavy artifacts (≥ ~8 icons): Lucide via jsDelivr** (ISC, a large visually consistent stroke set — successor to Feather): `<script src="https://cdn.jsdelivr.net/npm/lucide@1/dist/umd/lucide.min.js"></script>` (pin the major, as with the chart libraries — `@latest` can shift under you), mark slots with `<i data-lucide="trending-up"></i>`, call `lucide.createIcons()` after load (same CDN retry guard as charts). Renders as inline SVG with `stroke="currentColor"` — theme via the wrapper's `color:var(--accent)`/`var(--muted)`.
2. **Alternative when you need filled+line variants or very broad coverage: Remix Icon webfont** (Apache-2.0, 1539 icons in matching line/fill pairs, the closest open-source counterpart to iconfont.cn's style): `<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/remixicon@4/fonts/remixicon.css">`, then `<i class="ri-bar-chart-2-line" style="color:var(--accent)"></i>` — zero JS.
3. **A handful of icons: hand-written inline SVG**, simple 24×24 stroke-based (`fill="none" stroke="currentColor" stroke-width="2"`), depicting the topic. Keep size and stroke-width uniform throughout, and always color via `currentColor` so the palette applies — `fill="none"` is not optional, since SVG shapes default to `fill:black` and an outline icon without it becomes a solid blob.

**Hand-written SVG — the traps worth knowing.** Cheap to avoid, and hard to spot once the file is written:
- **IDs are document-global, not scoped per `<svg>`.** Two gauges that each define `<linearGradient id="grad">` will both resolve `url(#grad)` to whichever parsed first, so the second silently renders with the wrong fill. Suffix every `linearGradient` / `clipPath` / `mask` / `filter` / `marker` id — `id="grad-revenue"`. Long single-page artifacts built from a repeated template hit this constantly.
- **Rotating a shape about its own center needs `transform-box:fill-box; transform-origin:center`.** Otherwise CSS `transform-origin` resolves against the viewBox and the shape orbits the canvas corner instead of spinning in place.
- **Strokes scale with the viewBox** — a 24×24 icon rendered at 96px turns `stroke-width:2` into a visually fat 8px line. Scale the width down proportionally, or add `vector-effect="non-scaling-stroke"`.
- **`<text>` never wraps.** A long string runs straight out of the viewBox and is clipped: break lines yourself with `<tspan x="0" dy="1.2em">`, and place them with `text-anchor` plus `dominant-baseline="middle"`.
- Decorative SVG takes `aria-hidden="true"`; an icon carrying meaning on its own needs `role="img"` with a `<title>` child, or an `aria-label` on the button wrapping it.

**Emoji — TOTAL BAN** in your own UI text, labels, headings, buttons, particles, and body text. Use plain text or inline SVG instead. The only exceptions: the user explicitly asks to display specific emoji, or emoji that are part of verbatim user/source data being quoted.

### Visual Hierarchy (esp. Game / Canvas-first / App)

- **Buttons by weight**: Primary `background:var(--accent-soft);color:var(--text);border:1px solid var(--accent)` — one per view; a solid `var(--accent)` fill works too if you bold the label and set it ≥18px, per the accent-contrast rule in the Color Rotation System. Secondary `background:var(--card);border:1px solid var(--border)`; Ghost `background:transparent;color:var(--muted)`.
- **Card elevation**: Surface (border, no shadow) · Raised (border + `box-shadow:0 1px 3px rgba(0,0,0,.06)`) · Focal (accent border + glow). On dark palettes use a lighter card bg instead of black shadows.
- **Spacing rhythm**: large gaps between major sections (`margin-bottom:3rem`–`3.5rem`), tight within cards (`gap:1rem`); never uniform spacing everywhere.

### Design Polish Techniques (use 3–5 per artifact)

Radial-gradient background bleed (dark palettes); faint grid texture; gradient text in hero; custom CSS progress bars; status pills; tabular-nums for aligned numbers; eyebrow labels; card hover lift (`transform:translateY(-3px)`); per-item accent colors for 3–4 compared items; accent top-bar on key cards (light palettes). With a real `<style>` block you may use `color-mix()` and modern CSS freely.

### Chart & Visualization Rules

**Real charts MUST come from an interactive library on jsDelivr** — ECharts (`echarts@5`), Chart.js (`chart.js@4`), D3 (`d3@7`), Plotly (`plotly.js@2`). **FORBIDDEN**: matplotlib base64 PNGs, or any static rendered-image chart. For small bespoke visuals that are not really charts — a gauge, a progress row, a hand-built diagram — pure SVG/Canvas/vanilla JS beats pulling in a library.

Copy these tags exactly. jsDelivr auto-minifies any file on request, so **a 200 does not mean the build is usable**: `chart.js@4/dist/chart.min.js` returns 200 but is the ESM bundle and dies with "Cannot use import statement outside a module" in a classic `<script>`, leaving `Chart` undefined and the canvas blank.

```html
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.js"></script>    <!-- .umd.js — NOT chart.min.js -->
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/plotly.js@2/dist/plotly.min.js"></script>  <!-- 4.4 MB: prefer ECharts unless you need Plotly -->
```

> **NEVER base64-inline or vendor a chart/CDN library into the HTML.** Always load it with a `<script src="https://cdn.jsdelivr.net/...">` tag — do **NOT** embed `echarts.min.js` (or any large library) as a `data:` URI, and do **NOT** paste its minified source into the file. The artifact is expected to have internet access when opened, so the CDN tag is correct. Inlining a ~1 MB library is **forbidden**: it bloats the file *and* the agent's own conversation context (the megabyte of base64 re-enters every subsequent model turn), causing massive slowdowns and extra iterations. Keep the `.html` small — only your own code + data go inline; libraries stay on the CDN.
- **Theme to the palette** (hardcode the injected hex): series 1 is `--accent`, series 2 is `--accent2`, then `--muted` (max 4–5; never the library default rainbow); tooltip `backgroundColor`=`--card`, `borderColor`=`--border`, text=`--text`; hide axis ticks; axis/split lines at `--border`; labels in `--muted`.
- **Line/trend/time-series**: set `yAxis:{scale:true}` so data far from zero is visible; bar charts comparing magnitudes should include 0.
- **ECharts containers need an explicit height** (`style="height:380px"`) or they render 0px invisible.
- Keep `setOption` literals shallow: extract gradients into a `var`; put value labels at series level (`series:[{...,label:{show:true}}]`), never inside `itemStyle`/`areaStyle`. A missed brace is a fatal parse error, so keep nesting flat.

### Diagram Geometry Rules (node-link diagrams: trees, org charts, flowcharts, graphs)

Misaligned diagrams come from coordinates typed by hand in two places. Rules:
1. **Match algorithm to structure**: trees/org charts/flowcharts are LAYERED — lay out in rows with orthogonal (elbow) connectors. For trees prefer ECharts `series:[{type:'tree'}]` (zero coordinate math). **NEVER use force layout (`forceSimulation`, ECharts `layout:'force'`) on a tree/org chart** — it collapses the hierarchy into a blob.
2. **If hand-placing: ONE `<svg viewBox>`, ONE data table, render loops.** Define each node's position once in a JS object (by formula, not eyeballed); render BOTH nodes and edges from that table. An edge is `pos[from]→pos[to]` — never literal numbers typed twice.
3. Layered formula: `y = topMargin + level*rowGap`; within a row `x = (i+1)*width/(count+1)`. No sibling-sibling edges.
4. Orthogonal connectors: `M parentX parentBottom V railY H childX V childTop`.
5. ONE unit system (SVG user units) — never mix `%` and `px` for elements that must align. Reserve `transform` for motion; position with attributes/`left`/`top`.
6. Append edges BEFORE nodes so node fills cover line ends.

```html
<svg id="tree" viewBox="0 0 1000 620" style="width:100%;height:auto"></svg>
<script>
(function(){
  var svg=document.getElementById('tree'); if(!svg)return;
  var C={muted:'#64748b',card:'#ffffff',accent:'#2d7eb5'};  // REPLACE with your category's hex
  var NS='http://www.w3.org/2000/svg', W=1000, TOP=80, ROW=180, R=34;
  var levels=[['A','B'],['C','D','E']];          // node ids per layer
  var edges=[['A','C'],['B','C']];
  var pos={};
  levels.forEach(function(row,li){row.forEach(function(id,i){pos[id]={x:(i+1)*W/(row.length+1),y:TOP+li*ROW};});});
  edges.forEach(function(e){var a=pos[e[0]],b=pos[e[1]]; if(!a||!b)return;
    var railY=(a.y+b.y)/2;
    var p=document.createElementNS(NS,'path');
    p.setAttribute('d','M '+a.x+' '+(a.y+R)+' V '+railY+' H '+b.x+' V '+(b.y-R));
    p.setAttribute('fill','none');p.setAttribute('stroke',C.muted);p.setAttribute('stroke-width',2);
    svg.appendChild(p);});                         // edges first, nodes cover residue
  Object.keys(pos).forEach(function(id){var n=pos[id];
    var c=document.createElementNS(NS,'circle');
    c.setAttribute('cx',n.x);c.setAttribute('cy',n.y);c.setAttribute('r',R);
    c.setAttribute('fill',C.card);c.setAttribute('stroke',C.accent);c.setAttribute('stroke-width',2);
    svg.appendChild(c);});
})();
</script>
```

Never leave a literal placeholder like `ACCENT_HEX` in a color attribute — an invalid presentation-attribute value is discarded, so `stroke` falls back to `none` and your connectors render **invisible**.

### Robustness & Bug Prevention

1. **Self-contained data**: embed values as JS variables; no runtime API calls. If the request implies a live data source — a Google Maps embed, a real-time price feed, a rotating globe fed by an API — that dependency will fail for the user (missing key, CORS, dead endpoint). Say so, and offer the feasible version instead: a static SVG map, an ECharts map with the GeoJSON embedded, or a snapshot of the data with its timestamp shown.
2. **Text–chart consistency**: values, units, and legends must match your accompanying text.
3. **CDN guards**: if an inline script uses a CDN library, guard with a short retry (`setTimeout`) before showing a fallback, in case the library script is still loading.
4. **XSS / escaping**: insert user- or file-derived strings via `textContent`/`createElement`, never raw into `innerHTML` or inline event attributes.
5. **Mobile-friendly**: multi-column layouts use `flex-wrap`, `grid-template-columns:repeat(auto-fit,minmax(280px,1fr))`, or an explicit `@media (min-width:1024px)` breakpoint; no rigid fixed columns. There is no Tailwind here, so utility class names like `lg:grid-cols-2` would style nothing — write real CSS.

### Interactive JS Safety Rules (MANDATORY for any animated / stateful artifact)

Mechanism-level rules for any artifact containing animation, transitions, scroll effects, flips, countdowns, progress bars, particles, drag, or game logic. These govern HOW animation is driven, HOW timing avoids races, HOW layout stays intact, and HOW state is managed — copy these safe patterns; do NOT invent your own driving mechanism.

**A. Structure, animation driving & timing**

- **A0. No top-level declarations — wrap each script body in an IIFE (or use `<script type="module">`).** Two top-level `const`/`let` with the same name (your early registry object vs. a later temp variable) kill the page at **parse time**: zero JS runs, only the static skeleton renders. This is the single most frequent fatal bug in long single-file apps — the longer and more "organized" the code (registries, constant tables), the likelier the collision. IIFEs shrink the collision surface, and splitting independent concerns into separate IIFE-wrapped `<script>` tags firewalls a parse error into one of them instead of the whole page. The Step-0 syntax smoke (below) exposes it in seconds.
- **A1. Drive every animation by duration interpolation, never per-frame velocity decay.** Every animation must have a definite end: `p = Math.min(1, (now - start) / duration)`; `p >= 1` structurally guarantees the done-callback fires. BANNED: "add/subtract velocity each frame, stop when below a threshold" — values land in the threshold dead-zone and lock up forever.

  ```js
  let rafId = null;                         // lives inside the IIFE, not at top level (A0)
  function animate({duration, ease = t => t, onFrame, onDone}) {
    cancelAnimationFrame(rafId);            // A2: one animation loop at a time
    const start = performance.now();
    function frame(now) {
      const p = Math.min(1, (now - start) / duration);
      onFrame(ease(p), p);
      if (p < 1) rafId = requestAnimationFrame(frame);
      else onDone && onDone();
    }
    rafId = requestAnimationFrame(frame);
  }
  const easeOutCubic = t => 1 - Math.pow(1 - t, 3);
  ```

  Standard decomposition for "random result + animated stop" interactions (spinners, wheels, card reveals): **① pure logic picks the result → ② compute the target position it maps to → ③ `animate()` interpolates there (the animation is only theater) → ④ commit in `onDone` (see C2)**. A constant-speed infinite phase may use a bare rAF loop, but `cancelAnimationFrame` before entering the next phase.
- **A2. One property, one driver.** A CSS property is driven EITHER by CSS transition/animation OR by per-frame JS writes — never both (JS writing a transitioned property animates the browser's queue: jumps, lag, compounding). Declare `transition: none` on JS-driven elements.
- **A3. Never hang flow on a bare `transitionend`/`animationend`.** These may never fire (element `display:none`, animation interrupted, tab backgrounded) and the flow deadlocks. Use A1's `onDone`, or pair the listener with a `setTimeout(duration + 100)` fallback — first to fire wins.
- **A4. Countdowns/elapsed time = wall-clock difference, never tick counting.** `remaining = total - (Date.now() - startTs)`. rAF pauses and `setInterval` throttles in background tabs, so "subtract one per second" drifts; wall-clock self-corrects on return. Test end with `<= 0`, not `=== 0`.
- **A5. Register every timer/rAF handle centrally; clear ALL on any restart.** Keep `setTimeout`/`setInterval`/rAF handles in one array/object; every "new round / mode switch / reset" iterates and clears first. A leftover timer from the previous round firing into the new one is the hardest-to-debug bug class in these pages.

**B. Layout & rendering for interactive surfaces**

- **B1. Content-bearing elements must be sized by content or explicit dimensions — absolute positioning is not a skeleton.** `position:absolute` children contribute nothing to the parent's size; an `auto`/`1fr` track whose children are all absolute is 0 wide and `overflow:hidden` erases it. Verify key visible elements' `getBoundingClientRect()` exceeds a sane floor.
- **B2. Stacked-plane structures (card front/back, layered carousels) — three requirements**: the container gets an **explicit size** (both faces absolute → container collapses to 0); 3D flips need `backface-visibility: hidden` on BOTH faces + `perspective` on the wrapper (else both faces show through); only one face is interactive at a time (`pointer-events` follows state).
- **B3. `filter`/`backdrop-filter` only on pure-decoration elements.** Filters hit the entire subtree — on a container, all text/icons blur and shift color. Glows live on a separate empty element or pseudo-element (`position:absolute; pointer-events:none`, z-index below content). Pulse/breathe effects animate `opacity`/`box-shadow`/`transform:scale`, never `filter:hue-rotate` (it rotates colors away from your palette).
- **B4. Declare stacking explicitly.** `transform`/`filter`/`opacity<1` each create a stacking context that voids child z-index. Plan explicit tiers (e.g. content 1 / particles 30 / overlay 40) and verify occlusion in the rendered preview — never assume.
- **B5. Dynamic text needs a declared overflow strategy** — `ellipsis`, font-shrink, or wrap: pick one explicitly and test with the longest real value in the data.

**C. State & data**

- **C1. Buttons run on a single state machine.** One `state` variable (`idle | running | done`, extend as needed); all button `disabled`/labels computed in ONE `syncUI()` from state; every handler opens with a guard (`if (state !== 'idle') return`). Scattered `btn.disabled = ...` writes breed re-entry bugs: double-click mid-animation, double loops, data consumed twice. Comparison/settlement intermediate states also lock input.
- **C2. Consumable state commits ONLY in the completion callback.** Draws, deductions, scoring, match judgments commit in `onDone` — decide the result first (read), commit after the show (write). Mutating before the animation starts means an interrupted show silently burns data with no recovery.
- **C3. Reset = factory reset, not display clearing.** "Restart / change difficulty / next round" must clear: the state variable, ALL timers and rAF (A5), particle arrays, animation classes, dynamically generated DOM. Walk this list item-by-item when writing reset — each miss is a ghost from the previous round.
- **C4. Every number in the request is enforced programmatically.** Generate N items by loop or `console.assert(arr.length === N)`; paired/grouped requirements also assert structure after shuffling (still exactly N pairs). No hand-written long lists verified by eyeballing; displayed counts reference the same constant — never a second hardcoded copy.

**D. Canvas particles**

- **D1. Fixed skeleton**: canvas `position:fixed; inset:0; pointer-events:none`, explicit z-index (B4); every particle carries a life (`life -= dec`, filtered out of the array at 0); `clearRect` each frame; `resize` listener re-sets width/height. Unrecycled particles accumulate until the page freezes.

**Verification ladder (cost-ordered — cheapest checks earliest and most often).** This does NOT change the render-ONCE rule: `artifact-preview` still runs exactly once; the cheap steps below never touch a browser.

1. **Step-0 syntax smoke (seconds; run right after the skeleton and after every large edit)**: extract each `<script>` body to a temp `.js` and run `node --check` in the sandbox; if `node` is not available, fall back to `verifier file validate` on the HTML. One `SyntaxError` = that whole script tag dead before executing (A0) — this catches it instantly and can be repeated freely, unlike a preview render.
2. **Static self-review against the rules**: every rAF loop exits via `p >= 1` (not a numeric threshold); every property has one driver; every `transitionend` has a timeout fallback; every timer is cleared in reset; every absolutely-positioned element can answer "what sizes my parent"; consumables commit only in `onDone`; every requested number has an assert.
3. **The single `artifact-preview` render** (existing rule, unchanged): on the screenshot verify initial-state visibility, key element sizes, and occlusion order (B1/B4).
4. Interaction paths (rapid double-clicks, mid-animation clicks, reset-then-replay) cannot be exercised in this sandbox — compensate structurally: the C1 state guards and C2 onDone-commits make re-entry harmless by construction, and load-time `console.assert` self-checks (C4) surface count violations.

### Math Formulas

MathJax via CDN; configure BEFORE the library and use `\(...\)` for inline and `$$...$$` for display (do NOT enable single-`$` inline math — it collides with currency). **The body must use the same delimiters as the config** — a config registering `\(...\)` with `$...$` in the body renders raw LaTeX, and is the #1 MathJax failure. With the `Write` tool backslashes pass through verbatim; **only** if you generate the file through Python must the document live in a **raw string** so `\frac`/`\theta` survive `\t`/`\f`/`\r` corruption (see the file-writing section).

### Quality Checklist

- [ ] Saved a self-contained `.html` into the agent workspace, **self-checked** with `artifact-preview` (+`Read` screenshot) and `verifier-hub`, and delivered via **`NotifyHuman`**?
- [ ] Complete standalone document (`<!DOCTYPE html>`, `<head>`, `<body>`)?
- [ ] Archetype chosen by **genre** (auto-inferred when the user named no style); metric-card rows only in Dashboard?
- [ ] Font + colors from the **Rotation Systems** (none banned); all borders via `var(--border)`?
- [ ] **Zero emoji** in the UI; icons all from ONE system (Lucide / Remix Icon / hand-written SVG), topic-specific and themed via `currentColor`; hand-written SVG has `fill="none"` on stroke shapes and unique gradient/clip ids; every `<img>` came from a user-supplied URL, a search `<uri>`, or image generation for a decorative slot — **was actually looked at**, matches its caption, and was inlined as a `data:` URI (no fabricated URLs, no placeholder boxes, no generated stand-ins for real people/places/events)?
- [ ] Charts themed to the palette (no default rainbow), ECharts divs have explicit height, line charts use `yAxis:{scale:true}`?
- [ ] Diagrams: ONE viewBox + ONE data table + render loops; layered rows + orthogonal elbows; no force layout?
- [ ] All numbers from sandbox compute / search / user input (no guesses); values consistent across charts/text; untrusted strings escaped?
- [ ] If (and only if) the file was generated through Python: written from a raw string so LaTeX/CSS backslashes stayed intact?
- [ ] Interactive/animated artifacts: no top-level declarations, every script body in an IIFE/module (A0) and `node --check` smoke passed after every large edit; animations duration-interpolated with `onDone` (A1); one driver per property (A2); wall-clock countdowns (A4); single state machine + handler guards (C1); consumables commit only in `onDone` (C2); reset clears state/timers/rAF/particles/DOM (A5/C3); every requested number asserted (C4)?
- [ ] Games: start screen blocks the game world on load, HUD hidden until Start; state machine is `start | playing | paused | ended`; gameplay begins only via explicit Start action; end/session summary screen offers Play Again; no emoji on game screens?
