---
name: pdf-skill
description: >-
  Use when the task involves PDF creation, conversion, extraction, merge/split,
  forms, or scanned-PDF handling. Delegates heavy toolchains to routes and
  scripts/pdf.sh; coordinate with doc/excel/pptx skills for non-PDF editing.
metadata:
  version: 1.0
---

# PDF Skill

## Responsibilities & collaboration

When used alongside other skills: the primary (non-PDF) editing is handled by the
corresponding skill, and this skill only performs the PDF-related steps.

### When NOT to use this skill

- You only need to render a PDF into thumbnails / page images for a **visual
  self-check** → use `artifact-preview`, not this skill.
- You only need a **deterministic structural / content check** on an existing
  deliverable (whether numbers, sections, placeholders exist, etc.) → use
  `verifier-hub`.
- The primary object being edited is an Office/LaTeX source document itself (edit
  it in place, no PDF output) → hand it to the corresponding Office/document skill.

## Route selection

| Route | Trigger | Route file |
|------|---------|---------|
| **Create** (default) | User asks to "write / generate / create" a PDF, with no Office/LaTeX attachment | `routes/create.md` |
| **Convert** | User provides a `.docx/.pptx/.xlsx/.tex` etc. attachment and asks for format conversion | `routes/convert.md` |
| **Process** | Operate on an existing PDF (read, extract, merge, split, fill forms, etc.) | `routes/process.md` |

### Mandatory: read the route file before implementing

<system-reminder>
Before implementing any feature, you MUST first read the corresponding route file.
The route file contains critical implementation details that are not repeated here.
Skipping this step leads to wrong output (incorrect script calls, missing CSS,
broken layout).
</system-reminder>

**Before implementing, you must:**
1. Decide the route (Create / Convert / Process)
2. **Read the route file** (`routes/create.md`, `routes/convert.md`, or `routes/process.md`)
3. **The Create route additionally requires reading** `design/design.md` (the design spec)
4. Only then start implementing

### Route decision rules

| User input | Route |
|---------|------|
| "Write a report", "Generate a PDF", "Create a document", "Make me a resume" | **Create** |
| Provided a `.docx/.pptx/.xlsx` attachment + "convert to PDF" | **Convert** |
| Provided a `.tex` file or said "compile LaTeX" | **Convert** |
| "Convert this PDF to Word" | **Convert** |
| "Extract the text from this PDF", "Merge these PDFs", "Fill in this form" | **Process** |
| "Read / open this PDF", "Take a look at this PDF for me", "Summarize this PDF" | **Process** |
| Provided a PDF + "re-typeset / beautify" | **Create** (first use the Process route to extract content, then the Create route to regenerate) |

**Priority**: Office/LaTeX attachment → Convert > PDF + operation instruction → Process > everything else → Create

---

## Quick start

**Use the unified CLI for all operations:**

```bash
# Check the environment (JSON output; exit code 0 = OK, 2 = missing dependency)
bash scripts/pdf.sh check --json

# Auto-fix missing dependencies: enable explicitly only when modifying global/user
# packages is allowed (training machines usually have them preinstalled; can skip)
PDF_SH_ALLOW_FIX=1 bash scripts/pdf.sh fix

# HTML to PDF
bash scripts/pdf.sh html input.html

# Compile LaTeX to PDF
bash scripts/pdf.sh latex input.tex

# PDF processing (via the Python CLI)
python3 scripts/pdf.py <command> <subcommand> [options]
```

Note: always use **`bash scripts/pdf.sh`** to avoid `./scripts/pdf.sh` failing when
the executable bit is not preserved inside the zip.

**Exit codes:**
- `0` = success
- `1` = usage error
- `2` = missing dependency, or refusal to run `fix` when `PDF_SH_ALLOW_FIX=1` is not set
- `3` = runtime error

**Per-route dependencies:**
- **Create route**: Node.js, Playwright, Chromium
- **Convert route**: LibreOffice (Office direction), Tectonic (LaTeX direction)
- **Process route**: Python 3, pikepdf, pdfplumber

**If `html_to_pdf.js` produces no output after running** (the most common issue):

```bash
cd scripts && npm install && npx playwright install chromium
```

---

## Core constraints (must follow)

### 0. Keep the HTML self-contained; avoid non-essential external resources

<system-reminder>
Some sandboxed / offline environments block outbound requests through the proxy
(e.g. a 407 error), which makes any externally-loaded resource render blank or hang.
Other environments allow egress. Because you cannot assume which one you are in, keep
the HTML as self-contained as possible:
- **Fonts**: always use system fonts (Georgia, Arial, Times New Roman, etc.; for
  non-Latin scripts add an installed fallback such as a Noto CJK font). Never load
  fonts from a CDN — `fonts.googleapis.com`, Adobe Fonts, or any
  `@import url('https://...')` font reference — so output is deterministic everywhere.
- **CSS/JS frameworks**: do not load arbitrary framework CDNs.
- **KaTeX and Mermaid are the only permitted CDN resources** (loaded from
  `cdn.jsdelivr.net`; see `routes/create.md`). They work only where the environment
  allows egress. If it is blocked, `html_to_pdf.js` now aborts with an explicit error
  instead of emitting a broken PDF — if you hit that, pre-render the formula/diagram to
  an image and embed it with `<img>`, or vendor the library locally.
</system-reminder>

### 1. Output language

**The output language must match the language of the user's query.** Default to English
when the query language is ambiguous.
- Write all body text, headings, captions, and references in the user's query language.
- If the user explicitly specifies a language, follow that choice.

### 2. Word-count and page-count constraints

| User requirement | Standard to apply |
|---------|---------|
| Explicit word count (e.g. "3000 words") | Within ±20%, i.e. 2400-3600 words |
| Explicit page count (e.g. "5 pages") | Exactly equal; the last page may be partial |
| Word-count range (e.g. "2000-3000 words") | Must fall within the range |
| No explicit requirement | Infer reasonably from the document type; prefer thorough over sparse |
| Lower-bound requirement (e.g. "no fewer than 5000 words") | No more than 2×, i.e. 5000-10000 words |

**Forbidden behavior:**
- Arbitrarily trimming content ("concise" is not an excuse)
- Padding page count with lots of bullet points (keep high information density)
- Exceeding the user's requirement by more than 2×

**Special case — resume**: default **1 page** unless the user says otherwise. Use
compact margins `margin: 1.5cm`.

### 3. Citation and search rules

#### Search before writing (no fabrication)

<system-reminder>
Do not write content involving statistics, research conclusions, or policies/regulations
without searching first.
Fabricating facts is strictly forbidden. When in doubt, you must search.
</system-reminder>

| Scenario | Search required? | Note |
|------|---------|------|
| Statistics, numbers | **Required** | e.g. "2024 employment rate" |
| Policies / regulations | **Required** | e.g. "startup subsidy policy" |
| Academic research, papers | **Required** | e.g. "effectiveness of a method" |
| Time-sensitive content | **Required** | information after the knowledge cutoff |
| **Uncertain facts** | **Required** | if you are not sure, search |
| Common knowledge | Not needed | e.g. "water boils at 100°C" |

**Search workflow:**
1. Identify the facts / data that need verification
2. Search authoritative sources
3. When search results are insufficient, **iterate the search** until you obtain reliable information
4. Cite the real sources in the references
5. **If repeated searches still fail, tell the user** rather than fabricating data

#### Citation format

| Situation | Format |
|---------|------|
| English document (default) | APA |
| User requests a specific style | Follow it (MLA, Chicago, IEEE, etc.) |
| Non-English document | Use that locale's standard academic citation style |

**Citations must be real**: every citation must have the correct author/institution
name, an accurate title, and a verifiable year and source. **Do not fabricate
references.**

#### Cross-references (must be clickable)

```html
As shown in <a href="#fig-1-1">Figure 1-1</a> ...
From <a href="#eq-2-1">Equation (2-1)</a> we obtain ...
See <a href="#sec3">Chapter 3</a> for details ...
```

### 4. Outline adherence (mandatory)

**When the user provides an outline:**
- **Strictly follow** the outline structure the user provided
- Section headings must match the outline (wording may be tweaked, but the hierarchy/order must not change)
- Do not add or remove sections arbitrarily
- If the outline has issues, **ask the user first** before changing it

**When the user provides no outline**, use the standard structure for the document type:
- **Academic paper**: IMRaD, or Introduction-Literature review-Methods-Results-Discussion-Conclusion
- **Business report**: conclusion-first (Executive summary → Detailed analysis → Recommendations)
- **Technical document**: Overview → Principles → Usage → Examples → FAQ
- **Coursework**: follow the structure required by the assignment

---

## Cover style selection

| Scenario | Style |
|------|------|
| Academic paper, thesis, formal coursework | **Minimal** (white background, centered, no decoration) |
| Report, proposal, business document | **Designed** (choose from `design/design.md`) |
| Unsure | Default to **Designed** — a plain text-only cover = mediocre |

**Core principle**: the cover background color is what separates "passable" from
"outstanding". See the cover patterns in `design/design.md`.

---

## Color recommendations

Choose a primary color based on the document content and industry:

| Scenario | Recommended palette |
|------|---------|
| Legal / compliance / finance | Deep navy `#1C3A5E`, charcoal `#2E3440`, slate gray `#3D4C5E` |
| Medical / health | Turquoise `#2A6B5A`, cool green `#3A7D6A` |
| Tech / engineering | Steel blue `#2D5F8A`, indigo `#3D4F8A` |
| Environmental / sustainability | Forest green `#2E5E3A`, olive green `#4A5E2A` |
| Creative / arts / culture | Wine red `#6B2A35`, plum purple `#5A2A6B`, terracotta `#8A3A2A` |
| Academic / research | Deep teal `#2A5A6B`, scholarly blue `#2A4A6B` |
| Corporate / neutral | Slate `#3D4A5A`, graphite `#444C56` |
| Luxury / premium | Warm black `#1A1208`, deep bronze `#4A3820` |

**Principle**: choose a color that is meaningful for the document's content, not the
default color for its type. Low-saturation, darker tones work best. When unsure,
pick a darker, more neutral color.

---

## Tech stack overview

| Route | Tool | Purpose |
|------|------|------|
| Create | Playwright + Paged.js | HTML → PDF rendering |
| Create | KaTeX, Mermaid | Math formulas, diagrams |
| Convert | LibreOffice | Office ↔ PDF conversion |
| Convert | Tectonic | LaTeX → PDF compilation |
| Process | pikepdf | Form filling, page operations, metadata |
| Process | pdfplumber | Text and table extraction |

> For the source, version, and license of third-party dependencies (including the
> bundled `scripts/paged.polyfill.js`), see [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
