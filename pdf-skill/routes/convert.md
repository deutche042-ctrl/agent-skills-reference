# Convert route: format conversion

Handle conversion between Office documents and PDF, and compile LaTeX to PDF.

## Table of contents

- Route branches
- Branch A: Office → PDF
- Branch B: PDF → Office
- Branch C: LaTeX → PDF
- Script reference

---

## Route branches

| User scenario | Branch | Tool |
|---------|------|------|
| Provides `.docx/.pptx/.xlsx` etc. and asks to convert to PDF | **Office → PDF** | LibreOffice |
| Asks to convert a PDF to Word/PPT/Excel | **PDF → Office** | LibreOffice |
| Provides a `.tex` file or asks to compile LaTeX | **LaTeX → PDF** | Tectonic + `compile_latex.py` |

---

## Branch A: Office → PDF

### Dependencies

Requires LibreOffice. Check whether it is installed:

```bash
soffice --version
```

### Single-file conversion

```bash
python3 scripts/pdf.py convert input.docx -o output.pdf
```

### Batch conversion

```bash
soffice --headless --convert-to pdf --outdir ./output *.pptx *.docx *.xlsx
```

### Supported formats

`.docx`, `.doc`, `.odt`, `.rtf`, `.pptx`, `.ppt`, `.odp`, `.xlsx`, `.xls`, `.ods`, `.csv`, `.txt`, `.html`

### Notes

- Conversion preserves the original layout, formatting, and fonts (subject to system-font availability)
- Complex Office documents (e.g. PPTs with many charts) may convert with minor differences
- Missing fonts (especially for non-Latin scripts) may render as missing-glyph boxes; install the appropriate font package if needed

---

## Branch B: PDF → Office

### Reverse conversion with LibreOffice

```bash
# PDF to Word
soffice --headless --infilter="writer_pdf_import" --convert-to docx --outdir ./output input.pdf

# PDF to PPT (results depend on the PDF's content structure)
soffice --headless --convert-to pptx --outdir ./output input.pdf
```

### Limitations

- The quality of PDF → Office conversion depends on the PDF's internal structure
- Scanned PDFs (pure images) cannot be converted to editable documents
- Complex layouts (multi-column, floating images) may lose formatting
- Advise the user to review the result and adjust manually

---

## Branch C: LaTeX → PDF

### Step 1: Install Tectonic

The training image may already have `tectonic` preinstalled. If `tectonic --version` is
unavailable, use the installation method provided by your **distribution or team image**
(package manager, prebuilt binary, or internal artifact repository). **Do not** run
remote-pipe install scripts like `curl ... | sh` in the agent environment.

Reference: the official release page <https://github.com/tectonic-typesetting/tectonic/releases>
(downloaded, verified, and installed to PATH by an administrator).

### Step 2: Compile

You **must** compile with the `compile_latex.py` script. **Do not run tectonic directly.**

The script automatically:
- Filters out redundant package-download logs
- Filters out compile-progress messages
- Preserves all errors and warnings
- Shows PDF statistics (size, page count, word count, number of figures)

```bash
# Single compile
python3 scripts/compile_latex.py main.tex

# Multiple compiles (for cross-references and bibliography)
python3 scripts/compile_latex.py main.tex --runs 2

# Keep the full log (for debugging)
python3 scripts/compile_latex.py main.tex --keep-logs
```

### Step 3: Check and fix

After compiling, you **must check**:
- If there are errors, you **must fix** them and recompile
- If there are layout issues (overfull/underfull box), also try your best to fix them
- Use `--runs 2` to ensure cross-references and the table of contents are correct

### LaTeX authoring conventions

#### Document structure

```latex
\documentclass[12pt,a4paper]{article}
\usepackage{geometry}
\geometry{left=2.8cm, right=2.8cm, top=2.8cm, bottom=2.5cm}
% For CJK (Chinese/Japanese/Korean) content, also add: \usepackage[UTF8]{ctex}
\usepackage{hyperref}             % hyperref must be loaded last
\hypersetup{colorlinks=true, linkcolor=blue, citecolor=blue}

\begin{document}
% content
\end{document}
```

#### Key rules

- The `hyperref` package **must be loaded last** (after all other packages)
- For long documents, use `\input{}` to split into multiple .tex files
- The table of contents and references must be clickable (via hyperref)
- For CJK content, add the `ctex` package (or `xeCJK` when compiling with XeLaTeX)

---

## Script reference

| Script | Purpose |
|------|------|
| `pdf.py convert` | Office → PDF (calls LibreOffice) |
| `compile_latex.py` | LaTeX → PDF (calls Tectonic) |
| `pdf.sh latex` | Shell entry point for LaTeX compilation |
