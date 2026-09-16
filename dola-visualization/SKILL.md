---
name: dola-visualization
description: >-
  THE DEFAULT path for HTML visual artifacts: the page streams into the reply inside a
  `type="renderer"` html code fence and renders live in the conversation, with no file
  written to disk. Handles trigger recognition (when to visualize vs answer in plain
  text), style auto-inference, layout archetype selection, color/font rotation, chart
  rules (ECharts, D3, Chart.js), SVG diagram geometry, renderer hard constraints, and
  mobile responsiveness. Use for HTML pages, dashboards, data reports, comparison tables,
  infographics, interactive diagrams, games, calculators, timelines, mind maps, or any
  styled visual artifact — including proactive visualization decisions — whenever the
  visual is meant to be seen in the chat. Use it ONLY for that streaming path: if the
  user explicitly asks for a downloadable, standalone, exportable or saveable .html file,
  or wants something to open, host, print, or share outside the chat, the skill
  `downloadable-html-visualization` owns that request instead.
---

## Web Design & Visualization Handbook — Streaming Edition v2

> **#1 RULE — burn this into memory: your code fence MUST be ` ```html type="renderer" `. Writing ` ```html ` without `type="renderer"` makes the ENTIRE output useless (user sees raw code, not a rendered page). This is the single most frequent fatal error.**

You can generate self-contained HTML artifacts using the code interpreter for computation and your response text for the HTML itself. This handbook produces **distinctive, high-quality HTML that streams progressively to the user** — each section appears as you generate it, creating a smooth, delightful experience. Enrich with real imagery via verified URLs or `general_search`, and SVG icons for visual polish.

**Severity tiers** — how to read the labels used throughout this handbook:

| Label | Meaning | Consequence of violation |
|-------|---------|--------------------------|
| **CRITICAL** | Violating these produces blank, broken, or fundamentally unusable output | Task fails — user sees nothing useful or the page is non-functional |
| **MANDATORY** | Violating these produces generic, ugly, or off-brand output | Page works but looks amateur or indistinguishable from a template |
| **IMPORTANT** | Violating these produces misleading, inconsistent, or fabricated content | Page looks fine but information is wrong or deceptive |

When time-pressed or hitting token limits, prioritize in this order: CRITICAL > IMPORTANT > MANDATORY (yes — content accuracy outranks visual polish; a correct plain page beats a gorgeous page with wrong data). Never skip CRITICAL rules.

### When This Handbook Applies (Trigger Recognition)

This handbook activates for ANY request that asks for a visual HTML deliverable. All of the following phrasings are EQUIVALENT and must produce the SAME quality of styled, designed output:

| User phrasing pattern | Applies? | Notes |
|---|---|---|
| "make an html report" / "generate html" / "output as html" | YES | "html" = styled visual artifact, NOT raw source code |
| "make a webpage" / "create a page" | YES | Identical to above |
| "visualize" / "infographic" / "make a chart" | YES | |
| "make it look nice" / "create a pretty report" | YES | |
| "dashboard" / "data report" / "comparison table" | YES | |

**CRITICAL**: The word "html" in a user request means "render a styled, designed visual artifact" — it does NOT mean "output raw HTML code for me to inspect." Treat a bare "make an html report" identically to "make a beautifully designed visual report." Always apply the full design system (archetype, font rotation, color rotation, design polish) regardless of whether the user explicitly asks for beauty. The user's choice of wording ("html" vs "webpage" vs "visualize") must NEVER affect output quality.

**Proactive visualization (MANDATORY when signals match)**: When ANY signal in the table below matches, you MUST generate an HTML visualization unless a "Do NOT generate HTML" exclusion also applies (resolve via the Tiebreaker rule). Responding with text-only when a signal matches is a task degradation, equivalent to producing a generic unstyled page when the user explicitly asked for HTML. You do NOT need the user to say "html," "webpage," or "visualize" — the signal match alone is sufficient mandate. Think of it as opt-out, not opt-in: when signals match, you need a reason NOT to visualize, not a reason TO visualize.

**When to proactively visualize** — if ANY of these signals are present, default to generating HTML:

| Signal | Why HTML wins over text |
|--------|------------------------|
| Comparison (≥3 items with multiple attributes) | Spatial layout lets users scan and contrast instantly |
| Data with numbers, rankings, or trends | Charts/tables convey magnitude and pattern at a glance |
| Process / workflow / sequence of steps | Flowcharts and timelines show order + branching |
| Hierarchical or nested structure | Tree/org-chart/mind-map clarifies depth vs. breadth |
| Before/after or pros/cons | Side-by-side layout is inherently clearer |
| Geographic or spatial content | Maps and spatial diagrams beat verbal directions |
| Technical architecture or system design | Node-link diagrams > paragraphs of "A connects to B" |
| "Explain how X works" (complex system) | Animated/interactive diagrams aid understanding |
| Multiple categories/dimensions to organize | Card grids or tabbed layouts prevent info overload |
| User provided data/file and asks for insight | Visualization of the finding IS the answer |

**How to combine**: Provide a brief text explanation (1-3 sentences framing the answer) PLUS the ` ```html type="renderer" ` block. The HTML is NOT a supplement — it IS the primary answer; the text is the introduction. A proactive visualization that matches multiple signals should be treated with the SAME quality standard as an explicit user request for HTML.

**Examples of good proactive use**:
- User: "explain how transformers work" → 2-sentence intro + animated architecture diagram with attention flow
- User: "compare iPhone 16, Pixel 9, and Galaxy S25" → one-line lead-in + styled comparison dashboard
- User: "how does TCP handshake work" → short explanation + animated 3-way handshake sequence diagram

**Do NOT proactively visualize these (borderline over-triggers the model often gets wrong):**
- "What are the differences between Python and JavaScript?" → a few prose paragraphs suffice; no spatial/relational structure → text
- "List the steps to deploy to AWS" → sequential steps, no branching or hierarchy → text
- "What are the pros and cons of remote work?" → simple two-column answer, not enough dimensions for layout to add value → text

**Do NOT over-trigger**: The "Do NOT generate HTML" table below still applies. Short factual answers, pure prose, translation, etc. remain text-only. The bar is: "would a visual layout make this answer meaningfully easier to understand or compare?" If yes → visualize.

**Tiebreaker**: If a request matches BOTH a proactive visualization signal AND a "Do NOT generate HTML" exclusion, ask: "Does the content have spatial, relational, or quantitative structure that a 2D layout makes easier to parse than linear prose?" If yes → visualize. If no → text. Example: "5 types of ML" → flat list, no relational structure → text. "How the 5 types of ML relate to each other" → hierarchy/overlap → visualize.

**Do NOT generate HTML** for these request types — respond with text, appropriate tools, or the requested format instead:

| Pattern | Why not HTML | Correct response |
|---------|-------------|-----------------|
| Pure prose deliverables (essays, letters, speeches, novels, scripts, creative writing) | The user wants authored text, not a visual artifact | Plain text in your response |
| Simple factual Q&A with short answers (medical, legal, cooking, pet care, definitions) | A one-paragraph answer does not benefit from spatial layout | Plain text answer |
| Translation requests | The deliverable is translated text | Plain text |
| Requests for a specific non-HTML format ("create a PPT", "make a presentation", "deliver as PDF", "Word document") | User explicitly wants a different format | Produce that format instead of HTML: use the tooling that owns it (`.pptx` / `.pdf` / `.docx`) and deliver the file via `NotifyHuman` |
| Image / video generation requests ("create an avatar", "make a cover image", "cinematic concept") | The deliverable is the picture itself, not a page around it | Use `image_gen` / `image_edit` (or the video tool) directly |
| Roleplay / character conversation ("pretend to be...", "from now on you are...") | The user wants conversational interaction | Respond in character as text |
| Technical how-to with no visual component ("how to convert A3 to A4 in Word", "write code using X framework") | The answer is procedural text or code | Plain text / code block |
| Visualizations requiring external APIs that will fail in the sandbox (Google Maps API, WebGIS, real-time data feeds, rotating globe with live data) | These WILL break — the sandbox blocks third-party API calls | Explain the limitation; offer a feasible alternative (static SVG map, ECharts map with embedded GeoJSON) or provide code the user can run locally |
| Requests for jokes, quotes, names, brainstorming lists | Short creative text does not benefit from layout | Plain text |

### Decision Recipe (follow this sequence for EVERY visualization request — INCLUDING proactive ones)

**CRITICAL: Every HTML code fence MUST be ` ```html type="renderer" `. Without `type="renderer"`, the user sees raw code, not a rendered page — total task failure.**

0. **Should I visualize?** → Even if the user didn't ask for HTML, check the *Proactive visualization* signal table above. If any signal matches, you MUST proceed with this recipe (it is mandatory, not optional). If none match AND user didn't request HTML, respond with text only.
1. **Auto-infer style** → If user didn't specify a style, infer archetype + category from content (see *Style Auto-Inference* in [design-system.md](references/design-system.md))
2. **Pick archetype** → Determines page structure (see *Layout Archetype System* in [design-system.md](references/design-system.md))
3. **Pick form of expression** → Refines the dominant content element within the archetype (see *Form-of-Expression* table in [design-system.md](references/design-system.md))
4. **Pick category** → Determines color palette + font (see *Color/Font Rotation Systems* in [design-system.md](references/design-system.md))
5. **Decide block count** → The default is ONE block. Interactive (ANY JS filtering/sorting/dynamic rendering/state) = ALWAYS one block. Non-interactive = one block unless genuinely massive.
6. **Run CI for data** → Compute all numbers first; print results (see *Phase 1*)
7. **Verify the 4 conditions below** → If any fails, adjust your plan before proceeding
8. **Generate HTML** → Output ` ```html type="renderer" ` block(s) in your response — **ZERO emoji** in the entire output (see ban below)

### Absolute Ban: Zero Emoji in HTML Output

**Do NOT use emoji anywhere in your HTML output.** The rule is simple: if a character has emoji presentation (renders as a colorful pictogram with its own inherent color, rather than a plain monochrome glyph that takes CSS `color`), it is banned. This includes all characters with the Unicode `Emoji_Presentation` property and any character followed by the emoji variation selector (U+FE0F).

Commonly violated examples (all banned):
- Checkmark/cross-mark emoji (the filled colored boxes — plain `+`, `-`, `●` styled with CSS are fine)
- Fire, trophy, rocket, sparkles emoji
- Colored-circle emoji (the inherently colored kind — `●` styled with CSS `color` is fine)
- Pointing hands, lightbulbs, warning-triangle emoji
- Device/chart/globe/star pictograph emoji (plain ASCII `*` and CSS-styled `★` are fine)

The distinction: a plain monochrome glyph (`●`, `▲`, `★`, `■`, `+`, `−`) styled with CSS `color` property = ALLOWED. An emoji character that has inherent color regardless of what CSS you apply = BANNED. Example: `<span style="color:#059669">●</span>` is fine because `●` is a plain glyph taking CSS color; a green-circle emoji is banned because its color is built into the character itself.

Common violations and their fixes:

| Violation pattern | Fix |
|---|---|
| Emoji checkmark/cross in pros/cons lists (e.g. `❌` U+274C, `✅` U+2705) | Use plain text glyphs (`✓` U+2713, `✗` U+2717, `+`, `−`) styled with CSS color: `<span style="color:#059669;font-weight:600">✓</span>` / `<span style="color:#dc2626;font-weight:600">✗</span>`, or use text headers **Strengths** / **Weaknesses** |
| Colored-circle emoji as brand markers | Define per-item CSS classes with distinct colors (see Design Polish #9), then use a plain dot: `<span class="item-a" style="color:var(--item-accent)">●</span>` |
| Pointing-hand emoji as heading decorator | Plain heading text — the styling system provides visual interest |
| Lightbulb/warning emoji in callouts | Styled callout box with `border-left` or `background:var(--accent-soft)` |
| Emoji checkmark in table cells as "yes" indicator | Text "Yes" / symbol with color, or a colored pill `<span>` |

**Pros/cons lists — the correct pattern:**
```html
<!-- CORRECT: styled text with color indicators (never emoji markers) -->
<div class="text-sm space-y-1">
  <p><span style="color:#059669;font-weight:600">+</span> Fast response</p>
  <p><span style="color:#059669;font-weight:600">+</span> Good quality</p>
  <p><span style="color:#dc2626;font-weight:600">−</span> Expensive</p>
  <p><span style="color:#dc2626;font-weight:600">−</span> Limited</p>
</div>
```

The ONLY exceptions: (a) verbatim user-supplied data being displayed (quoted tweets, file contents); (b) user explicitly asked to display specific emoji characters. See *Icon & Visual Enrichment Strategy* (in [design-system.md](references/design-system.md)) for the full rule and alternatives.

---

### Pre-Generation Gate (step 7 above — verify before writing HTML)

Before writing your first ` ```html type="renderer" ` fence, verify these four conditions hold for your plan. If any condition fails, adjust your plan (cut scope, switch format, fetch data) before proceeding to step 8.

1. **COMPLEXITY** — How many JS event handlers / state transitions does this need?
   - ≤3 → safe, proceed normally
   - 4–8 → moderate risk: ensure each handler is simple and independent; budget ~60 lines per feature
   - \>8 → FAILS: cut scope to the 4–5 most critical interactions. Note the rest as "could be added in a follow-up."

2. **FORMAT** — Did the user name a specific deliverable form (game, mind map, timeline, calculator, interactive diagram)?
   - If YES → that form is a HARD constraint, equivalent in priority to the content itself. Text, bullet points, or static lists cannot substitute for the named form. If your current plan delivers a different format, it FAILS — restructure.

3. **DATA** — Does this need real-world numbers I cannot verify from memory alone?
   - If YES and you haven't fetched them yet → FAILS: go back to step 6 (CI/search). Never silently present invented numbers as factual.

4. **TESTABILITY** — Can I mentally trace the primary user action (click Start, submit form, select option) through my planned code and confirm it produces visible output?
   - If NO → FAILS: the feature is too complex to ship unverified. Simplify until you can trace it.

**Proactive escape hatch**: If the visualization was YOUR initiative (not the user's explicit request) and any Gate condition fails after reasonable scope reduction, abandon the HTML and deliver a text-only answer. This is correct judgment, not failure. If the user explicitly requested HTML, you may NOT abandon — simplify until it passes the Gate.

### Failure Pattern Categories

All output failures fall into one of these four patterns. When you detect the RISK of any pattern during generation, apply the corresponding countermeasure immediately — do not wait until the end.

| Pattern | Detection heuristic | Countermeasure |
|---------|-------------------|----------------|
| **Complexity Overreach** | You plan >8 JS event handlers / state transitions, or you cannot mentally trace the primary action through your JS | Cut to the features you CAN verify. Working with 4 features beats broken with 12. |
| **Format Drift** | The user named a specific visual/interactive form but your output is converging toward text, lists, or a different form | Stop and restructure. The named form is non-negotiable. |
| **Data Fabrication** | You are writing specific numbers (dates, statistics, measurements) that you neither computed in CI nor fetched via search | Replace with clearly-labeled placeholders, or fetch real data first. |
| **Platform Mismatch** | Your layout uses fixed widths >320px, blocks share state, or height grows unbounded | Apply mobile rules (overflow-x, viewBox, responsive sizing), keep interactive apps in ONE block, ban 100vh. |

---

### Precedence — Visualization vs File Output

For visualization requests covered by this Handbook, the deliverable is a ` ```html type="renderer" ` block **in your response text** — do **NOT** write that HTML to `/mnt/` via CI. The renderer block IS the deliverable; writing a file adds nothing and risks escape corruption.
- When the user explicitly asks for a downloadable file, in any language (e.g. "download", "save as file", "export", or their equivalents), **this Handbook stops applying**: that request belongs to `downloadable-html-visualization`, whose document structure, viewport-unit, script-placement, and image-embedding rules deliberately differ from the renderer rules here. Read that Skill in full before writing anything, and deliver the file through `NotifyHuman` rather than a `/mnt/` download link. Never preemptively offer a file download when a renderer block suffices.
- If you do write an HTML file in CI (rare exception), see **LaTeX escape hazard** in *Math Formulas* (in [quality-and-mobile.md](references/quality-and-mobile.md)) — Python string escaping destroys LaTeX. This is the #1 reason to output HTML directly in your response.
- **Static plots vs interactive visualizations**: Use the *Plotting & Showing Images* section in the CI Handbook for simple matplotlib/plotly image output. Use THIS handbook's renderer blocks for interactive, styled HTML visualizations (ECharts, D3, Canvas, etc.).

---

### HTML Output Procedure (CRITICAL — follow exactly)

**Phase 1: Compute data in the code interpreter (MANDATORY for data tasks)**

Use CI for all heavy computation (numpy, pandas, scipy, etc.). Print results so you can reference them when writing HTML.

- For small datasets (<20 values): print key numbers/results directly.
- For medium datasets (20-200 values): print as compact JSON via `json.dumps(data)`.
- Do NOT write any HTML files in CI. CI is for computation only (see the Precedence note above for the file-request exception; see **LaTeX escape hazard** in *Math Formulas* in [quality-and-mobile.md](references/quality-and-mobile.md)). Output HTML directly in your response instead.

**Phase 1 is NOT optional for data-driven visualizations.** If your artifact involves ANY of the following, you MUST use CI first:
- More than 5 data points that need calculation or transformation
- Date/time computations (durations, countdowns, time series)
- Statistical measures (averages, percentiles, trends, growth rates)
- Currency conversions or unit math
- Sorting, filtering, or aggregating datasets

Hardcoding guessed or fabricated numbers is **forbidden** — all data must be traceable to CI output or explicitly stated user input. The ONLY exception is the labeled-placeholder case defined in *Tool Loop Prevention* below.

**Image URLs also require CI verification** — if your artifact includes `<img>` tags, you MUST validate each URL in CI before outputting HTML (see *Step C* in *Icon & Visual Enrichment Strategy* in [design-system.md](references/design-system.md)). Never skip this step.

**Phase 2: Output HTML directly in your response**

After all tool calls are complete, output the HTML in your final response text wrapped in a ` ```html type="renderer" ` code block:

**Format**: Alternate between Markdown text and ` ```html type="renderer" ` code blocks. When the request matches the visualization whitelist, do NOT output only text, a Markdown table, an ASCII chart, or mere suggestions — you must provide a runnable renderer. Do NOT use `<head>`/`<body>`.

The outermost layer must **strictly** use the following wrapper structure. CDN `<script>` tags, the Google Fonts `<link>`, and the CSS-variable injection script sit inside `<html>` *before* the wrapper div, so the browser starts fetching them as the first tokens arrive — everything you actually render goes inside the div:

```html type="renderer"
<html style="margin:0;padding:0;">
<!-- font <link>, Tailwind + other CDN <script> tags, then the :root CSS-variable injection script -->
<div style="background-color:transparent;box-sizing:border-box;">
  <!-- Place the real UI container here -->
</div>
</html>
```

**Height rules** — see HC#5 below for the full ban. Summary: no `100vh`/`min-height:100vh`/`height:100%`/`min-h-screen` on layout containers. (`height:100%` is fine on a child of an explicitly-sized parent, e.g. a canvas div inside a `height:600px` wrapper.) Visualization containers (ECharts, Canvas, Three.js) REQUIRE explicit fixed px heights (300–450px typical). Put `box-sizing:border-box` on every layout container.

**Style — CSS mechanism table** (the single authoritative reference; other sections that mention CSS rules defer to this table):

| Mechanism | Status | Use for |
|-----------|--------|---------|
| Tailwind utility classes | Preferred | Layout, spacing, typography, responsive behavior |
| Inline `style="..."` | Allowed | CSS variable references, dynamic or one-off values |
| `<style>` injected via `document.createElement('style')` in a script | Allowed | `@keyframes`, `:hover`/pseudo-classes, `:root` CSS variable definitions |
| `<style>` tag written directly in markup | FORBIDDEN | In streaming mode, a bare `<style>` in markup is parsed incrementally — the browser applies partial rules mid-stream causing FOUC and specificity conflicts with styles injected later. JS injection (`createElement('style')`) executes atomically after DOM insertion, avoiding these race conditions. |

**Content**: `<script>` is allowed. The `<TEXT>` tag is forbidden — it is reserved by the renderer and breaks parsing.

**Layout**: Multi-column layouts must use flexible wrapping (`flex-wrap: wrap` or `auto-fit`); rigid fixed column counts that don't collapse on small screens are strictly forbidden. Responsive breakpoint columns (e.g. `grid-cols-1 lg:grid-cols-2`) are fine. Avoid unnecessarily deep nesting on mobile.

**Block count — the DEFAULT is ONE block.**

Almost every artifact should be a **single** ` ```html type="renderer" ` block. Splitting into multiple blocks is a LAST RESORT for genuinely massive non-interactive content — never a default, never "for organization," and never triggered by section boundaries.

**Why splitting is harmful:**
- Blocks are **isolated iframes** — they share NO DOM, NO CSS, NO JS state. A `var` defined in block 1 does not exist in block 2. `document.querySelectorAll` in block 1 cannot find elements in block 2.
- Each extra block wastes tokens on repeated CDN/CSS boilerplate, adds rendering delays, and creates visual seams.
- Splitting interactive content **breaks functionality** 100% of the time.

**Rule 1 — Interactive content: ALWAYS one block, no exceptions.**

If your page has ANY of these, it is interactive and MUST be a single block:
- Filter/sort buttons that show/hide or reorder elements
- JS that dynamically generates DOM elements (cards, list items, table rows) from a data array
- Tabs, accordions, or toggles that switch visible content
- Any `onclick`/`oninput`/`onchange` handler that modifies elements elsewhere on the page
- `<canvas>`, game logic, drawing tools, simulations, stateful UI
- Charts with linked tooltips or drill-down
- Forms where inputs affect other parts of the UI

**The common mistake**: a "gallery/catalog page" with filter chips at the top and JS-rendered cards below. The model sees "it's just a list of cards, not a game" and splits by section. But the filter operates on ALL cards via `querySelectorAll` — splitting puts half the cards in a separate iframe where the filter cannot reach them, silently breaking the feature.

**Rule 2 — Non-interactive content: default to one block; split only when genuinely necessary.**

Most reports, editorials, documents, and dashboards fit comfortably in a single block. Write the entire artifact as one block. Only consider splitting if the content is genuinely massive (e.g., a 10-chapter comprehensive report) AND you are confident the output will be very long. Even then:
- The split point must be between major logical sections (not mid-section)
- Each continuation block must be fully self-contained: own `<html>` wrapper, Tailwind CDN, CSS variable injection
- Never split because a section "feels complete" — that is not a reason

**The classic failures (NEVER do these):**
- Block 1 contains the UI (HTML structure, buttons, cards) and Block 2 contains the `<script>` (JS logic). Block 2 runs in its own isolated iframe where `document.getElementById('canvas')` returns `null` → everything is dead.
- A filtered catalog split at the section boundary — filter JS in block 1 cannot reach cards in block 2. Same principle: any cross-reference between blocks is impossible.

**The fix is always the same:** ONE block containing ALL HTML + ALL scripts together.

**Quick test**: does your JS contain any `document.querySelector`/`getElementById` that targets a DOM element in a DIFFERENT logical section? If yes — those sections must be in the same block. If every section's JS only touches its own internal DOM, splitting is technically safe (but still not recommended).

**Decide the block count BEFORE writing the first fence.** The answer is almost always ONE. Never decide to split mid-stream because the content "feels like it's getting long" or because a section "feels like a new block." If the block grows long, compress first (strip comments, reduce whitespace); only split genuinely enormous non-interactive content between major sections, keeping each sub-block self-contained.

Never copy meta-instructions or checkpoint comments from this handbook into your output HTML. The HTML comments in the skeleton template (see [skeleton-templates.md](references/skeleton-templates.md)), e.g. `<!-- MANDATORY: Replace font... -->`, `<!-- SECTION 1: Hero -->`, `<!-- CRITICAL: height... -->`) are notes for YOU to read — strip them from your output.

---
### Renderer Runtime & Hard Constraints (CRITICAL — these break the renderer)

Your HTML does **not** run as a standalone page. The renderer injects your markup into the document of a **sandboxed, height-adaptive iframe** after the host page has loaded, then re-creates and executes each `<script>` in document order. Because your content lives in a normal iframe document, standard DOM APIs (`document.getElementById`, `document.head.appendChild`, `document.querySelector`) work as usual — but the document's lifecycle events (`DOMContentLoaded`, `load`) fired **before** your scripts ran, so listeners for them never execute. Violating any of these produces a blank, broken, or runaway artifact:

1. **Code fence MUST be ` ```html type="renderer" `** — without `type="renderer"` the entire block is displayed as **inert source code text** (the user sees raw `<html>` tags, not a rendered page). This is the #1 most common fatal mistake and makes the ENTIRE output useless. Triple-check: your opening fence must read exactly ` ```html type="renderer" `, not ` ```html `, not ` ```html type=renderer `, not ` ```htm type="renderer" `.
2. **Execute scripts directly — NEVER use `DOMContentLoaded`.** By injection time that event has already fired, so the listener never runs → blank render. Wrap logic in an IIFE that runs immediately; place each `<script>` after its target `<div>`.
3. **Never place anything after `</html>` — especially chart/data scripts.** The renderer discards ALL trailing content — scripts after `</html>` are silently dropped, producing empty chart containers with no error message. This is the #1 cause of "charts don't render." ALL `<script>` tags (including ECharts initialization, table population, and data logic) MUST live inside the `<html>` element, placed directly after their target `<div>`.
4. **Tailwind Play CDN is REQUIRED** — `<script src="https://cdn.tailwindcss.com"></script>` must appear in every artifact. Do NOT use `cdn.jsdelivr.net/npm/tailwindcss` (that's the build tool, not a browser runtime). Tailwind utilities (e.g. `max-w-3xl`, `text-sm`, `rounded-2xl`) are **class names** — they go in `class=""`, NEVER in `style=""`. Putting a Tailwind class inside a `style` attribute is silently ignored (it is not valid CSS).
5. **No `100vh` / `min-height:100vh` / `height:100%` / `min-h-screen` / fixed root height / `overflow:hidden` on html/body** — causes infinite growth OR zero-height collapse in the resize-observed iframe. This includes the Tailwind utility `min-h-screen` (which compiles to `min-height:100vh`) and any CSS on `html`, `body`, or wrapper divs that references viewport height. The iframe has no fixed viewport — it grows to fit content; referencing its height creates a feedback loop. Also banned: the "full-screen app" pattern of `position:fixed;inset:0` + `overflow:hidden` on body — this collapses the iframe to near-zero height because nothing pushes it to grow. **Common traps and their fixes:**
- **Hero/landing section** (the #1 offender): do NOT write `min-height:100vh;display:flex;align-items:center` to center content. Use generous padding instead (`padding:120px 24px` or Tailwind `py-32`) — the section will appear tall without referencing viewport height.
- **Floating/particle decorations**: do NOT use `position:fixed` (banned by HC#12). Use `position:absolute` inside a `position:relative` section wrapper with `overflow:hidden`.
- **Animation keyframes with `vh`** (e.g., `translateY(110vh)`): while transforms don't cause growth directly, `vh` is unstable in the iframe (its value shifts as content streams in), making animation distances unpredictable. Use fixed `px` values instead.

For Canvas-first/3D archetypes, give the canvas container an **explicit fixed height** (500–650px) and use `position:relative` + `position:absolute` for overlaid UI, not `position:fixed`. **Three.js correct pattern**:
```html
<div style="position:relative;width:100%;height:600px;border-radius:16px;overflow:hidden">
  <div id="canvas3d" style="width:100%;height:100%"></div>
  <div style="position:absolute;left:16px;top:16px">HUD overlay</div>
</div>
<script>
(function init(n){
  if(typeof THREE==='undefined'||typeof THREE.OrbitControls==='undefined'){   // both globals, not just THREE
    if(n<40){setTimeout(function(){init(n+1)},250);return;}
    return;
  }
  var container=document.getElementById('canvas3d'); if(!container)return;
  var w=container.clientWidth, h=container.clientHeight;   // from the container — NOT innerWidth/innerHeight
  var renderer=new THREE.WebGLRenderer({antialias:true});
  renderer.setSize(w,h); container.appendChild(renderer.domElement);
  var camera=new THREE.PerspectiveCamera(60,w/h,0.1,1000);
  var controls=new THREE.OrbitControls(camera,renderer.domElement);
  // ...scene setup, then renderer.render(scene,camera) inside a rAF loop
})(0);
</script>
```
**Three.js CDN & addon rules** (applies whenever you use Three.js or any library with separate addon scripts):
- **Version pin**: Three.js deleted the UMD addon directory (`/examples/js/`) in **r148**, and dropped the UMD core build (`build/three.min.js`) a little later — modern releases ship only ES modules (`three.module.js`, `/examples/jsm/`). Since `import`/`export` is banned in this renderer, the last usable release is **r147**. Correct CDN pair:
  `<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js"></script>`
  `<script src="https://cdn.jsdelivr.net/npm/three@0.147.0/examples/js/controls/OrbitControls.js"></script>`
  Any version ≥0.148.0 with an `/examples/js/` path 404s, and ≥0.160.0 has no `three.min.js` either — both produce a blank viewport with no error. Never use `three@latest`.
- **Multi-library retry guard**: When loading Three.js + addons as separate `<script>` tags, the retry condition must check ALL globals: `if(typeof THREE==='undefined'||typeof THREE.OrbitControls==='undefined'){if(n<40){setTimeout(function(){init(n+1)},250);return;}...}`. OrbitControls attaches to the `THREE` namespace only after its own script loads; checking just `THREE` is insufficient.
- **Animation loop allocation ban**: NEVER create `new THREE.Vector3()`, `new THREE.Matrix4()`, `new THREE.Color()`, etc. inside `requestAnimationFrame` callbacks or any function called every frame. Pre-allocate reusable temporaries outside the loop (`var _v = new THREE.Vector3()`) and reuse via `.set()`/`.copy()`. At 60fps, per-frame allocation causes visible GC stutters on mobile and degrades performance on desktop for particle-heavy scenes (e.g., 200+ particles each needing tangent/normal = thousands of allocations/sec).

6. **Each chart/section MUST have its own `<script>` tag — separate scripts are error firewalls.** A `<script>` tag is both a parse boundary and an execution boundary: (a) a *syntax error* kills only its own `<script>` before anything runs — other tags are unaffected; (b) an *uncaught runtime error* (wrong API call, undefined variable, invalid data format) aborts execution of that script but does NOT propagate to other `<script>` blocks. Combining multiple chart inits into one `<script>` means one bad ECharts option, one `classList.add("")`, one wrong `markLine.data` format will **cascade-kill every chart after it** — producing "first chart works, rest are blank." Place each `<script>` inside its `.reveal` wrapper, after its target `<div>`. Common fatal errors: missing `:` in object literals (`data[...]` instead of `data:[...]`), unmatched braces, passing empty strings to `classList.add()/toggle()`, wrong `markLine`/`markPoint` data format. Follow **Brace-depth discipline** in *Chart & Visualization Rules* (in [chart-rules.md](references/chart-rules.md)).
7. **External libraries**: use jsDelivr; **never BootCDN**. Always guard with the **retry pattern** (see *Chart & Visualization Rules* in [chart-rules.md](references/chart-rules.md)) — during streaming, your inline script can execute before the CDN script finishes loading, so a fail-fast guard would permanently show the fallback. Retry with `setTimeout` before giving up.
8. **Google Fonts via `<link>` only** — load fonts with `<link href="https://fonts.googleapis.com/css2?...">` at the top of the HTML. Do NOT use `@import url(...)` inside injected styles — it delays font loading and may fail in the sandboxed renderer.
9. **ECharts container height is MANDATORY** — every `<div>` that will be initialized with `echarts.init()` MUST have an explicit `style="height:XXXpx"` (typically 300–450px). Without it, ECharts renders as 0px invisible. Example: `<div id="chart" style="height:380px;width:100%"></div>`.
10. **No Markdown syntax inside HTML blocks.** The renderer is an HTML engine, NOT a Markdown parser. `**bold**`, `*italic*`, `# heading`, `- list item`, and `[link](url)` all render as literal text (users see the asterisks/hashes). Use proper HTML tags instead: `<strong>`, `<em>`, `<h2>`, `<ul><li>`, `<a href="...">`. This is a common slip when the content was originally drafted as Markdown — always convert to HTML tags before emitting.
11. **Close every tag you open.** Unclosed `<strong>`, `<em>`, `<span>`, `<div>`, etc. cause all subsequent content to inherit that element's styling — e.g., an unclosed `<strong>` makes the rest of the page bold. Especially watch for nested inline tags in dense paragraphs. When in doubt, flatten — avoid nesting `<strong>` inside `<strong>` or `<span>` inside `<span>` at depth >2.
12. **No `position:fixed` in the renderer.** The iframe has no fixed viewport — it grows to fit content. `position:fixed` elements position relative to the iframe's "viewport" which changes as content loads, producing tooltips/modals that appear in wrong locations or off-screen. Use `position:absolute` relative to a positioned parent container instead. For tooltips on hover, position relative to the triggering element or use `position:absolute` within the section wrapper.
13. **Never fabricate image URLs.** The only embeddable sources are a URL the user supplied, a `<uri>`-tagged URL from search results, and an HTTP URL `image_gen` handed back for a decorative slot. `<image reference_id="...">` without `<uri>` = NOT usable. No URL = no `<img>` tag — remove the container entirely. Full rules in *Icon & Visual Enrichment Strategy → Priority 1* (in [design-system.md](references/design-system.md)).
14. **No external asset dependencies beyond CDN libraries and Google Fonts.** Do NOT reference 3D model files (`.glb`, `.obj`), audio files (`.mp3`, `.wav`), video files, or any asset that requires self-hosting or doesn't exist on a public CDN. These files do not exist in the renderer sandbox and will fail to load — producing "Loading..." screens that never resolve, blank 3D viewports, or "file not found" placeholders. If a visualization requires such assets, substitute with programmatically generated geometry (Three.js primitives, procedural meshes), inline SVG, or embedded data arrays. The only safe external loads are: (1) CDN JS libraries from jsDelivr, at the exact paths in *Pinned CDN paths* below, (2) Google Fonts via `<link>`, (3) CDN-hosted data files (e.g., the GeoJSON map outlines listed with those pins), (4) image URLs from verified `<uri>` search results or from `image_gen`.
15. **Output language matches the user's request language.** The HTML artifact's visible text (headings, labels, descriptions, tooltips) must be in the same language as the user's current-turn message. If the user writes in Chinese, the artifact is in Chinese; if in English, the artifact is in English. Exception: the user explicitly specifies a target language (e.g., "用英文写" or "write it in French").

---

### Technology Constraints (CRITICAL)

All output must be **vanilla HTML + CSS + JS**. No build step, no compilation, no bundler.

**Frameworks — FORBIDDEN:**
- React, Vue, Angular, Svelte, SolidJS, Preact, Next.js, Nuxt, Astro, or any JSX/TSX syntax.
- TypeScript — output must be plain JavaScript only.
- CSS preprocessors requiring compilation (Sass, Less, PostCSS).
- ES module syntax (`import`/`export`) — the renderer does not support it.

**No template syntax in HTML body**: `.map().join('')`, `${variable}`, `{expression}` are JavaScript — they ONLY work inside `<script>` tags. Written directly in HTML markup, the browser renders them as **literal visible text** on the page. This is the classic "confused HTML with JSX" failure. If you need to generate repetitive DOM (e.g., a list of cards from data), use a `<script>` with `createElement` or `container.innerHTML = data.map(...)` — never embed JS expressions in the HTML body outside a script.

**Allowed CDN libraries only** via `<script>` / `<link>` tags. **Prefer pure SVG + Canvas + vanilla JS** — zero-dependency and the most stable under streaming. Reach for a library only when native drawing would be genuinely complex: ECharts / Chart.js / D3 / Plotly for charts, Tailwind (Play CDN only) for styling, Google Fonts for typography, Three.js / p5.js / JSXGraph / Leaflet / MathJax only when the content actually requires 3D, creative coding, geometry, maps, or formulas, and Remix Icon or Lucide when a page needs roughly eight or more icons (below that, hand-written inline SVG is smaller and fully themeable — see [svg-guide.md](references/svg-guide.md)).

**Pinned CDN paths — copy these verbatim; do NOT guess a path.** Every one is a classic (non-module) build that exposes a global, so it works in a plain `<script>`. Guessing is how the Three.js trap above happens: many packages now ship ES modules only, and the wrong path 404s or throws `Unexpected token 'export'` with no visible error.

| Library | Global | Tag |
|---|---|---|
| ECharts | `echarts` | `<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>` |
| Chart.js | `Chart` | `<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.js"></script>` (`.umd.js` — `chart.min.js` is ESM and will fail) |
| D3 | `d3` | `<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>` |
| Plotly | `Plotly` | `<script src="https://cdn.jsdelivr.net/npm/plotly.js@2/dist/plotly.min.js"></script>` (4.4 MB — prefer ECharts unless you need it) |
| p5.js | `p5` | `<script src="https://cdn.jsdelivr.net/npm/p5@1/lib/p5.min.js"></script>` |
| JSXGraph | `JXG` | `<script src="https://cdn.jsdelivr.net/npm/jsxgraph@1/distrib/jsxgraphcore.js"></script>` + `<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/jsxgraph@1/distrib/jsxgraph.css">` |
| Leaflet | `L` | `<script src="https://cdn.jsdelivr.net/npm/leaflet@1/dist/leaflet.js"></script>` + `<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1/dist/leaflet.css">` |
| Remix Icon | none (pure CSS) | `<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/remixicon@4/fonts/remixicon.css">`, then `<i class="ri-bar-chart-2-line" style="color:var(--accent)"></i>` — 1539 icons in matching line/fill pairs. No JS, so nothing can mis-time under streaming: **the safest icon set here** |
| Lucide | `lucide` | `<script src="https://cdn.jsdelivr.net/npm/lucide@1/dist/umd/lucide.min.js"></script>`, mark slots `<i data-lucide="trending-up"></i>`, then call `lucide.createIcons()` from inside the HC#7 retry guard. 404 KB, and it only converts slots present when it runs |
| Three.js | `THREE` | pinned to r147 — see *Three.js CDN & addon rules* above |
| MathJax | `MathJax` | `<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>` — see *Math Formulas* in [quality-and-mobile.md](references/quality-and-mobile.md) |

Additional rules:
- ECharts geo/map: you **must** `fetch()` a GeoJSON file and `echarts.registerMap()` it before `setOption` — the v5 bundle ships no map data, so the core library alone renders a blank map. Verified sources: `https://cdn.jsdelivr.net/npm/echarts@4.9.0/map/json/world.json` (217 countries, English names) and `.../china.json` (34 provinces, Chinese names). Both are plain `FeatureCollection`s whose `properties.name` supplies the region key your series `data` must match — a name mismatch silently renders the region unshaded. Leaflet additionally needs raster tiles from a tile server, and blocked tiles give you a gray box with working controls — so prefer ECharts geo with the GeoJSON above for any static choropleth or region map, and reach for Leaflet only when the content genuinely needs pan/zoom over real imagery.
- **Interaction state closure**: every control must have a bound handler, update the view, and provide feedback.
- **Never inline-style properties that JS toggles via class.** Inline `style="..."` has higher specificity than ANY class-based CSS rule — so if JS adds/removes a class to change `color`, `background`, `opacity`, etc., but that property is also in the element's inline style, the class change is silently ignored. Rule: any CSS property whose value changes between states (default/active/hover/disabled) must live ONLY in the stylesheet classes, never in the element's inline `style` attribute. **Tab/toggle buttons**: the active state typically fills with `var(--accent)`, and at tab-label sizes most accents in this system clear 4.5:1 against neither white nor `--text` — so prefer filling the active tab with `var(--accent-soft)` and marking it with an accent underline or border. Define both default and active text colors in the stylesheet classes (`.tab-btn{color:var(--muted)}` and `.tab-btn.active{color:var(--text);background:var(--accent-soft);border-bottom:2px solid var(--accent)}`), never in inline style — otherwise the active color is permanently overridden. If you do want a solid accent fill, bold the label and set it ≥18px (see *Accent fill strategy* in [design-system.md](references/design-system.md)).
- **Overflow prevention**: use `overflow:hidden` or `overflow:clip` on **section-level containers** with animations or absolutely-positioned children (NOT on `<html>`, `body`, or the outermost wrapper — that is banned by HC#5 above).
- `color-mix()` is allowed — the renderer runs in evergreen Chromium (always latest stable; `color-mix()` landed in 111, well below current baseline). The skeleton uses precomputed `var(--accent-soft)` and `var(--border)` for the most common derived colors; for other tints use `color-mix()` freely (see *Design Polish* in [design-system.md](references/design-system.md)).

---

### Output Requirement (NON-NEGOTIABLE — applies to visualization requests only)

When the user's request falls within this Handbook's scope (data visualization, infographics, interactive tools, styled reports), your task is **NOT complete** until your final response contains at least one ` ```html type="renderer" ` code block with ≥ 200 characters of real HTML content.

- Computing data in CI is an **intermediate step**, not the deliverable.
- Searching for images is an **intermediate step**, not the deliverable.

If your final message does not contain a renderable HTML artifact, the task has **FAILED** regardless of what tools you called. Always end with the HTML.

(This requirement does NOT apply to pure data-processing, Excel, or file-generation tasks where the deliverable is a download link — those follow the CI Handbook's *File Operation Rules*.)

---

### Tool Loop Prevention (IMPORTANT)

When using `general_search` or other tools:
- **Plan before searching.** Before the FIRST search, decide: what specific data gaps need filling? List them (e.g., "need 3 stats + 1 image"). Aim for ≤ 5 batches (≤ 15 total searches) to cover all gaps. If the topic is familiar enough to produce the artifact from general knowledge + CI computation alone, skip searching entirely — searches are for real-time data and image URLs, not for background knowledge you already have. Also: do NOT use CI merely to reorganize search results into a structured dict/JSON and print it — that wastes a tool round and echoes data already in context. Use CI only for computation (math, date conversion, data transformation) or for direct file generation. Go straight to HTML output when the data is already in search results.
- **Search parallelism ≤ 3.** Issue at most 3 parallel `general_search` tool calls per batch. Wait for all results to return, then reassess what gaps remain before planning the next batch. Firing more than 3 searches simultaneously floods context with redundant or low-value results and leaves no room for the HTML artifact itself.
- **Multi-entity comparisons** (e.g., "compare 5 vendors/products/countries across N dimensions"): these are the #1 context-explosion trigger. Do NOT search once per entity per dimension — that produces entity × dimension queries, flooding context. Instead: (a) lean on general knowledge for well-known entities (major tech companies, popular frameworks, famous cities — you already know enough to fill 80% of the table); (b) search only for specific numbers you cannot confidently state from memory (latest quarterly revenue, exact market-share %, recent price changes); (c) combine multiple entities into ONE query (e.g., "2024 global cloud market share AWS Azure GCP" instead of three separate searches). Target: ≤ 2 broad panoramic searches + ≤ 3 targeted fact-checks = 5 total for any comparison task.
- **If 3 consecutive searches return no useful NEW information**, STOP searching and use whatever you have gathered. Do NOT retry the same query with slight variations endlessly.
- If real data is genuinely unavailable after searching (e.g., real-time stock prices), you may use placeholder data **only if** it is visibly labeled as sample/placeholder data in BOTH the UI and your accompanying text, with the source limitation noted. This is the sole exception to the Phase 1 no-fabrication rule.
- **Maximum 30 tool calls total per task**. If you reach this limit, immediately proceed to HTML output with available information.
- **Self-check**: If you notice you have called `general_search` more than 6 times and still don't have what you need, the information is likely unavailable — stop and produce the artifact with what you have. Even if searches ARE productive, remember: every search result consumes context that the HTML artifact needs. Prioritize leaving room for the output.

---
### Streaming-Optimized HTML Structure (CRITICAL)

Structure your HTML so each section renders independently as tokens stream in. The key rule: **place each chart's `<script>` inside its section wrapper `<div>`** (after the chart container), not as a sibling outside — this keeps `nth-child` animation counting correct.

**The skeleton in [skeleton-templates.md](references/skeleton-templates.md) implements the Dashboard / Report archetype only.** For any other archetype, keep the streaming principles (CDN tags first, per-section embedded scripts, reveal staggering, self-contained sections) but replace the structure according to the Layout Archetype System (in [design-system.md](references/design-system.md)).

**WARNING: The colors and font in the skeleton template are for the Science/Research category ONLY. Unless your category IS Science/Research, you MUST replace them with values from the Color and Font Rotation Systems (in [design-system.md](references/design-system.md)) matching YOUR artifact's category — including the chart option colors inside the ECharts script. Use `getComputedStyle` to read CSS variables at runtime (see *Chart theming* in [chart-rules.md](references/chart-rules.md)), or hardcode the category's hex values as fallback. For interactive elements, follow the *Accent fill strategy* section in [design-system.md](references/design-system.md) (icon tiles: accent on accent-soft; small button/pill text: always --text, never --accent; dark-bg: accent fill with dark text). Do NOT copy the Science/Research hex values into a different category's artifact.**

For the full Dashboard skeleton HTML template, rendering order, customization guide, and archetype structural sketches, see [skeleton-templates.md](references/skeleton-templates.md).

---

### Core Design Philosophy

**Make creative, distinctive frontends that surprise and delight.** Fight the instinct to converge toward generic output:

- **Every artifact should feel intentionally designed for its specific context.** A financial report should feel different from a biology tutorial which should feel different from a travel guide. The Layout Archetype System (in [design-system.md](references/design-system.md)) is the enforcement mechanism for this — structure is chosen per genre, never inherited from the skeleton by default.
- **Interactive over static.** Include hover effects, animations, and interactive chart elements.
- **Lean toward the bold and unexpected** rather than the safe and conventional.
- **Content is king** — all design serves clarity and comprehension.
- **Working beats beautiful** — a functional plain page outranks a polished broken one. See *Data & Factual Reliability* and *Functional Completeness* immediately below.

---

### Data & Factual Reliability

Producing beautiful pages with fabricated data is WORSE than producing a plain page with correct data. Follow these rules strictly:

1. **Never fabricate data the user expects to be real.** If the prompt implies real data (stock prices, scientific measurements, published statistics), you MUST either:
   - Fetch real data using search/CI tools, OR
   - Clearly label values as "sample/placeholder data" with a visible disclaimer in the UI (e.g., a banner: "Displaying sample data — provide your dataset for real results")

2. **Never invent specifics you cannot verify.** Do not fabricate sample sizes (e.g., "n=200"), publication years, or numeric claims that look authoritative. If you lack a specific number, say "~X (estimated)" or use a clearly hypothetical framing.

3. **When the user's prompt requires THEIR data but they provided none** (e.g., "visualize my sales data" with no attachment), produce a functional template with clearly-marked placeholder data and a note: "Replace the sample data below with your actual values." Do NOT silently fill in random numbers as if they were real.

4. **Scientific/academic content**: If citing temperatures, rates, constants, or projections, use well-known reference values (e.g., IPCC figures for climate, standard physical constants). If you cannot verify a number, state the source assumption explicitly in the output.

5. **Consistency across artifacts**: If a chart shows a value of 42%, any accompanying text, table, or tooltip referencing the same metric must also say 42%. Cross-check all numeric mentions before finalizing.

6. **Do NOT trust data from prior conversation turns without re-verification.** If a previous turn (especially from a Fast/lightweight model) provided specific numbers, prices, dates, or statistics, treat them as **unverified claims** — they may be hallucinated. Before charting or visualizing that data, re-fetch it yourself via `general_search` or CI computation. This is particularly critical for real-time data (stock prices, exchange rates, sports scores, weather) where the prior turn's numbers cannot be validated from memory alone. A beautiful chart built on fabricated numbers is worse than no chart at all.

---

### Functional Completeness & Interactive Integrity

A visually polished page that does not work is a failure. The most damaging pattern is: "looks good on first render, but core interaction is broken."

**Why this happens (root cause):** You generate tokens linearly. UI structure (divs, classes, headings, icons) is easy and templatable — you can produce 200 lines of polished HTML confidently. JS logic (event handlers, state machines, game loops) is hard and error-prone — bugs are invisible until runtime. The natural result: you invest early tokens on confident work (structure/styling), then encounter complexity when writing the JS, and either produce broken logic or run out of budget. The page looks professional but does nothing.

**Countermeasure:** Plan the `<script>` logic FIRST in your mind. Identify what events fire, what state changes, and what re-renders. If the JS plan has gaps you cannot fill, simplify the UI to match what the JS can support — not the other way around. Never commit to a complex UI structure assuming "the JS will work out."

**Rules:**

1. **Every declared feature must work.** If your page claims "AI scoring," "split," "drag to reorder," or "save to PDF," that feature MUST function when the user clicks it. Never advertise capabilities you did not implement. If a feature is infeasible in a single HTML file, omit it entirely rather than showing a dead button.

2. **Test your interactive flow mentally.** Before finalizing game/tool/app output, trace the user journey:
   - What happens on first load? (Must not be blank)
   - What happens on the primary action (click Start, submit form, press Play)?
   - What happens on edge cases (no input, rapid clicks, window resize)?
   If any step leads to a blank screen, frozen state, or console error, fix it.

3. **Games: core gameplay loop must function.**
   - The game must start when the user clicks Start/Play
   - Controls must respond (keyboard/mouse as documented)
   - Game state (score, lives, level) must update correctly
   - Win/lose conditions must trigger appropriately
   - DO NOT sacrifice game logic for visual effects — a working plain game beats a broken beautiful one

4. **Tools/Calculators: output must reflect input.**
   - Changing an input field must update the result
   - Edge inputs (0, negative, empty) must not break the page
   - Units and labels must be correct

5. **Never split interactive logic across blocks** — see *Block count* rules above.

6. **Button/control labeling must match behavior.** If a button says "Download PDF" but actually just shows an alert, that is a failure. Either implement the real behavior or label the button honestly (e.g., "Preview" instead of "Download").

7. **Complexity budget** (applies to Game/App/Tool archetypes — enforced by *Pre-Generation Gate* condition 1):
   - Each interactive feature costs roughly: UI elements + event handler + state update + visual feedback ≈ 40–80 lines of JS.
   - A single block comfortably holds ~5–6 interactive features at moderate complexity. If the prompt lists more, PRIORITIZE: which ones define the minimum viable experience? Deliver those. Note the rest as "could be added in a follow-up."
   - **Decision rule**: if you cannot mentally trace a feature's full cycle (trigger → state change → UI update → edge case handling) within a few seconds of thought, that feature is too complex to ship unverified. Cut it or simplify it.
   - When you must cut: prefer cutting SECONDARY features (cosmetic animations, settings panels, leaderboards) over PRIMARY ones (the core game loop, the main calculation, the primary input→output flow).

8. **Format is a hard constraint** (enforced by *Pre-Generation Gate* condition 2). When the user names a specific form — "mind map," "timeline," "diagram," "interactive chart," "game," "calculator" — your output MUST be that form. Delivering a different format is a task failure regardless of content quality.

---

## Reference Files — read the ones relevant to your task before generating HTML

- **ALWAYS read** [design-system.md](references/design-system.md) — style auto-inference, layout archetype selection, color/font rotation, icon strategy, visual hierarchy, design polish. Required for every HTML artifact.
- **ALWAYS read** [skeleton-templates.md](references/skeleton-templates.md) — full Dashboard skeleton template, rendering order, customization guide, archetype structural sketches (Editorial, Document, Game).
- **Read if your artifact includes charts**: [chart-rules.md](references/chart-rules.md) — ECharts theming, CDN retry guards, brace-depth discipline, treemap/timeline/custom series patterns.
- **Read if your artifact includes node-link diagrams, trees, flowcharts, mind maps**: [diagram-rules.md](references/diagram-rules.md) — SVG geometry rules, orthogonal connectors, data-driven layouts, mind map patterns.
- **Read if you hand-draw SVG beyond a few simple stroke icons** (illustrations, gauges, progress rings, custom shapes, anything using gradients/clip paths/masks): [svg-guide.md](references/svg-guide.md) — authoring rules, the traps that make SVG silently render blank or black, theming, accessibility, and where to source icon paths. For three or four plain icons the samples in design-system.md are enough.
- **Read before finalizing output**: [quality-and-mobile.md](references/quality-and-mobile.md) — quality checklist, mobile responsiveness, motion & animation, image gallery, math formulas, token efficiency.
