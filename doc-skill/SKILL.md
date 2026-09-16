---
name: doc-skill
description: "Manages document formatting standards and routes to sub-skills with strong formatting requirements. Sub-skills include resume writing and optimization, patent drafting/examination/response/portfolio, visa document filling and generation, and official document writing (litigation notices/legal announcements/meeting notices). Provides unified management of document typography standards (page/font/section/figures & tables/formulas) and the parsing and generation scripts for .docx/.doc files. Trigger conditions: the user mentions a Word/Office document, uploads a .docx/.doc file and wants to produce a file of the same type, mentions a resume/patent/visa document/complaint/announcement/meeting notice/official document, or needs to control the document output format."
version: doc_skill_V6_0321
---

# Document Formatting and Delivery Management

This Skill focuses on the formatting standards and delivery workflow of document deliverables, and also manages sub-skills with strong formatting requirements (resume, patent, visa documents).

## Routing Rules

Based on the user's intent, **route first, then read the corresponding sub-skill's SKILL.md, then execute**.

| User intent signal | Sub-skill path |
|---|---|
| Resume, CV, job-application materials; editing a resume, optimizing a resume, filling in a resume template | `resume-writing/SKILL_resume-writing.md` |
| Patent, claims, specification, technical disclosure, Office Action (OA), patent portfolio, FTO | `patent-writing/SKILL_patent-writing.md` |
| **When there is a clear intent to apply for a visa** and the request involves the materials required for a visa: visa application form, itinerary, invitation letter, employment/asset certificates and other supporting materials, filling in official visa forms (a cover letter, invitation letter, etc. do NOT take this route if they are unrelated to a visa) | `visa-doc-filler/SKILL_visa-doc-filler.md` |
| Complaint, statement of defense, summons, court notice, capital-reduction announcement, liquidation announcement, meeting notice, meeting minutes, official document | `official-document/SKILL_official-document.md` |
| **None of the above categories match**: general writing/typography needs such as novels, lesson plans, papers, ordinary Word documents, explanatory materials, reading notes, etc. | **Do not route to a sub-skill**; **base your judgment on the content the user provides** to first determine the appropriate genre/format (e.g. chaptered / lesson-plan / paper / report style), then produce an **adapted content framework (table of contents + key points/placeholders for each part)** |

### Execution Steps

1. **Identify intent**: match the user's need against the table above to determine the sub-skill
2. **Read the sub-skill**: use the Read tool to read the corresponding sub-skill's SKILL file
3. **Execute per the sub-skill**: handle the user's request strictly according to the workflow in the sub-skill

If none of the routes above match, handle the document need according to the general formatting and delivery standards below.

## 1. Deliverable Delivery Rules

- The user cannot directly see the thinking process or the deliverables produced during tool calls. Any non-canvas deliverable that the user needs to view must be pushed using the **NotifyHuman** tool.
- After generating a file with a file-creation tool (such as `Write`), you **must** call NotifyHuman to pass the file path or content to the user.
- **Exception**: when the deliverable is created via `CanvasCreateFile`, you are **forbidden** to call NotifyHuman again—content created by CanvasCreateFile is automatically shown to the user based on its canvas_id.
- NotifyHuman is only used to deliver file paths inside the VM and deliverable links returned by tools other than CanvasCreateFile.

## 2. Default Typography Standards (used when the user provides no template)

Output should primarily be "plain text / Markdown structure that can be pasted directly into Word":

- **Paper**: A4 (use US Letter where that is the local standard)
- **Margins**: ~2.5 cm (≈1 inch) on all sides
- **Body text**: 11–12pt, a serif (Times New Roman / Georgia) or clean sans-serif (Calibri / Arial), 1.5 line spacing, left-aligned or justified. Separate paragraphs with a space before/after, or a first-line indent (~0.5" for academic prose) — never fake it with blank lines, spaces, or Tabs. For CJK content the generator automatically falls back to 宋体 (SimSun) body / 黑体 (SimHei) headings.
- **Level-1 heading**: bold, ~15–16pt, centered or left-aligned
- **Level-2 heading (1.1)**: bold, ~14pt
- **Level-3 heading (1.1.1)**: bold, ~12pt
- **Section numbering**: use "Chapter 1 / Chapter 2 …" (or "1 Introduction, 2 …") for the top level; "1.1", "1.2" for level 2; "1.1.1" for level 3 — consistent throughout
- **Heading levels**: do not skip levels
- **Figures/tables and formulas**: figure captions go below the figure, table captions go above the table; figures, tables, and formulas must be numbered and referenced in the body text (e.g. "see Figure 2-1", "as shown in Equation (3-2)")

- **Header/footer/page number**: when the user's need is a formal document such as a paper/report/resume/patent/official document, or the user explicitly requests "headers and footers / page numbers", you must configure the header and footer and insert page numbers (commonly "centered or bottom-right page number", and when necessary including "Page X of Y"). If there are different sections such as a cover, table of contents, and body text, use "section breaks" to separately control things like hiding the header/footer on the first page, Roman numerals for the table-of-contents page numbers, and Arabic numerals for the body text (per the user's requirements).
- **Paragraph formatting**: pay particular attention to paragraph separation (a first-line indent or space before/after), justification, line spacing (e.g. 1.5), spacing before/after paragraphs (avoid faking it with blank lines), and pagination-related options such as "widow/orphan control / keep with next / keep lines together". Avoid unstable layout practices such as "faking a first-line indent with spaces/Tab" or "creating inter-paragraph spacing with carriage returns".
- **Heading levels and table of contents**: headings must use the "Heading 1/2/3 …" styles by level (or equivalent styles recognizable by the table of contents); they must not be simulated with bold/font size alone. If a table of contents needs to be exported, you must confirm that the **level range** of the generated TOC (e.g. levels 1–3) matches the user's expectation, and that heading levels do not skip. If the user has special heading-style requirements (font/size/numbering rules/centering/indent, etc.), make the corresponding modifications on top of the default heading format, rather than manually changing just one spot in the body text and causing inconsistency throughout.
- **Spacing between headings and body text (when there are chapter/section/article headings)**: there must be **appropriate spacing before/after** between a heading and the body text following it, to avoid "the heading being too close to the body text". It is recommended to control this uniformly with styles: set "space after" on the heading and "space before = 0" on the body text, consistent throughout; do not create blank space with multiple carriage returns.

## 2.1 Content Formatting Constraints (Mandatory)

All output must strictly follow the rules below and must not produce a format that "exposes raw markup symbols to the user":

### Code

**When outputting a .docx file (mandatory):** never let raw ` ``` ` code fences survive as literal text in a docx paragraph. Use whichever of the two supported paths matches how you are generating the file:

- **Option 1 — `create_docx.py` (Markdown → docx, recommended):** just write a normal fenced code block (open with ` ```python `, then the code, then ` ``` `) in the Markdown source. The script detects it and renders a gray code block automatically — you do **not** call any function yourself.
- **Option 2 — hand-written python-docx:** when generating a docx programmatically, it is **forbidden** to write the ` ```python ` triple backticks into a paragraph (they are not rendered and will be exposed as literal symbols). You must call `add_code_block(doc, code, lang)` from `scripts/code_formula.py`:

```python
# import at the top of the script
import sys; sys.path.insert(0, "path/to/scripts")
from code_formula import add_code_block, add_inline_formula, add_latex_formula

add_code_block(doc, code_str, lang="python")   # lang affects the label display
```

Either way: comment lines starting with `#` must stay inside the code block (never split into ordinary paragraphs or treated as headings). Rendered effect: uniform light-gray background (`#F2F2F2`), Courier New 9pt, line numbers, no divider lines, Word/WPS compatible. For detailed usage see `references/docx-code-formula-guide.md`.

**When outputting chat text:**
- All code snippets must be wrapped in triple-backtick code blocks with the programming language noted
- It is forbidden to output code as ordinary paragraph text, and forbidden to omit the language tag


### Formulas

**When outputting chat text:**
- Do not use `$$...$$` or `$...$` LaTeX syntax—it will be exposed as literal symbols
- Inline formulas: write directly with Unicode math symbols, e.g. `M = U × Σ × Vᵀ`
- Block-level formulas: on their own line, written clearly with natural mathematical expression

**When outputting a .docx file (mandatory):**

**Option 1: Use `create_docx.py` (Markdown → docx, recommended)**

`create_docx.py` already natively supports LaTeX formula syntax; **just write it directly in the Markdown text** and the script automatically converts it to Word OMML formulas:

- **Inline formula**: wrap LaTeX in `$...$`, mixed with the body text, automatically converted to an inline OMML math formula

```markdown
Note that the phase velocity $c = \frac{\omega}{k} = \sqrt{\frac{g\tanh(kh)}{k}}$, substitute it into the equation above and simplify.
```

- **Standalone centered formula** (may include a number): use `$$...$$` on its own line, with the number written in parentheses at the end of the line

```markdown
$$C_g = \frac{c}{2}\left[1 + \frac{2kh}{\sinh(2kh)}\right]$$ (4-3)
```

**Option 2: Call directly from a Python script (`add_inline_formula` / `add_latex_formula`)**

When generating a docx programmatically with python-docx, it is **forbidden** to write `$$`/`$` LaTeX strings directly into a paragraph (they are just plain text and will not be rendered); you must call:

- **Inline formula within a paragraph** (mixed with the body text): do not paste the formula as ordinary body text. Examples: `E = mc^2`, `\int_a^b f(x)\,dx`. Call `add_inline_formula(para, text)`, Times New Roman italic, matching the surrounding body-text size

```python
p = doc.add_paragraph("The standard deviation of the Gaussian function is ")
add_inline_formula(p, "σ")
p.add_run(", the discretization formula is shown in Equation (4-2).")
```

- **Standalone displayed formula** (numbered, centered): call `add_latex_formula(doc, latex, label)`, which generates a native Word OMML formula (supporting complex structures such as fractions, superscripts/subscripts, radicals, summations, etc.)

```python
add_latex_formula(doc, r"\frac{1}{2\pi\sigma^2} e^{-\frac{x^2}{2\sigma^2}}", label="(4-1)")
```

For the complete LaTeX syntax reference and implementation notes, see: `references/docx-code-formula-guide.md` → Sections 2 and 3

### Bold
- Always use the `**text**` Markdown syntax for bold; do not mix extra spaces inside or outside the `**`
- Correct: `**keyword**`; incorrect: `** keyword **` or `**keyword **`
- In the final text output, the `**` symbols must appear in pairs; a single `*` or an unclosed `**` must not appear

### No raw HTML tags or entities (mandatory for the docx path)

In the Markdown source you feed to `create_docx.py`, the **only** special markup is
`**bold**`, `*italic*`, `$inline formula$`, and `$$block formula$$`. Everything else must
be plain Markdown:

- **Never write HTML tags** such as `<br>`, `<center>`, `<b>`, `<p>`, `<div>`, `<span>`, or
  `<font>`. For a line break, end the paragraph and start a new one (a blank line); for
  centering, rely on the style/heading defaults. Raw tags render as literal, broken text.
- **Never write HTML entities** such as `&nbsp;`, `&amp;`, `&lt;`, `&gt;`. Type the real
  character (a normal space, `&`, `<`, `>`).
- **Do not emit JSON/dict-looking blobs** as body content; render structured data as a
  Markdown table or prose.

`create_docx.py` now defensively strips these artifacts as a safety net, but you must not
rely on it — write clean Markdown so the output is correct even if the safety net changes.

## 2.2 Length and Page-Count Discipline (Mandatory)

When the user states a length, **budget before you write, then verify after generating.**
Do not write freely and hope — over/under-length output is a common, avoidable failure.

| User requirement | Standard to apply |
|---|---|
| Explicit word/character count (e.g. "2,500 words", "3000자", "约3000字") | within **±10%** |
| A range (e.g. "2,000–3,000 words") | must fall inside the range |
| Explicit page count (e.g. "3 pages") | budget by words-per-page, then **verify by rendering to PDF** |
| Lower bound (e.g. "at least 5,000 words") | no more than **2×** |
| No explicit requirement | infer from the document type; prefer substance over padding |

**Forbidden**: padding to hit a length (filler sentences, bullet spam, repeating the same
recommendation across sections), and arbitrarily trimming required content ("concise" is
not an excuse to drop requested sections).

**Budgeting a page target → word/char budget** (rough, for planning the first draft):

| Style | English ≈ words/page | CJK ≈ chars/page |
|---|---|---|
| general / patent | 350–450 | ~750 |
| resume | ~550 | ~1000 |
| official (GB/T 9704) | ~350 | ~620 |

So "3 pages, general" ≈ 1,100–1,300 English words (or ~2,200 CJK chars). Tables, images,
and headings take space, so budget on the lower side when the document is chart/table-heavy.

**Verify after generating (do not skip):**
- `create_docx.py` prints a length report (`Length: … words | … chars`) and an estimated
  page count. Pass the user's target so it checks for you:
  ```bash
  uv run scripts/create_docx.py content.md out.docx --target-words 2500
  uv run scripts/create_docx.py content.md out.docx --target-chars 3000   # CJK/Thai targets
  uv run scripts/create_docx.py content.md out.docx --target-pages 3
  ```
  If it prints a `LENGTH WARNING`, fix it efficiently as below (do not skip).
- The page estimate is approximate. When an **exact page count** matters, render the file
  with `scripts/docx_to_pdf.py` and count the PDF pages, then adjust.

**If the length is off, fix it efficiently — do NOT nibble:**

- **Aim low from the first draft.** Draft in the lower half of the allowed range (models tend
  to over-write); expanding a short draft is cheap, repeatedly trimming a long one is slow.
- **Revise in ONE decisive pass.** From the report, compute the gap (e.g. 3,100 vs 2,500 =
  cut ~600 words), spread it across sections, and **rewrite** those sections to their new
  budget in a single edit — cut redundancy and verbose phrasing, never required sections or
  data. A full rewrite is also a real change (a near-identical rewrite makes the file tool
  report "no change" and wastes a turn).
- **Stop after at most 3 revision attempts.** If the length is still outside the target after
  the third revision, **stop and deliver the closest version** instead of looping further.
  Tell the user the final count and that it is slightly outside the requested length (e.g.
  "≈2,780 words, about 11% over the 2,500 target") so they can decide. A bounded, honest
  result beats making the user wait through an endless trim loop.

## 3. Delivery Acceptance (Mandatory)

Before the final output, do a "coverage check":

- **The plan is not lost**: every analysis dimension promised/planned during the process must appear in the final deliverable
- **The deliverable can be opened**: the delivered file must be openable by the target application; do not deliver only an outline or a faked format
- **Interactions work**: if delivering a web page/interactive report, you must click through each key interaction to verify it works
- **Sources must be output** (research/report deliverables only): when the deliverable draws on external sources, include a "References and Sources" section. This does not apply to documents with no external citations such as résumés, visa forms, letters, or official notices.
- **Key data must be attributed** (research/report deliverables only): in reports and data summaries, key numbers, conclusions, and figures/tables must carry a source reference in place.

## 4. Rich Media and Layout Quality (Mandatory)

When the deliverable includes visualization/document typography:

- **Avoid overlap and overflow**: use safe margins and grid alignment; avoid absolute positioning that causes text overlap
- **Fonts and color scheme**: avoid low-contrast color schemes for covers and titles; use a stable font-size gradient for body text
- **Chart readability**: labels are clear and not blurry; avoid oversized charts crowding the page; merge repeated information
- **Text-image consistency**: images must match their corresponding objects; when a match cannot be confirmed, mark them as illustrative

## 5. Document Operation Scripts

All general-purpose scripts are located in the `scripts/` directory; sub-skills can call them via the relative path `../scripts/`.

### 5.1 docx_edit.py — Word unpack/pack/replace

Modify content in an existing .docx while preserving the original formatting. Supports three operations: unpack to an XML directory, pack back to a .docx, and one-step text replacement. The replace mode supports matching text spliced across `<w:r>` runs, with optional track changes.

```bash
uv run scripts/docx_edit.py unpack template.docx unpacked/
uv run scripts/docx_edit.py pack unpacked/ output.docx
uv run scripts/docx_edit.py replace source.docx output.docx replacements.json
```

replacements.json format:
```json
{
  "replacements": [
    {"find": "{{placeholder}}", "replace": "replacement content"}
  ],
  "track_changes": false,
  "author": "assistant"
}
```

### 5.2 create_docx.py — Markdown → .docx generator

Generate a standard-typography Word document directly from Markdown text. **The model outputs Markdown text directly, writes it to a .md file, and the script automatically parses the structure and applies typography—no intermediate JSON format is needed.** Use this only when the user has not provided a template/source file.

Supported Markdown elements: `# ## ### ####` headings, body paragraphs, `- *` unordered lists, `1.` ordered lists, `| |` tables, ` ``` ` code blocks, `**bold**`, `$formula$` inline OMML formulas, `$$formula$$` standalone centered OMML formulas (may include `(number)`), `---` visual separator (a section break in patent mode), `![caption](url or local path)` images.

Four styles:
- `general` (default): general document (A4, 12pt body / bold headings, 2.5cm margins, 1.5 line spacing; Latin text in Times New Roman/Arial, CJK content falls back to 宋体/黑体)
- `resume`: resume (compact layout, 10pt body, 12/11/10.5pt headings, 1.15 line spacing, 1.8cm margins, no first-line indent, no header/footer)
- `patent`: patent document—automatically detects the H1 headings `# Claims` / `# Specification` / `# Abstract` (or their Chinese equivalents `# 权利要求书` / `# 说明书` / `# 摘要`) and splits them into independent Word Sections (each with its own header and page numbers); ordered lists are rendered in claims format
- `official`: official document (GB/T 9704: 仿宋 (FangSong) size-three body text, 黑体 (SimHei) size-two headings, official-document margins)

```bash
uv run scripts/create_docx.py content.md output.docx                  # general
uv run scripts/create_docx.py content.md output.docx --style resume   # resume
uv run scripts/create_docx.py content.md output.docx --style patent   # patent
uv run scripts/create_docx.py content.md output.docx --style official # official document
```

After generation the script prints a **length report** (word count, non-space character
count, and an estimated page count). When the user specified a length, pass the target so
the script checks it and warns if the output is out of range (see §2.2):

```bash
uv run scripts/create_docx.py content.md output.docx --target-words 2500   # ±10% by default
uv run scripts/create_docx.py content.md output.docx --target-chars 3000   # CJK/Thai targets
uv run scripts/create_docx.py content.md output.docx --target-pages 3      # estimate; verify via PDF
```

**Image insertion rules (important):**
- Use the `![caption](url)` syntax in Markdown to reference an image
- The script automatically downloads a remote image (HTTP/HTTPS) before inserting it into the docx. **Do not write an image-host URL directly**—image-host links often have expiration limits and cannot be displayed in Word after being inserted directly
- Local file paths are also supported (relative or absolute)
- The image width is limited to 14 cm by default, and the caption is centered below the image
- On download failure, gray placeholder text `[Image failed to load: caption]` is automatically inserted

### 5.3 code_formula.py — Code block and formula insertion (python-docx library)

Imported and called when generating a .docx; provides three APIs:
- `add_code_block(doc, code, lang)` — light-gray-background code block (Courier New 9pt, with line numbers, no border)
- `add_inline_formula(para, text)` — inline formula within a paragraph (Times New Roman italic)
- `add_latex_formula(doc, latex, label)` — LaTeX → native Word OMML formula (supports fractions, superscripts/subscripts, radicals)

For detailed usage see `references/docx-code-formula-guide.md`.

## 6. Reference Documents (read when needed)

| File | Content |
|------|------|
| `references/docx-editing-guide.md` | The complete operation guide for unpack → edit XML → repack, including notes on space handling (xml:space), image insertion, smart-quote escaping, etc. |
| `references/docx-creation-guide.md` | Guide for creating a .docx from scratch with `create_docx.py` (Markdown → docx): the four styles, supported Markdown elements, images, formulas, page setup, etc. |
| `references/docx-code-formula-guide.md` | The python-docx implementation spec for code blocks and formulas: parameter descriptions and examples for `add_code_block`, `add_inline_formula`, `add_latex_formula` |

## 7. Delivery Check

— **Check with Read before delivery (important):** before delivery you must call Read once more to view the complete doc file and check for formatting errors; if any exist, you must fix them by regenerating the file
- Deliver both the original Markdown and the Word file
- If the user wants Word, deliver `docx` or a format that can be explicitly exported
- Feature-list lock-in: if the user requests interactive capabilities such as collapse/expand, toggle, or filter, they must be included in the delivery checklist and verified item by item in the final deliverable; when they cannot be done, explain the limitations and alternatives in advance

## Sub-skill Directory

```
doc-skill/
├── SKILL.md                     # this file (formatting and delivery entry point)
├── resume-writing/              # resume writing and optimization
│   ├── SKILL_resume-writing.md
│   ├── scripts/
│   └── references/
├── patent-writing/              # patent drafting, examination, response, portfolio
│   ├── SKILL_patent-writing.md
│   └── references/
├── visa-doc-filler/             # visa document filling and generation
│   ├── SKILL_visa-doc-filler.md
│   ├── scripts/
│   └── references/
├── official-document/           # official document writing (litigation notices/legal announcements/meeting notices)
│   ├── SKILL_official-document.md
│   └── references/
├── scripts/                     # general document operation scripts
└── references/                  # general reference documents
```
