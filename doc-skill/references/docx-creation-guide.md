# DOCX Creation Guide — Creating New Documents with `create_docx.py`

Create a brand-new, professionally typeset Word document from **Markdown text** using the Python script `scripts/create_docx.py`. You write Markdown; the script parses the structure and applies the typography automatically. **No intermediate JSON and no Node.js/`docx-js` are involved** — this is the single, recommended path for generating a `.docx` from scratch.

> Use this only when the user has **not** provided a template/source file. If the user gave you a `.docx` to modify, edit it in place instead — see `docx-editing-guide.md`.

## Workflow

1. Write the document content as Markdown and save it to a `.md` file (e.g. `content.md`).
2. Run `create_docx.py` with the appropriate `--style`.
3. `Read` the generated `.docx` once to sanity-check the formatting before delivery.

```bash
uv run scripts/create_docx.py content.md output.docx                  # general (default)
uv run scripts/create_docx.py content.md output.docx --style resume   # resume
uv run scripts/create_docx.py content.md output.docx --style patent   # patent
uv run scripts/create_docx.py content.md output.docx --style official # official document
```

From a sub-skill directory, call it via the relative path `../scripts/create_docx.py`.

## Styles

| `--style` | Use for | Key typography |
|---|---|---|
| `general` (default) | ordinary documents, reports, letters, visa support materials, explanatory docs | A4, 12pt body, bold headings, 2.5cm margins, 1.5 line spacing, first-line indent; Latin text Times New Roman/Arial, CJK falls back to 宋体/黑体; footer page numbers |
| `resume` | résumés / CVs | compact: 10pt body, 12/11/10.5pt headings, 1.15 line spacing, 1.8cm margins, **no** first-line indent, **no** header/footer |
| `patent` | patent claims / specification / abstract | detects the H1 headings `# 权利要求书` / `# 说明书` / `# 摘要` and splits them into independent Word sections, each with its own header and page numbers; ordered lists render as claim entries |
| `official` | official / government documents | GB/T 9704: 仿宋 (FangSong) size-three body, 黑体 (SimHei) size-two headings, official-document margins |

## Supported Markdown Elements

| Markdown | Result |
|---|---|
| `# ## ### ####` | Headings, levels 1–4 (mapped to Word heading styles) |
| plain text lines | Body paragraph (auto first-line indent, except in `resume`) |
| `- ` or `* ` | Unordered list (bulleted) |
| `1. ` `2. ` | Ordered list (continuous numbering; blank lines between items are merged into one group) |
| `\| col \| col \|` | Table (a `\|---\|---\|` separator row is skipped automatically) |
| ` ```lang … ``` ` | Code block (light-gray background, Courier New, line numbers) |
| `**bold**` | Bold run |
| `$formula$` | Inline OMML math formula (LaTeX syntax, e.g. `$\frac{a}{b}$`) |
| `$$formula$$` | Standalone centered OMML formula; may carry a trailing `(4-3)` number, or use `\tag{4-3}` |
| `---` | Visual separator (a **section break** in `patent` mode) |
| `![caption](url or local path)` | Image with a centered caption below it |

Formula and code details (LaTeX syntax reference, OMML support matrix) live in `docx-code-formula-guide.md`.

## Image Rules (important)

- Reference images with `![caption](url)` Markdown syntax.
- The script **downloads** remote HTTP/HTTPS images before embedding them — **do not** expect a bare image-host URL to render in Word; the script fetches the bytes and inserts them so the image survives.
- Local file paths (relative or absolute) are also supported.
- Image width is capped at 14 cm by default, with the caption centered beneath.
- On download failure the script inserts a gray placeholder `[Image failed to load: caption]` rather than crashing.

## Headers, Footers, and Page Numbers

Page numbering and headers are applied automatically per style: `general`, `official`, and `patent` documents get a centered footer page number (and `patent` also gets per-section headers); `resume` intentionally has none. You do not configure these manually — pick the right `--style`.

## Tips

- **Headings must use `#`/`##`/`###`**, not bold text, so Word recognizes them as real heading styles (needed for a table of contents and correct outline levels). Don't skip levels.
- **Never paste raw ` ``` ` fences or `$`/`$$` markup as ordinary body text** — write them as the Markdown elements above so the script converts them into real code blocks / OMML formulas. (See `docx-code-formula-guide.md`.)
- For bilingual output (e.g. visa materials), generate two separate `.md` files and produce two `.docx` files.
- Do not fake layout with blank lines, spaces, or tabs; the style presets handle spacing and indentation.

## Validation

After generating, `Read` the `.docx` once to confirm the content and formatting are correct. If anything is wrong, fix the Markdown and regenerate. For documents that must preserve an existing file's formatting, edit the original instead — see `docx-editing-guide.md`.
