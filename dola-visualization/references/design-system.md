# Design System

### Style Auto-Inference (MANDATORY — do this BEFORE choosing an archetype)

When the user does NOT explicitly specify a visual style (e.g., they just say "make an html report" without saying "newspaper style" or "academic style"), you MUST still choose a distinctive style. **Never default to a generic look.** Infer the best archetype from the CONTENT itself:

| Content pattern | Inferred archetype | Inferred category |
|---|---|---|
| News / current events / "what happened today" / digests | **Editorial / Newspaper** | News/Editorial |
| Paper summary / research / innovations / "key findings" | **Document / Handbook** | Science/Research |
| Data comparison / rankings / KPIs / market data / benchmarks | **Dashboard / Report** | Finance/Markets or the subject's category |
| Tutorial / how-to / learning material / explainer | **Document / Handbook** | Education/Learning |
| Travel / food / lifestyle / gallery / showcase | **Magazine / Showcase** | Travel/Geography or Food/Lifestyle |
| Algorithm / system diagram / relationship / flowchart | **Canvas-first / Diagram** | Science/Research or Education/Learning |
| Game / puzzle / quiz / interactive challenge | **Game / Interactive** | Education/Learning or Entertainment/Media |
| Calculator / converter / configurator / form tool | **App / Tool** | Technology/Engineering or the subject's category |
| Timeline / chronology / historical progression | **Editorial / Newspaper** | History/Culture or News/Editorial |
| Product landing page / feature showcase / portfolio | **Magazine / Showcase** | Creative/Design |
| Sports stats / match results / athlete profiles | **Dashboard / Report** | Sports/Events |
| Recipe / cooking guide / menu | **Magazine / Showcase** | Food/Lifestyle |
| Scientific process / experiment / biological mechanism | **Canvas-first / Diagram** | Science/Research |
| Financial report / stock analysis / investment | **Dashboard / Report** | Finance/Markets |
| Health metrics / fitness tracking / medical info | **Dashboard / Report** | Health/Nature |
| Music / film / entertainment recommendations | **Magazine / Showcase** | Entertainment/Media |
| Code/API documentation / technical reference | **Document / Handbook** | Technology/Engineering |
| Personal resume / CV / self-introduction | **Magazine / Showcase** | Creative/Design |
| Comparison / "A vs B" / pros and cons | **Dashboard / Report** | (use subject's category) |
| Speed / distance / "show me the difference intuitively" | **Canvas-first / Diagram** | Sports/Events or Science/Research |

**The inference rule**: imagine the user HAD specified a style — what would they most naturally have said given their content? A news roundup user would have said "newspaper style"; a research summary user would have said "academic/paper style"; a metrics comparison user would have said "dashboard." Pick THAT archetype. The user omitting the style hint is NOT permission to produce bland, unstyled output — it means you must make the style decision yourself.

**Examples of correct inference:**
- "What are today's AI news? Make an html report" → infer Editorial/Newspaper + News/Editorial palette (same quality as if they had said "newspaper style")
- "Summarize key innovations of MAI-Thinking-1, make an html report" → infer Document/Handbook + Science/Research palette (same quality as if they had said "academic paper style")
- "Compare GPT-4o vs Claude performance data, make an html" → infer Dashboard/Report + Science/Research palette
- "Introduce Japan travel spots, make an html page" → infer Magazine/Showcase + Travel/Geography palette
- "I ran a marathon in 3:45:28, Kipchoge ran 1:59:40 — show me the speed difference" → infer Canvas-first/Diagram + Sports/Events palette (an animation or race visualization, NOT a static chart)
- "Dynamically demonstrate PCR denaturation, annealing and extension" → infer Canvas-first/Diagram + Science/Research palette (animated SVG process, NOT a text document)
- "Design a guessing game for a party" → infer Game/Interactive + Entertainment/Media palette

**When the user DOES specify a style** (e.g., "newspaper style", "academic", "dashboard", "game-like", "magazine layout"), use their explicit choice directly — no inference needed.

**Choosing the right FORM of expression** (not just archetype): The archetype determines page structure, but you must also choose the right *expressive form* within it. Form operates WITHIN your chosen archetype — it refines what the dominant content element should be (e.g., an animated SVG race inside a Canvas-first page), not the overall page structure. Common form-matching rules:

| User intent signal | Best form | Wrong form |
|---|---|---|
| "show me the difference intuitively" / "visualize the gap" | Animated comparison, race animation, side-by-side scale | Static table or bar chart with no narrative |
| "step by step" / "dynamically demonstrate" / "process" | Animated SVG/Canvas with play/pause, stage-by-stage reveal | Static diagram with all steps shown at once |
| "timeline" / "chronology" / "history of" | Vertical/horizontal scrollable timeline with dated nodes | Bullet-point list or plain table |
| "visual card" / "flashcard" / "summary card" | Compact card layout with key-value pairs, icons, rounded corners | Dense paragraph of text |
| "academic table" / "three-line table" | Bordered table with header/footer rules, no zebra striping, serif font | Colorful dashboard-style cards |
| "comparison" / "vs" / "A versus B" | Split-screen or side-by-side columns with shared metrics | Single merged list |
| "interactive" / "try it" / "play" | Working controls with immediate visual feedback | Static mockup that looks interactive but does nothing |

---

### Layout Archetype System (MANDATORY — choose BEFORE writing any HTML)

The Font/Color tables control flavor; **this table controls structure**. Pick the archetype by what the artifact **IS** (its genre), not what it is **ABOUT** (its subject). An AI news digest is Editorial, not a Technology dashboard; a finance-themed puzzle is a Game, not a Finance report; study notes about LLMs are a Document, not a tech dashboard.

| Archetype | Typical requests | Structure recipe |
|-----------|------------------|------------------|
| **Editorial / Newspaper** | news digests, daily briefings, essays, reviews, commentary | Masthead + dateline → kicker + serif headline → lede paragraph → article blocks separated by 1px hairlines (NO card boxes) → pull quotes → colophon footer |
| **Dashboard / Report** | data analysis, KPI summaries, financial reports, comparisons | The streaming skeleton: hero → metric cards → charts → tables → footer |
| **Document / Handbook** | study notes, tutorials, outlines, documentation, plans | Title block → table of contents → prose sections in a narrow reading column (`max-w-3xl`) with headings, callout boxes, code blocks; collapsibles optional |
| **Game / Interactive** | puzzles, quizzes, games, simulators | Compact title + one-line rules → board/play area front and center → tactile control buttons with pressed states → status panel. No hero block, no metric cards |
| **Magazine / Showcase** | travel, food, lifestyle, galleries, portfolios | Large lead image → captioned image blocks interleaved with short prose → sparse highlight cards |
| **Canvas-first / Diagram** | relationship graphs, maps, flowcharts, 3D scenes | One-line title → the visualization as the dominant element (give its container a generous fixed height, 500–650px) → compact legend → nothing else |
| **App / Tool** | calculators, converters, configurators, forms | Input controls + live output side by side (flex-wrap) → brief explanation below |

**Anti-convergence rules:**
- **Metric-card rows are EXCLUSIVE to the Dashboard/Report archetype.** If your topic has impressive numbers you want to highlight in Editorial/Document/Game contexts, use a `<dl>` definition list, bold inline text, or a styled `<table>` row — NOT the flex-wrap card pattern with hover effects. "5 Monarchs" in a History timeline is a `<dl>`, not a metric card.
- Outside Dashboard, these skeleton signatures are also **banned**: monospace `01`-numbered section headers and the 44×44 gradient-icon hero. Reintroduce one only if the chosen archetype genuinely benefits from it.
- When unsure how to implement a non-Dashboard archetype, render its recipe as a flat list of sections inside the standard wrapper — do NOT fall back to metric cards or numbered section headers.
- Vary structural details across artifacts even within one archetype: section header treatment, card radius and border, background tone. A dark background is NOT the default — Editorial, Document, and Magazine usually read better on the light palettes in the Color table.
- **Template self-check** before output: if swapping in text on any other topic would leave the page looking equally appropriate, you have produced a generic template rather than a design for this content — restructure per the archetype.


For the structural mini-sketches (Editorial, Document, Game archetypes), see [skeleton-templates.md](skeleton-templates.md).

### Font Rotation System (MANDATORY)

**BANNED**: `Manrope`, `Outfit`, `Inter`, `Roboto`, `Arial`, `Plus Jakarta Sans`, `Space Grotesk` — NEVER use.

**Selection table** — pick the category using the **genre-first rule** from the Layout Archetype System (an AI news digest → News/Editorial, NOT Technology; a math learning game → Education/Learning), then pick **ONE** font from that row. Vary your choice across artifacts — do not always default to the first option. All fonts below are on Google Fonts and support the 400–700 weight range:

| Category | Font options |
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

Load via: `<link href="https://fonts.googleapis.com/css2?family=FONT:wght@400;500;600;700&display=swap" rel="stylesheet">`

**Display pairing (serif-row categories ONLY: Finance/Markets, History/Culture, Math/Statistics, News/Editorial)**: these serif picks shine in headlines but tire in long body text. You may load ONE additional body font — headings use the row's pick; body text uses a neutral sans from: `Source Sans 3` · `Public Sans` · `Karla`. Two `<link>` tags maximum; do NOT pair fonts in other categories.

---

### Color Rotation System (MANDATORY)

**BANNED as `--bg`**: `#0f172a`, `#020617`, `#0a0a0f` — NEVER use for background.

**Anti-Technology bias**: Technology/Engineering is ONLY for artifacts whose primary subject is hardware, software engineering, networking, DevOps, or system architecture. These common topics are NOT Technology — use their correct row instead:
- AI/ML tutorial → Education/Learning
- Math/physics visualization or simulation (Fourier, fractals, pendulum, wave) → Science/Research
- Algorithm explainer or CS education → Education/Learning
- Tech company earnings → Finance/Markets
- Tech news digest → News/Editorial
- Scientific paper summary → Science/Research
- App UI mockup → Creative/Design
- Coding puzzle → Education/Learning palette & font + Game/Interactive archetype structure

**Selection table** — same category as the font (the genre-first rule applies here too), use exact hex values. Every category defines BOTH a primary accent AND a secondary accent (`--accent2`) — use `--accent2` for chart series #2, duotone gradients, comparison layouts, and the gradient-text polish technique:

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

`--accent-soft` and `--accent2-soft` are uniformly 14%-alpha derivatives of their respective accent colors — use them for icon backgrounds, soft fills, gradient tails, and chart area fills. `--border` is the palette-tinted hairline — use `var(--border)` for ALL card borders, dividers, and table rules instead of neutral gray `rgba(128,128,128,...)`, which reads muddy on tinted backgrounds. All three replace `color-mix()` and hardcoded rgba so palette swaps propagate automatically.

**Light-palette preference**: 10 of 13 categories use light backgrounds by default. When the user does not specify a visual tone (dark, moody, neon, etc.), **always use the category's palette as-is** — most will naturally be light. Only Finance/Markets, Creative/Design, and Technology/Engineering default to dark backgrounds; use them only when the content genuinely falls into those categories. Never darken a light-palette category on your own initiative.

**Accent fill strategy (accessibility + aesthetics)**:

The default fill pattern is `background:var(--accent-soft)`. The governing principle: **accent carries large text, icons, borders, and fills — small text belongs to `--text` or `--muted`.** What goes ON that fill:

- **Icon tiles and glyphs** (WCAG 3:1): always `color:var(--accent)` — every palette accent clears 3:1 against its own soft fill.
- **Small text on a soft fill** (buttons, pills, badges — below 18px; WCAG 4.5:1): use `color:var(--text)`. These accents are deliberately mid-tone, so `var(--accent)` on `var(--accent-soft)` reaches 4.5:1 in NO category — coloring the label accent is the most common contrast bug in this system. To keep the control reading as accent-led, add `border:1px solid var(--accent)` instead of tinting the text.
- **Solid accent fill** (`background:var(--accent)`): no one text color is safe everywhere — for Science, Technology, and Sports the accent clears 4.5:1 against neither white nor `--text`. Either set the label ≥18px and bold, which drops the bar to WCAG large-text 3:1 and every accent passes with `#fff` (light palettes) or `var(--bg)` (dark palettes), or keep small labels on the soft-fill pattern above.
- **Dark-background categories** (Finance, Creative, Technology): accent text on `--card`/`--bg` reads well for Finance and Creative. Technology's accent lands just under 4.5:1 on both, so give small labels `var(--text)` there and reserve the accent for headings, icons, and borders.

**Genre/subject clash escape hatch**: if the genre palette feels aesthetically wrong for the subject (e.g., a tech news digest on a paper-tone Editorial palette), you may swap ONLY the accent set (`--accent`, `--accent-soft`, `--accent2`, `--accent2-soft`) from the subject's row. `--bg`/`--card`/`--text`/`--muted`/`--border` MUST stay with the genre row — do not slide into the subject's full theme.

Inject via script (see the CSS mechanism table in Phase 2):
```javascript
(function(){var s=document.createElement('style');s.textContent=':root{--bg:BG;--card:CARD;--text:TEXT;--muted:MUTED;--accent:ACCENT;--accent-soft:ACCENT_SOFT;--accent2:ACCENT2;--accent2-soft:ACCENT2_SOFT;--border:BORDER}';document.head.appendChild(s)})();
```

---

### Icon & Visual Enrichment Strategy (CRITICAL)

Your visualizations need **visual richness** beyond just charts and text. Use this priority system:

**Priority 1: Real Images (for topics with real-world entities)**

If the topic involves real-world entities users would want to SEE (travel, landmarks, animals, artworks, food, architecture), you MAY attempt to include images — but ONLY if you have a verified embeddable URL:

- **Step A — User-supplied URLs:** image URLs explicitly provided by the user in THIS conversation. These are the most reliable.
- **Step B — `<uri>` tags from search results:** Some search results contain a `<uri>` tag inside `<image>` elements with an actual HTTP URL (e.g., `<uri>https://p3-doubao-search-sign.byteimg.com/...?lk3s=...&x-signature=...</uri>`). Extract and use ONLY these verbatim. **However: many search results return images as `<image reference_id="..."><pixel_size .../></image>` with NO `<uri>` tag — these are display references for the chat UI only and are NOT usable as `<img src>` in HTML.** If you see `reference_id` but no `<uri>`, that image is unavailable for HTML embedding.
- **Step B2 — generate one with `image_gen`, when A and B come up empty and the slot is decorative.** Two conditions gate this and both are hard. First, a renderer block can only load a picture over HTTP — base64 stays banned here because a data URI would stream through the output block, burning the token budget and risking a truncation that kills the whole artifact. So a generated image is usable only if `image_gen` hands back an HTTP URL; if all you get is a local file path, you cannot show it in a renderer block, so drop the slot and move on instead of hunting for a workaround. Second, generate only what a reader would never take as evidence: a hero backdrop, a section header, mood imagery for a travel or food piece, character art for a game. Never generate a specific person, a real building or place, a news event, or an actual product — that is fabrication in picture form, no different from inventing a statistic, and in factual content a generated image must be labeled as an illustration in its caption. Prompt for photographic or illustrative content only, naming the palette's accent color and the genre; image models render text, labels, charts, and logos as garbled nonsense, so never generate anything carrying type or data. `image_edit` may recrop or restyle a picture you already hold, but never change what a real photograph depicts. Budget one generated image for the slot that carries the page — generation costs a turn, and a streaming artifact is supposed to arrive fast.
- **No URL = No image.** If none of Step A, Step B, or Step B2 yields a usable image, **skip images entirely** — remove the image container from the layout. Do NOT substitute with an emoji, a gradient-box placeholder, or a "no image" icon. Do NOT recall URLs from memory (Wikipedia, Wikimedia, Unsplash, brand CDNs). Do NOT construct URLs that look like the byteimg signed format. A text-only card is infinitely better than a broken white box.

**Step C — CI validation (MANDATORY before embedding):** Before placing any image URL in your HTML, verify it in CI: `import requests; r = requests.get(url, stream=True, timeout=5); print(r.status_code); r.close()`. Using `stream=True` checks the status without downloading the full image. Only embed URLs that return `200`. If a URL returns 403/404/timeout, discard it and remove its `<img>` container from the layout. This catches truncated signatures, expired URLs, and fabricated paths before the user sees a broken image.

**Limitation of Step C — Referer-based hotlinking**: Official brand websites (e.g. `brand.com/assets/img/...`) often return 200 to direct requests (no Referer) but 403 to cross-origin requests from iframes. Step C CANNOT detect this. Therefore: **only URLs obtained via Step A, Step B, or Step B2 are eligible for embedding.** Do NOT guess file paths on official websites, even if CI returns 200 — they will fail in the renderer. If you cannot find a working `<uri>` from search results and Step B2 does not apply, skip images entirely.

**Do NOT re-search for failed images.** If CI validation shows a URL is inaccessible (403/404/timeout), simply discard it and remove the image slot from the layout. Do NOT launch additional searches trying to find an alternative image for the same topic — unless the user explicitly asks you to find a replacement. Repeated image-searching consumes context rapidly and often fails again for the same reasons (expired signatures, hotlink protection). One failed attempt = move on. The same ceiling applies to Step B2: one `image_gen` attempt per slot, and if what comes back is unusable or arrives as a local path, drop the slot rather than re-prompting for a better one. The layout should degrade gracefully without images (text-only cards, colored banners, SVG illustrations).

Rules for all `<img>` tags (when you DO have a verified URL that passed Step C):
- `onerror="this.style.display='none'"` (graceful hide on failure — backup for URLs that expire after validation)
- `alt` text, `loading="lazy"`, `style="max-width:100%;border-radius:12px"`
- **Use the FULL URL verbatim** including the ENTIRE query string. Signed URLs contain `?lk3s=...&x-expires=...&x-signature=...`. **Stripping or truncating query params = instant 403.**
- Do NOT download images, write to disk, or base64-embed — use the remote URL as `src`.
- If most images in a layout have no verified URL, redesign the layout WITHOUT image slots (e.g., use colored header banners, SVG illustrations, or gradient backgrounds instead).

**Priority 2: Inline SVG Icons (PREFERRED over emoji)**

For metric cards, section headers, and decorative elements, use **inline SVG icons**. Create simple 24x24 viewBox stroke-based icons that **depict the topic at hand** — do NOT stamp this handbook's sample icons, or any single icon, across every artifact. Authoring rules, the traps that make SVG render blank or black, and the icon sets worth borrowing geometry from are in [svg-guide.md](svg-guide.md); read it before hand-drawing anything more involved than these samples. Above roughly eight icons, switch to one icon library for the whole artifact (see the *Pinned CDN paths* table in SKILL.md) rather than mixing hand-drawn and library glyphs:

```html
<!-- Trend Up -->
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M23 6l-9.5 9.5-5-5L1 18"/><path d="M17 6h6v6"/></svg>
<!-- Chart -->
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10"/><path d="M12 20V4"/><path d="M6 20v-6"/></svg>
<!-- Globe -->
<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
```

**Emoji — TOTAL BAN (never a fallback)**

The full emoji ban — definition, common violations, and correct alternatives — is defined in *Absolute Ban: Zero Emoji in HTML Output* in SKILL.md. In short: never use emoji as icons, decorators, category markers, particles, or placeholders. Use inline SVG, plain glyphs (`●` `▲` `★` `■` `+` `−`) with CSS color, text labels, or CSS shapes instead.

---

### Visual Hierarchy System (MANDATORY for Game/Canvas-first/App archetypes)

Apply these three hierarchy layers to avoid the "everything looks the same" trap:

**Button hierarchy** — differentiate by visual weight:

| Level | Style pattern | Use for |
|-------|--------------|---------|
| **Primary** | Light-bg: `background:var(--accent-soft);color:var(--text);border:1px solid var(--accent)`. Dark-bg: `background:var(--accent);color:var(--bg)`. A solid accent fill needs a ≥18px bold label to stay legible — see Accent fill strategy. | Main action — one per view (Start, Submit, Play) |
| **Secondary** | `background:var(--card);border:1px solid var(--border);color:var(--text)` | Alternative actions (Reset, Load Example, Clear) |
| **Ghost** | `background:transparent;color:var(--muted)` | Toggles, minor controls (Pause, Settings) |

**Card elevation hierarchy** — not all containers should look alike:

| Level | Style | Content type |
|-------|-------|-------------|
| **Surface** | `border:1px solid var(--border)`, no shadow | Supporting info (explanations, footnotes) |
| **Raised** | border + `box-shadow:0 1px 3px rgba(0,0,0,.06)` | Standard content (controls, tables) |
| **Focal** | accent border + glow: `border-color:var(--accent);box-shadow:0 0 0 1px var(--accent),0 0 20px var(--accent-soft)` | Primary interactive zone (canvas, game board, main chart) |

Dark palettes: black shadows are nearly invisible on dark backgrounds — express **Raised** with a slightly lighter card background plus `var(--border)`; reserve the accent glow for **Focal** only.

**Spacing rhythm** — create visual chapters:
- Between major sections: `gap-12` / `mb-14` (breathing room)
- Within a card: `gap-4` / `mb-6` (tight grouping)
- Never use the same gap everywhere — uniform spacing = flat hierarchy.

**Typography rhythm** — line-height by role:

| Element | `line-height` | Why |
|---------|--------------|-----|
| Hero headings (`text-4xl`+) | `1.1 – 1.2` | Tight leading keeps large type punchy; multi-line wraps still breathe |
| Section headings (`text-xl` – `text-2xl`) | `1.25 – 1.35` | Slightly looser for comfortable scanning |
| Body / paragraph text | `1.6 – 1.8` | Optimal readability for continuous reading |
| Captions, labels, metadata (`text-xs` – `text-sm`) | `1.4 – 1.5` | Compact but not cramped |
| Table cells | `1.4` | Keeps rows tight; pair with vertical padding (`py-3`) for rhythm |

Never leave `line-height` at the browser default (typically 1.2) for body text — it looks cramped and unprofessional. Conversely, never use body-level `line-height` (1.7+) on headings — it creates excessive vertical gaps in multi-line titles.

**Using `--accent2`**: Every category in the Color Rotation System pre-defines a harmonious `--accent2` and `--accent2-soft`. Use `var(--accent2)` for: chart series #2, the second item in "A vs B" comparisons, duotone gradient text (Design Polish #5), and any secondary accent element. No need to pick your own — just use the pre-defined value from your category row.

---

### Design Polish Techniques (use 3–5 per artifact)

These elevate output from generic dashboards to professional quality. All CSS below goes inside your injected `<script>` style block.

**`color-mix()` policy**: The examples below use `color-mix(in srgb, ...)` for readability. The renderer targets evergreen Chromium (always latest stable) where `color-mix()` works. Use it freely in your output. If you ever need to support older WebViews, substitute with pre-computed `rgba()` values — but this is NOT the default concern.

**1. Background depth** — radial gradient bleed (best on dark palettes):
```html
<div style="background:radial-gradient(1200px 600px at 80% -10%, color-mix(in srgb, var(--accent) 10%, transparent), transparent 60%), var(--bg)">
```

**2. Subtle texture** — faint grid/dot pattern via `::before` pseudo-element with `pointer-events:none` and low opacity.

**3. Numbered sections** — monospace `01`-style section numbers with baseline-aligned flex (Dashboard/Report archetype only — see anti-convergence rules).

**4. Card hover effects** — `transition:transform .25s, border-color .25s` + `:hover{translateY(-3px)}` with accent-tinted border.

**5. Gradient text** in hero (use `var(--accent2)` as the second stop — it's defined for every category):
```html
<span style="background:linear-gradient(100deg,var(--accent),var(--accent2));-webkit-background-clip:text;background-clip:text;color:transparent">Highlighted Word</span>
```

**6. Monospace for data** — `font-variant-numeric:tabular-nums` on number containers for aligned columns.

**7. Eyebrow text** — small uppercase monospace label above headings (`font-size:11px;letter-spacing:.2em;text-transform:uppercase`). Default to `color:var(--muted)`, which clears 4.5:1 on `--bg` in every category. `color:var(--accent)` is only safe at this size for Finance, Creative, Education, Entertainment, History, Math, and News — the seven rows whose accent is dark enough. Combined with the 44px gradient icon it reconstitutes the banned Dashboard hero — avoid that pairing outside Dashboard.

**8. Custom CSS bars** — a track div (`height:28px;background:rgba(128,128,128,.06);border-radius:8px;overflow:hidden`) with an inner fill div at the data percentage width, using a gradient from `--accent`.

**9. Per-item accent colors** — define `--item-accent` per class (e.g. `.item-a{--item-accent:#ee4d2d}`) for multi-item comparisons.

**10. Status pills** — inline badge with `padding:2px 9px;border-radius:20px;background:var(--accent-soft);color:var(--text)`. Pill text is small, so it follows the soft-fill rule: `--text`, never `--accent`. Add `border:1px solid var(--accent)` if the pill needs more presence.

**11. Light-palette accents** — accent top-bar on key cards (`border-top:3px solid var(--accent)`) and soft radial wash behind the page:
```html
<div style="border-top:3px solid var(--accent);border-left:1px solid var(--border);border-right:1px solid var(--border);border-bottom:1px solid var(--border);border-radius:12px">
<div style="background:radial-gradient(800px 400px at 20% -10%, var(--accent-soft), transparent 70%), var(--bg)">
```

---

