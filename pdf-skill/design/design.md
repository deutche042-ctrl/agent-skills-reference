# Design System

The visual layer. Read this file before creating any PDF.
This file answers "what should it look like, and why designed this way".

## Table of contents

- Core principles
- Color logic
- Font system
- Cover design
- Inner-page typography rules
- Quality standards

---

## Core principles

Every design decision must be **rooted in the document's content and purpose**.

Deep teal on cream does not equal "professional". Serif on beige does not equal
"elegant". A color chosen because it **fits the content** always beats a color
chosen because it **looks safe**.

---

## Color logic

### Mood → base palette

| Content characteristics | Mood | Cover background | Primary color | Text color |
|---------|------|---------|--------|--------|
| Research, science, analysis | Authoritative | `#0F1F2E` deep ink-blue | `#00B4A6` teal-green | `#F0EDE6` warm white |
| Business, strategy, finance | Confident | `#1C1C2B` near-black | `#E8A020` amber | `#F5F2EC` cream |
| Creative, portfolio, design | Expressive | `#1A0A2E` deep purple | `#FF6B6B` coral red | `#FAF5FF` lavender white |
| Education, academic papers | Academic | `#FAFAF7` warm white | `#2C4A7C` navy | `#1A1A2E` dark |
| Medical, health | Calm | `#F5F9F8` pale mint | `#2D8B72` forest green | `#1E3830` deep green |
| Resume / personal | Clean | `#FFFFFF` white | pick from content | `#111111` near-black |
| Generic / unknown | Neutral | `#F8F6F1` warm off-white | `#3D3D3D` dark gray | `#1A1A1A` black |

### Primary-color selection rules

- **Use only one primary color.** Using two primary colors scatters the visual energy.
- Where the primary color appears: cover geometric elements, section-heading underlines,
  quote-box left border, table-header background, header rule. Nowhere else.
- The primary color must have a contrast ratio of at least 4.5:1 against the cover
  background (WCAG AA standard).
- **Do not default to blue.** Blue is the most overused primary color in AI-generated documents.

### Color anti-patterns (forbidden)

| Forbidden | Reason |
|------|------|
| White background with purple gradient | The classic AI aesthetic — instantly recognizable as generated |
| Navy + gold | An overused corporate cliché |
| All-black background | Prints poorly, visually aggressive |
| More than 3 colors in the system | Visual noise |
| Body text in the primary color | Hurts readability |

---

## Font system

### Font-pairing logic

**At most two fonts. Always.**

| Role | Criterion | Recommended choice |
|------|------|---------|
| Display font (cover title, H1) | Distinctive, high contrast, high weight | Times New Roman, Georgia (serif) |
| Body font (paragraphs, notes) | High readability at 10-11pt | Helvetica, Arial (sans-serif) |

**Do not use `@import url(...)` to load external fonts.** External requests may be blocked
by the proxy in some sandboxes; system fonts keep output deterministic everywhere.

### Cover font pairs by mood

| Mood | Display font (system) | Body font (system) |
|------|---------|---------|
| Authoritative | Georgia, 'Times New Roman', serif | Arial, Helvetica, sans-serif |
| Confident | 'Trebuchet MS', Verdana, sans-serif | Arial, sans-serif |
| Expressive | Georgia, serif | Verdana, sans-serif |
| Academic | 'Times New Roman', Georgia, serif | Arial, Helvetica, sans-serif |
| Clean | Georgia, serif | 'Segoe UI', Tahoma, sans-serif |
| Restrained | 'Palatino Linotype', 'Book Antiqua', serif | Verdana, sans-serif |
| Bold/rugged | 'Arial Narrow', Arial, sans-serif | Arial, sans-serif |
| Classical | 'Palatino Linotype', Georgia, serif | Georgia, serif |
| Editorial | Impact, 'Arial Black', sans-serif | Arial, Helvetica, sans-serif |

**Note**: all of the above are system fonts — no external CDN loading required. If the
document contains non-Latin scripts (e.g. CJK), append a matching fallback font to the
stack so those glyphs render (see "Non-Latin script support" in `routes/create.md`).

### Type scale

All sizes are in pt.

| Token | Size | Line height | Use |
|-------|------|------|------|
| display | 36-54pt | 1.0 | Cover title |
| h1 | 22pt | 1.3 | Section heading |
| h2 | 15pt | 1.4 | Sub-section heading |
| h3 | 11.5pt | 1.5 | Sub-sub-section |
| body | 10.5pt | 1.6 | Body text |
| caption | 8.5pt | 1.4 | Figure/table caption |
| meta | 8pt | 1.3 | Header/footer |

### Spacing scale

| Token | Value | Note |
|-------|-----|------|
| margin_outer | 2.8cm | Left/right page margin |
| margin_top | 2.8cm | Top margin |
| margin_bottom | 2.5cm | Bottom margin |
| section_gap | 26pt | Space before H1 |
| para_gap | 8pt | Space after a paragraph |
| line_gap | 17pt | Body line spacing |

---

## Cover design

The cover is the most important page. It determines whether the reader trusts the document.

### Six cover patterns

Choose a cover pattern based on the document type:

**1. `fullbleed`** — for: reports, general documents
- Dark background fills 100% of the page
- Title: large, left-aligned, in the top 60% of the page
- Primary color: thin horizontal rule + a color band in the top-right corner
- Dot-grid background texture (subtle, 8-10% opacity)
- Bottom bar: author + date

**2. `split`** — for: proposals, plans
- Left 42% panel: solid cover color, title + author
- Right 58%: off-white, dot-pattern decoration
- Primary-color vertical line as the divider
- No gradient — pure flat geometry

**3. `typographic`** — for: resumes, academic papers
- White / off-white background
- Title as oversized display type (60-80pt), left-aligned
- First word in the primary color, the rest in a dark color
- A thin rule below the title block

**4. `minimal`** — for: minimalist-style documents
- Near-white background, with only an 8px left vertical bar in the primary color
- Title in an extra-large, light-weight display font (300 weight)
- Hairline rule; author + date as a single line of gray text
- The vertical bar is the only visual element

**5. `frame`** — for: annual reports, legal documents, formal documents
- White / cream background, with an inset rectangular border (1.2px, 28px from the edge)
- Primary-color bands at the top and bottom inside the border; small primary-color corner squares
- Title centered inside the border, classical weight

**6. `editorial`** — for: magazine-style, creative documents
- Ghost-letter background (oversized semi-transparent letters)
- All-caps title
- Bold, rugged typographic style

### Cover CSS requirements

- Fixed canvas `width: 210mm; height: 297mm` (A4)
- `body { margin: 0; }`
- Use **inline SVG** for textures; do not use external `background-image: url()` links
- **Do not** use `@import url(...)` to load external fonts — use system fonts
- Use CSS variables for all colors

---

## Inner-page typography rules

### Section heading (H1)

- Primary-color 2px underline, 30-40% of the page width
- 26pt space above the heading
- Font size 22pt, bold

### Quote / callout box

- 3px left border in the primary color
- 1em left padding
- Background optionally a light tint of the primary color (5-8% opacity)

### Tables

- Header: primary-color background + white text
- Alternating rows: light tint of the primary color
- Borders: only top 2px, header-bottom 1px, last-row-bottom 2px (three-line table)

### Code blocks

- Background `#f5f5f5`
- 3px left border in the primary color
- Monospace font: `'Courier New', monospace`
- Font size 9pt

---

## Quality standards

| Check | Standard |
|--------|------|
| Cover | Must exist, must be full-page, must be separated from the body |
| Number of colors | No more than 3 colors in the system (primary + dark + light variant) |
| Number of fonts | No more than 2 fonts |
| Margins | Must not use defaults; must be set explicitly |
| Contrast | Body text vs. background contrast >= 7:1 |
| Print-friendly | Avoid large dark backgrounds (except the cover) |
