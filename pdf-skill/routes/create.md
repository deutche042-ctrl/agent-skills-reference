# Create route: HTML → PDF

Create a professional PDF from scratch using HTML + Playwright + Paged.js.

**Before you start creating, you MUST read `design/design.md` to learn the design spec.**

## Table of contents

- Step 0: Check dependencies
- Step 1: Write the HTML
- Step 2: Design (see `design/design.md`)
- Step 3: Convert to PDF
- Important notes
- Troubleshooting

---

## Step 0: Check dependencies

Training images usually have Node.js / Playwright / Chromium preinstalled. First
**only check**; do not install packages directly:

```bash
bash scripts/pdf.sh check --json
```

Exit code `0` means the Create-route dependencies are complete and you can go straight
to Step 1 and write the HTML in parallel.

If the check reports missing dependencies: if this environment **allows** modifying
global/user packages, you may explicitly enable auto-install; otherwise use the
training image's preinstalled packages or contact the environment maintainer.

```bash
PDF_SH_ALLOW_FIX=1 bash scripts/pdf.sh fix
```

### Reading the check output (important — avoids wasted effort)

The field that matters is **`browser_usable`**, not the version-match field:

- `browser_usable: "ok"` or `"fallback"` → **you can render; go to Step 1.**
- A **Playwright ↔ Chromium version mismatch** (e.g. Playwright expects Chromium build
  1228 but only 1169 is installed), or a "version may not match Playwright" warning at
  render time, is **NOT a blocker**. `browser_helper.js` automatically falls back to any
  available Chromium and renders correctly. **Do not reinstall Chromium to force matching
  versions** — only act if rendering actually fails.
- If Playwright isn't in the skill's local `scripts/node_modules`, the script
  auto-discovers it in common locations (global npm root, and the npx cache
  `~/.npm/_npx/*/node_modules`). You normally **don't** need to set `NODE_PATH` by hand;
  only if discovery fails, set `PLAYWRIGHT_PATH` or `NODE_PATH` to Playwright's folder.
- Only `browser_usable: "missing"` (or `node` / `playwright` themselves missing) is a real
  blocker that needs an install.

---

## Step 1: Write the HTML

### Key rules

1. **Do not load Paged.js**: the conversion script injects it automatically; loading it again doubles the page count and breaks the layout
2. **Do not use CSS counters**: Paged.js is not compatible with CSS counters. Use `data-*` attributes or manual numbering
3. **Do not use JS charting libraries**: dynamically rendered JS libraries such as ECharts, Chart.js, D3.js, Plotly conflict with Paged.js pagination
4. **Do not load external font CDNs**: external font services such as Google Fonts and Adobe Fonts may be blocked by the proxy in a sandboxed/offline environment (407 error), causing the page to render blank. **Always use system fonts** so output is deterministic regardless of environment

### Charts and formulas

| Type | Approach | Note |
|------|------|------|
| Flowcharts, sequence diagrams, architecture diagrams | **Mermaid** | Renders to static SVG; must set `theme:'neutral'` |
| Data charts (bar/line/pie) | **`<img>` tag** | Pre-generate the image with matplotlib, then embed it |
| Math formulas | **KaTeX** | Inline with `\(...\)`, display with `\[...\]` |

**Chart-size rule**: always use a **landscape** ratio (width > height), e.g.
`figsize=(10, 6)`. Do not use square or portrait ratios, to avoid overflowing the page.

### Using Mermaid

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<script>mermaid.initialize({startOnLoad: true, theme: 'neutral'});</script>

<div class="mermaid">
graph TD
    A[Start] --> B{Decision}
    B -->|Yes| C[Execute]
    B -->|No| D[End]
</div>
```

### Using KaTeX

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.css">
<script src="https://cdn.jsdelivr.net/npm/katex/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex/dist/contrib/auto-render.min.js"
        onload="renderMathInElement(document.body)"></script>
```

> **Environment note**: KaTeX and Mermaid are fetched from `cdn.jsdelivr.net`, so they
> depend on the environment allowing outbound requests. Where egress is available this
> works with no extra setup. Where it is blocked, `html_to_pdf.js` aborts with an
> explicit error instead of exporting a PDF full of raw `$...$` / diagram source — in
> that case, pre-render the formula or diagram to an image (e.g. matplotlib or a static
> SVG) and embed it with `<img>`, or vendor the library locally.

---

## Step 2: Design (see design/design.md)

### Base page setup

```css
@page {
    size: A4;
    margin: 2.8cm 2.8cm 2.5cm 2.8cm;
    @bottom-center {
        content: counter(page);
        font-size: 9pt;
        color: #666;
    }
}
```

### CSS variables (unified design tokens)

Every document must define the following variables in `:root` to ensure consistency
throughout:

```css
:root {
    --accent: #2D5F8A;       /* Primary color; choose from the color-recommendation table */
    --accent-lt: #E8F0F8;    /* Light tint of the primary color, for alternating table rows */
    --bg-cover: #0F1F2E;     /* Cover background color */
    --text-cover: #F0EDE6;   /* Cover text color */
    --font-display: Georgia, 'Times New Roman', serif;  /* Cover/heading font (system fonts) */
    --font-body: Georgia, 'Times New Roman', serif;     /* Body font (system fonts) */
    --font-sans: Arial, Helvetica, sans-serif;          /* Sans-serif font (system fonts) */
    /* For non-Latin scripts (e.g. CJK), append a fallback, e.g.:
       --font-body: Georgia, 'Noto Serif CJK SC', 'Source Han Serif SC', serif; */
}
```

**Do not use `@import url('https://fonts.googleapis.com/...')`.** External fonts may be
unavailable in the sandbox; system fonts keep output deterministic.

### Cover structure

The cover must be its own page, separated from the body with `break-after: page`.

**Designed-style cover skeleton** (recommended for most scenarios):

```html
<div class="cover" style="
    background: var(--bg-cover);
    color: var(--text-cover);
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 4cm;
    break-after: page;
">
    <h1 style="font-family: var(--font-display); font-size: 36pt; line-height: 1.2; margin-bottom: 1cm;">
        Document Title
    </h1>
    <div style="width: 60px; height: 4px; background: var(--accent); margin-bottom: 1cm;"></div>
    <p style="font-size: 14pt; opacity: 0.8;">Author · Date</p>
</div>
```

**Minimal-style cover skeleton** (academic papers, etc.):

```html
<div class="cover" style="
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    break-after: page;
">
    <h1 style="font-size: 24pt; margin-bottom: 2cm;">Paper Title</h1>
    <p style="font-size: 14pt; color: #555;">Author Name</p>
    <p style="font-size: 12pt; color: #777;">Affiliation</p>
    <p style="font-size: 12pt; color: #777;">Date</p>
</div>
```

### Body typography

#### Academic style (default)

The default output should emulate a LaTeX academic-paper style, not a web/UI style.

**Forbidden UI components:**

| Forbidden | Alternative |
|------|---------|
| Card components (with border + header) | Three-line tables or plain paragraphs |
| Stat dashboards (grids of number cards) | Present data in a table |
| Dark heading bars | Bold headings + a thin rule or left border |
| Timeline components | Numbered lists or tables |
| Dark code blocks | Light-gray background `#f5f5f5` |
| Rounded borders | Square corners or no border |
| Shadow effects | No shadows |

#### Color standards

| Element | Color rule |
|------|---------|
| Body text | `#1a1a1a` (near pure black) |
| Section headings | `#000` or `var(--accent)` |
| Table borders | `#ddd` (light gray) |
| Table-header background | `var(--accent)` + white text |
| Alternating rows | `var(--accent-lt)` |
| Code background | `#f5f5f5` |
| Quote / callout box | 3px `var(--accent)` left border |

#### Three-line table

Tables in academic documents should use the three-line-table style:

```css
table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
    font-size: 10pt;
}
th {
    border-top: 2px solid #000;
    border-bottom: 1px solid #000;
    padding: 8px 12px;
    text-align: left;
    background: var(--accent);
    color: white;
}
td {
    padding: 6px 12px;
    border-bottom: 1px solid #eee;
}
tr:last-child td {
    border-bottom: 2px solid #000;
}
```

#### Theorem / definition box

```css
.theorem {
    border-left: 3px solid #333;
    padding-left: 1em;
    margin: 1em 0;
}
.theorem-title { font-weight: bold; }
.theorem-content { font-style: italic; }
```

#### Footnotes

```css
.footnote {
    font-size: 8pt;
    color: #666;
    border-top: 1px solid #ccc;
    padding-top: 0.5em;
    margin-top: 2em;
}
```

### Header/footer (using Paged.js string-set)

```css
h1 { string-set: chapter-title content(text); }

@page {
    @top-left {
        content: string(chapter-title);
        font-size: 9pt;
        color: #999;
    }
    @bottom-center {
        content: counter(page);
        font-size: 9pt;
    }
}

@page:first {
    @top-left { content: none; }
    @bottom-center { content: none; }
}
```

---

## Step 3: Convert to PDF

```bash
node scripts/html_to_pdf.js document.html
node scripts/html_to_pdf.js document.html --output output.pdf
```

After conversion the script reports:
- Page count, word-count stats, number of charts
- **Overflow detection**: warns if `pre`, `table`, `figure`, `img`, etc. exceed the page width
- **CSS counter detection**: warns if CSS counters are used (incompatible with Paged.js)
- Abnormal-page detection (blank pages, low-content pages)

If overflow is detected, add `max-width: 100%` to the overflowing elements.

---

## Important notes

### Body text & non-Latin script support

Set the body font stack with a comfortable line height and justified text. For non-Latin
scripts (e.g. CJK), append a matching fallback font to `--font-body` so glyphs render
instead of appearing as missing-glyph boxes:

```css
body {
    font-family: var(--font-body);
    line-height: 1.8;
    text-align: justify;
}
```

### Splitting long documents

For documents longer than 20 pages, split the content into multiple `<section>`
elements, one per chapter. This helps Paged.js paginate correctly.

### Handling images

- All images must set `max-width: 100%` to prevent overflow
- Use the `<figcaption>` tag for image captions
- Figure numbering format: `Figure <chapter>-<index>` (e.g. "Figure 3-1")

```html
<figure id="fig-3-1">
    <img src="chart.png" style="max-width: 100%;">
    <figcaption>Figure 3-1: Sample analysis results</figcaption>
</figure>
```

### References

Use APA format for English documents (for other languages, use that locale's standard style):

```html
<section class="references">
    <h2>References</h2>
    <ol>
        <li id="ref1">Author, A. A. (Year). Title of the article. Journal Name, Vol(Issue), pages.</li>
        <li id="ref2">Author, A. A. (Year). Book title. Publisher.</li>
    </ol>
</section>
```

---

## Troubleshooting

### Playwright / Chromium version mismatch (usually safe to ignore)

If `pdf.sh check` reports a mismatch (e.g. Playwright expects Chromium build 1228 but only
1169 is installed), or `html_to_pdf.js` prints "Using existing Chromium executable (version
may not match Playwright)", **this is expected and safe**: the script deliberately falls
back to whatever Chromium is available and renders normally. **No action needed** unless the
PDF actually fails to render — do not reinstall to force matching versions.

### `html_to_pdf.js` produces no output at all

**Cause**: Playwright cannot be located at all. Note the script already auto-discovers
Playwright in the global npm root and the npx cache (`~/.npm/_npx/*/node_modules`), so this
only happens when Playwright truly isn't installed anywhere (or `node` is missing).

**Fix** (only if auto-discovery failed):

```bash
cd /path/to/.skill/pdf-skill/scripts
npm install
npx playwright install chromium
```

Then re-run `node html_to_pdf.js document.html`. Alternatively, if Playwright is installed
elsewhere, point the script at it with `PLAYWRIGHT_PATH=/path/to/dir/containing/node_modules`
or `NODE_PATH`.

### The PDF content is blank

**Possible causes:**
1. The HTML uses an external font CDN (`@import url('https://fonts.googleapis.com/...')`), which may be blocked by the proxy → **remove all external font references and use system fonts**
2. The HTML manually loads Paged.js → **remove it; the script injects it automatically**
3. Paged.js pagination timed out → check whether the HTML structure is too complex

### Chromium fails to launch

**Fix**:

```bash
npx playwright install-deps chromium   # install system-level dependencies (needs root)
npx playwright install chromium         # reinstall Chromium
```

### Page overflow or truncation

Add the following for all images and tables in the HTML:

```css
img { max-width: 100%; height: auto; }
table { width: 100%; table-layout: fixed; word-wrap: break-word; }
pre { white-space: pre-wrap; word-wrap: break-word; overflow-x: hidden; }
```
