# Quality, Mobile & Additional Rules

### Image Gallery Pattern

When multiple verified images are available (per *Icon & Visual Enrichment Strategy → Priority 1* in [design-system.md](design-system.md)), render a data-driven CSS grid (`grid-template-columns:repeat(auto-fill,minmax(180px,1fr))`) of `<figure>` elements with `<figcaption>`. Key rules:
- Build from a JS array of `{src, caption}` objects — do NOT hardcode image markup; loop from the array.
- Apply `onerror` hide on each `<img>` (graceful degradation).
- Add a click-to-enlarge overlay using `position:absolute` (NOT `fixed` — see HC#12) within a `position:relative` container, if image count >= 4.
- The overlay container must be a sibling of the gallery grid, inside the same relative parent.
- Each gallery block must be self-contained with its own CSS variable injection (same rule as any continuation block).

---

### Motion & Animation

The `.reveal` stagger system, `.metric-card` hover, and `.tbl-row` hover are defined in the skeleton's CSS injection script — do not duplicate them. Below are the additional rules that govern animation behavior:

**IMPORTANT**: Chart `<script>` tags must be **inside** their `.reveal` wrapper div, not as siblings outside — otherwise `<script>` elements count as nth-child siblings and break the delay sequence.

**Reveal limit**: Only apply the `.reveal` class to the first 5–6 sections. Elements beyond that should render without the class (visible by default) — CSS animations on off-screen elements complete before the user scrolls to them, leaving those sections permanently stuck at `opacity:0`.

**Never combine `.reveal` with elements that have their own `animation` property** (tab panels, modals, toggled content). `.reveal` sets `opacity:0` as its base state and relies on its `animation:fadeUp ... forwards` to persist at `opacity:1`. If another class with higher specificity (e.g., `.panel.active{animation:fadeIn .35s ease}`) overrides the `animation` property, the `forwards` fill is lost — the element fades in briefly, then snaps back to `opacity:0` when the overriding animation ends without `forwards`. This produces a "renders then immediately disappears" bug. Rule: `.reveal` is for static, always-visible sections only — never on elements with `display:none` toggling or their own animation declarations.

**SVG `transform` attribute vs CSS `animation` conflict**: NEVER place a CSS animation that sets `transform` on the SAME element that uses an SVG `transform` attribute for positioning (e.g., `<g transform="translate(200 130)" class="float">`). The CSS animation's `transform` value **completely overrides** the SVG attribute, removing the positioning and causing the content to render at the SVG origin — the user sees only the small fragment that falls within the viewBox. Fix: nest TWO groups — an outer group for positioning and an inner group for animation:
```xml
<g transform="translate(200 130)">   <!-- positioning (never animated) -->
  <g class="float">                   <!-- animation layer -->
    <!-- shapes drawn relative to (0,0) -->
  </g>
</g>
```
This applies to ALL SVG animation patterns (`.float`, `.swim`, `.wiggle`, `.pulse`, etc.) when the animated group also needs translation.

---

### Mobile Responsiveness (MANDATORY)

The renderer is viewed on both desktop and mobile. Both must work well, but mobile failures are more common and harder to catch — pay extra attention to mobile constraints. Text overflow, label overlap, undersized touch targets, and truncated tables are the top mobile complaints.

**The 360px test** (general principle): Before finalizing, mentally render your output at 360px viewport width. Any element with a fixed width >320px, any text with `font-size` >24px without responsive scaling, any grid that doesn't collapse to single-column — these WILL overflow. Every container must accommodate its content at minimum viewport width, either by wrapping, scrolling, or scaling.

Apply these rules:

**Touch targets (CRITICAL on mobile):**
- All interactive elements (buttons, links, toggles, clickable cards) MUST have a minimum tap area of 44×44px. This means: `min-height:44px; min-width:44px` on the element or its clickable wrapper. Padding counts toward this size.
- Spacing between adjacent touch targets: at least 8px gap to prevent mis-taps.
- Game controls and primary action buttons on mobile: prefer 48×48px or larger for comfortable thumb reach.

**Icon sizing:**
- SVG icons used as standalone interactive elements (not inline with text): minimum 24×24px on all viewports. The handbook's 20×20px examples are for inline decorative use alongside text — standalone icons (e.g., in icon-only buttons or nav elements) need 24px minimum, 32px preferred on mobile.
- Inline decorative icons (next to headings or in metric cards): 20px is fine — the adjacent text provides the touch target.

**Text & Typography:**
- All text containers must use `overflow-wrap:break-word` (or Tailwind `break-words`). Long words/URLs must not overflow their containers.
- Headings: use `text-2xl sm:text-4xl` (scale down on mobile). Never set a fixed large `font-size` without a responsive breakpoint.
- Body text: minimum `font-size:14px` on mobile for readability. Never go below 12px for any visible text.
- Chart axis labels: on narrow screens (< 640px), long category labels MUST be rotated (`axisLabel:{rotate:45}` for ECharts) or truncated. A chart with 10+ overlapping x-axis labels is unreadable.

**Tables:**
- Wide tables (5+ columns) MUST be wrapped in `<div style="overflow-x:auto">` so they scroll horizontally on mobile rather than breaking the layout.
- Alternatively, use Tailwind's responsive `hidden` utilities to hide less-critical columns on small screens.

**Layout:**
- Cards and grid items: use `flex-wrap:wrap` (already required) with `min-width` that accounts for mobile (~160px minimum, not 300px+).
- SVG diagrams: always use `viewBox` + `width:100%;height:auto` so they scale. Never use fixed pixel widths > 600px without a responsive wrapper.
- ECharts containers: `width:100%` (not a fixed pixel width) so charts resize with the viewport.
- Horizontal scrollable areas (carousels, timelines): add `-webkit-overflow-scrolling:touch` for smooth momentum scrolling on iOS.


---

### Additional Robustness Rules

1. **ECharts geo/map**: MUST `fetch()` a GeoJSON file + `echarts.registerMap()` before `setOption` — no map data ships with the v5 bundle. Use the verified URLs in *Pinned CDN paths* in SKILL.md, and make your series `data` names match the file's `properties.name` or the region renders unshaded.
2. **Self-contained data**: embed data as JS variables. No runtime calls to arbitrary third-party or business API endpoints (they will CORS-fail in the sandbox). CDN-hosted static resources (GeoJSON files, font CSS, JS libraries) are fine — they serve `Access-Control-Allow-Origin: *`.
3. **Broken-image handling**: every `<img>` needs `onerror="this.style.display='none'"` — graceful degradation is non-negotiable.
4. **Untrusted content escaping (XSS)**: when inserting user-provided or file-derived strings into the DOM, use `textContent` / `createElement` — NEVER interpolate raw strings into `innerHTML` or inline event attributes.
5. **Contrast in custom-background sections**: when a section/card uses a background different from `--bg` (custom gradient, overlay, darker/lighter card), all text and chart elements inside must be contrast-verified against THAT actual background — not against the page `--bg`. Specifically:
   - Use `--text` (lightest) for body text inside custom dark sections, not `--muted` (which was designed for `--bg` contrast and may be too dim against a different dark gradient).
   - Chart data series (bars, lines, areas) inside a custom-background section must use colors that visibly contrast against the section's background — never use near-background colors (e.g., `#3a3a48` bars on a `#1a1a25` card).
   - Set text color directly on `<table>`, `<ul>`, `<ol>`, and other block-level elements inside dark sections — do NOT rely solely on inheritance. In some rendering environments, tables and lists do not inherit color reliably from ancestor divs.

---

### Token Efficiency (IMPORTANT)

Since the HTML is part of your output tokens:
- Follow the CSS mechanism table (Phase 2): prefer Tailwind utility classes (concise) over verbose inline CSS where both work
- Minimize HTML comments — the code should be self-explanatory
- Use 2-space indentation, no excessive blank lines
- For large datasets (100+ table rows), summarize or paginate in the UI rather than listing all rows
- Combine related CSS into compact rules

---

### Math Formulas

- **Static**: MathJax CDN with LaTeX syntax. Load the MathJax config BEFORE the library script: `<script>window.MathJax={tex:{inlineMath:[['\\(','\\)']],displayMath:[['$$','$$']]}}</script>` then `<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>`. **Do NOT enable single-dollar `$...$` inline math** — it collides with currency amounts ("$50", "$1T" become broken formulas), which are common in finance and news content. Write inline math as `\(...\)` and display math as `$$...$$`. **The body MUST use the SAME delimiters as the config** — since the config registers `\(...\)`, writing `$...$` in the body produces raw unrendered LaTeX. This is the #1 MathJax failure mode: config says `\(...\)` but body uses `$...$`.
- **Dynamic**: Use Unicode: `π ω α β Σ √ ∞ ≈ ≤ ≥ ² ³ ∫ ∂ ∇`
- **CRITICAL — LaTeX escape hazard** (canonical statement; the Precedence and Phase 1 sections point here): Because you output HTML directly in your response (not via Python), backslashes in `\theta`, `\frac`, `\text` etc. are safe — they pass through verbatim. If you ever must write LaTeX to a file in CI (rare exception), use raw strings `r"$$\frac{a}{b}$$"` or double-escape `"$$\\frac{a}{b}$$"` — Python interprets `\t` as TAB, `\f` as form-feed, `\r` as CR in regular strings, destroying formulas. Never write LaTeX formulas in regular Python strings.

---

### Quality Checklist

- [ ] Font from **Rotation System** (not banned)? Colors from **Rotation System** (not banned)? All borders via `var(--border)` (no neutral-gray rgba)?
- [ ] Each chart has its **own separate `<script>`** inside its `.reveal` wrapper (never multiple charts in one script)? **CDN retry-guard present** (`if(typeof echarts==='undefined'){setTimeout...}`)? ECharts divs have **explicit `height:XXXpx`**? Chart series/tooltip/axes themed to the palette (no library default colors)? Line/trend charts have `yAxis:{scale:true}`? Gradients extracted to a `var` (shallow setOption)? `label` at series level (never inside itemStyle/areaStyle)? `custom` series uses `shape:{x,y,width,height}` (not root-level)? Three.js pinned to `0.147.0` (the last release with UMD core + UMD addons)? Retry guard checks BOTH `THREE` and addon globals (e.g., `THREE.OrbitControls`)? No per-frame `new THREE.Vector3()`/`Matrix4()` allocation inside animation loop?
- [ ] Node-link diagrams: ONE SVG viewBox + ONE unit system, nodes + edges from one data table + render loops? Trees/org charts: layered rows + orthogonal elbows (NO diagonal lines), NO force layout, NO sibling-sibling edges? Spouses/partners adjacent on the SAME row (not stacked vertically)? No DOM-cards-with-guessed-SVG-overlay? All node coordinates within viewBox bounds (no negative x/y that clips off-canvas)? ZERO HTML elements inside any SVG (no `<sub>`, `<sup>`, `<br>`, `<span>`, `<strong>` — search your output for any HTML tag inside `<svg>...</svg>`; use `<tspan>` with `baseline-shift` or `dy` instead)? Connectors only flow downward in top-down layouts (no upward-pointing merge lines)? If using `<g transform="translate(...)">` for nodes, are ALL edge path coordinates in GLOBAL SVG space (local anchor + translate offset)? ViewBox height ≥ lowest element's y + height (no bottom clipping)? **Every connector `<path>`/`<line>`/`<polyline>` has explicit `fill:none`** (SVG defaults to `fill:black` — missing `fill:none` turns bent paths into solid black polygons)? Preferred: use blanket `svg path, svg line, svg polyline { fill: none; }` — then verify NO connector variant class (`.connector-highlight`, `.edge-yes`, etc.) accidentally omits it?
- [ ] No `position:fixed` anywhere (use `position:absolute` with a positioned parent)?
- [ ] No `DOMContentLoaded`, **no scripts after `</html>`** (verify: every `<script>` tag is ABOVE the `</html>` line — this is the #1 blank-chart cause), no `100vh`/`min-height:100vh`/`min-h-screen`/`height:100%` on any layout container or body? Search for `100vh`, `min-h-screen`, `min-height:100`, and `vh` in `@keyframes`. Hero uses `padding` for height, NOT `min-height:100vh`.
- [ ] Tailwind from `cdn.tailwindcss.com`? Tailwind utilities in `class=""` only (never in `style=""`)? Vanilla HTML+JS only (no React/Vue/import)?
- [ ] **FIRST CHECK — Every block's fence reads exactly ` ```html type="renderer" `**? (Missing `type="renderer"` = user sees raw code, total failure.) Default = ONE block. Any page with JS filtering/sorting/dynamic rendering: ALWAYS one block — DOM and script together, NEVER in separate blocks. Non-interactive: one block unless genuinely massive?
- [ ] SVG icons topic-specific (not one icon stamped everywhere), all from ONE system, and clean against the pre-ship list in [svg-guide.md](svg-guide.md) — `fill="none"` on stroke shapes, unique gradient/clip ids, `currentColor` rather than hardcoded hex? **ZERO emoji in the entire HTML** (see emoji ban in SKILL.md) — not in table cells, list items, buttons, headings, placeholders, particles, or body text (verbatim quoted data exempt)? Real images only via verified tool-result URLs or 1 search?
- [ ] Archetype chosen by **genre** (not subject)? If user omitted style, did you infer from content (Style Auto-Inference) rather than defaulting to generic? Structure differs from dashboard skeleton? Metric-card rows ONLY in Dashboard? Game/Canvas-first/App: button + card elevation hierarchy applied?
- [ ] Mobile-friendly: flex-wrap/auto-fit, no rigid columns? Tables wrapped in `overflow-x:auto`? Chart axis labels won't overlap on narrow screens (rotated or truncated)? Headings use responsive sizing? Accent fill strategy followed (soft-fill pattern for light-bg categories)?
- [ ] All data from CI (not hardcoded guesses)? Values consistent across charts/text? Untrusted strings escaped? Search-derived data: fetched not snippet-built, labels match the column basis, provenance visible? If no real data available, are placeholder values clearly labeled as such?
- [ ] Every `<img src>` URL came from a `<uri>` tag in search results, a user-provided link, or an `image_gen` picture for a decorative slot (NEVER from memory, fabrication, guessed official-site paths, or `reference_id` without `<uri>`)? Each URL verified 200 in CI via Step C? If no source yielded a usable URL, are there ZERO `<img>` tags in the output? Every `<img>` has `onerror="this.style.display='none'"` + `alt` + `loading="lazy"`? CDN guards use the **retry** pattern?
- [ ] Every declared feature actually works? Games: start → play → score → end loop functional? Tools: inputs produce correct outputs? No dead buttons or fake "AI-powered" claims? Primary action does not produce a blank/frozen state? No empty-string arguments to `classList.add()/toggle()`? No non-CDN external assets (.glb, .obj, .mp3, self-hosted files) that won't exist at runtime?
- [ ] If user explicitly named a visualization form (mind map, timeline, diagram, interactive chart), does the output actually contain that form — not just text/bullets? Complexity budget respected (≤5-6 interactive features, each mentally traceable)? Pre-Generation Gate passed?
- [ ] Mind map? MUST use horizontal tree (`layout:'orthogonal', orient:'LR'`) unless ALL three conditions of rule 13 in [diagram-rules.md](diagram-rules.md) are satisfied (every label under 15 chars AND balanced branches AND under 20 leaves). If radial chosen despite this, no fixed `label.position`? Text of every label fully readable without overlap? No hand-coded polar angle/radius math? Container height ≥ visible-leaf-count × 38px (or `initialTreeDepth:1` for >20 leaves)? **Search your tree data for `label.color` — if ANY node sets a light text color (white/`#fff`/`#fafafa`), it MUST also set `label.backgroundColor` to a dark color; otherwise DELETE that `label.color` and rely on the dark-text series default (preferred)**?
- [ ] SVG elements with CSS animation: positioning `transform` on a SEPARATE outer `<g>` from the animated class (no single-element transform + animation)?
- [ ] If using MathJax: config and body delimiters match (both `\(...\)` / `$$...$$`)? Single-dollar `$...$` NOT enabled? No `$` currency amounts accidentally parsed as math?
- [ ] Typography rhythm applied (hero/heading `line-height` ≤1.2, body text ≥1.6)? Google Fonts loaded via `<link>` (not `@import`)? All opened tags properly closed?
- [ ] `overflow-wrap:break-word` on text-heavy containers with long strings (URLs, code)? No raw Markdown syntax (`**bold**`, `# heading`, `- list`) inside HTML?
- [ ] All visible text (headings, labels, tooltips, captions) in the SAME language as the user's current-turn message, unless they named a different target language (HC#15)?
- [ ] If YOU initiated the HTML (user didn't explicitly ask for it): is the simplest effective visualization form chosen — not over-engineered beyond what the content requires?