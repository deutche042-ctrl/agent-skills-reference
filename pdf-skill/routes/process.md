# Process route: operate on an existing PDF

Process an existing PDF file using the Python CLI tools (pikepdf + pdfplumber).

## Table of contents

- Step 0: Check dependencies
- Command reference
- Output format
- Exit codes
- Form-filling workflow
- Reading PDF content
- Text and table extraction
- Page operations
- Metadata operations
- Script reference
- Tech stack
- Important notes

---

## Step 0: Check dependencies

**Check the environment before using the pdf.py commands:**

```bash
bash scripts/pdf.sh check --json
```

This check only reports status; it does not auto-install. The Process route requires
`python3`, `pikepdf`, `pdfplumber`; training images usually have them preinstalled. If
they are missing and this environment allows installing packages, then explicitly run
`PDF_SH_ALLOW_FIX=1 bash scripts/pdf.sh fix`; otherwise contact the environment maintainer.

---

## Command reference

```
python3 scripts/pdf.py <command> <subcommand> [options]
```

| Command | Description |
|------|------|
| `form info <pdf>` | Inspect form fields |
| `form fill <pdf> -o <output> -d <json>` | Fill form fields |
| `extract text <pdf> [-p pages]` | Extract text |
| `extract table <pdf> [-p pages]` | Extract tables |
| `extract image <pdf> -o <dir>` | Extract images |
| `pages merge <pdf>... -o <output>` | Merge PDFs |
| `pages split <pdf> -o <dir>` | Split into single pages |
| `pages rotate <pdf> <90\|180\|270> -o <output>` | Rotate pages |
| `pages crop <pdf> <left,bottom,right,top> -o <output>` | Crop pages |
| `meta get <pdf>` | Read metadata |
| `meta set <pdf> -o <output> -d <json>` | Set metadata |

## Output format

All commands output JSON:

```json
// success
{"status": "success", "data": {...}}

// error (written to stderr)
{"status": "error", "error": "error type", "message": "description", "hint": "suggestion"}
```

## Exit codes

| Exit code | Meaning |
|--------|------|
| 0 | Success |
| 1 | Argument error |
| 2 | File not found |
| 3 | PDF parse error |
| 4 | Operation failed |

---

## Form-filling workflow

**Step 1: Inspect the form fields**

```bash
python3 scripts/pdf.py form info input.pdf
```

Example output:

```json
{
  "status": "success",
  "data": {
    "has_fields": true,
    "count": 5,
    "fields": [
      {"id": "name", "type": "text", "page": 1},
      {"id": "agree", "type": "checkbox", "states": ["/Yes", "/Off"], "checked_value": "/Yes", "page": 1},
      {"id": "country", "type": "dropdown", "options": [{"value": "US", "label": "US"}, {"value": "CN", "label": "CN"}], "page": 1}
    ]
  }
}
```

**Step 2: Fill the form**

```bash
python3 scripts/pdf.py form fill input.pdf -o output.pdf -d '{"name": "John Doe", "agree": "true", "country": "CN"}'
```

### Field-value rules

| Field type | Value format | Example |
|---------|--------|------|
| text | any string | `"name": "John Doe"` |
| checkbox | `"true"` or `"false"` | `"agree": "true"` |
| radio | one of the option values | `"gender": "/Choice1"` |
| dropdown | one of the option values | `"country": "CN"` |

**Important**: checkbox fields use the string values `"true"` or `"false"`. The script
automatically converts them to the correct PDF values (`/Yes`, `/On`, `/Off`, etc.).

---

## Reading PDF content

When the user asks to "read / open a PDF", "take a look at this PDF for me", or
"summarize the PDF content", use the `extract text` command to extract the text.

**Recommended workflow:**

```bash
# Step 1: extract the full text
python3 scripts/pdf.py extract text document.pdf

# If the document is long (>20 pages), extract page ranges to avoid output truncation
python3 scripts/pdf.py extract text document.pdf -p 1-10
python3 scripts/pdf.py extract text document.pdf -p 11-20
```

**Check the `likely_scanned` and `warning` fields in the returned result:**

| Returned field | Meaning | How to handle |
|---------|------|---------|
| No `warning` | Normal extraction | Use the extracted text directly |
| `likely_scanned: true` + `total_chars: 0` | Pure scanned/image PDF | **Take the image path**: export each page as an image → base64 → pass to the model's vision capability |
| `likely_scanned: true` + a little text | Partially scanned or mostly images | Return the extracted text, and for text-sparse pages supplement via the image path |

**Workflow for a pure-image PDF:**

```bash
# 1. Export each page as an image
python3 scripts/pdf.py extract image document.pdf -o ./page_images/

# 2. Convert the images to base64 (Python example)
import base64, pathlib
for img in sorted(pathlib.Path("./page_images").iterdir()):
    b64 = base64.b64encode(img.read_bytes()).decode()
    # 3. Pass b64 as an image message to the model; the model's vision capability recognizes the content
```

After passing each page as base64 to the model, the model can recognize text, tables,
charts, and other content — no external OCR tool required.

---

## Text and table extraction

**Extract text:**

```bash
python3 scripts/pdf.py extract text document.pdf
python3 scripts/pdf.py extract text document.pdf -p 1-3    # pages 1-3 only
python3 scripts/pdf.py extract text document.pdf -p 1,3,5  # specific pages
```

**Extract tables:**

```bash
python3 scripts/pdf.py extract table document.pdf
```

The output contains structured table data:

```json
{
  "total_pages": 10,
  "extracted_pages": 10,
  "total_tables": 3,
  "tables": [
    {
      "page": 1,
      "table_index": 0,
      "rows": 5,
      "cols": 3,
      "data": [["Header1", "Header2", "Header3"], ["A", "B", "C"]]
    }
  ]
}
```

---

## Page operations

**Merge PDFs:**

```bash
python3 scripts/pdf.py pages merge a.pdf b.pdf c.pdf -o merged.pdf
```

**Split a PDF:**

```bash
python3 scripts/pdf.py pages split document.pdf -o ./output_dir/
```

**Rotate pages:**

```bash
python3 scripts/pdf.py pages rotate document.pdf 90 -o rotated.pdf
python3 scripts/pdf.py pages rotate document.pdf 180 -o rotated.pdf -p 1-3  # specific pages
```

**Crop pages:**

```bash
python3 scripts/pdf.py pages crop document.pdf 50,50,550,750 -o cropped.pdf
```

Box format: `left,bottom,right,top`, in points (1 inch = 72 points).

---

## Metadata operations

**Read metadata:**

```bash
python3 scripts/pdf.py meta get document.pdf
```

**Set metadata:**

```bash
python3 scripts/pdf.py meta set document.pdf -o output.pdf -d '{"Title": "My Document", "Author": "John Doe"}'
```

Supported fields: `Title`, `Author`, `Subject`, `Keywords`, `Creator`, `Producer`

---

## Script reference

| Script | Purpose |
|------|------|
| `pdf.py` | Unified CLI entry point |
| `cmd_form.py` | Form inspection and filling |
| `cmd_extract.py` | Text, table, image extraction |
| `cmd_pages.py` | Merge, split, rotate, crop |
| `cmd_meta.py` | Metadata read/write |

## Tech stack

| Library | Purpose | License |
|----|------|--------|
| pikepdf | Form filling, page operations, metadata | MPL-2.0 |
| pdfplumber | Text and table extraction | MIT |

---

## Important notes

### Encrypted PDFs

**Not supported.** The CLI commands do not support encrypted PDFs. If the user provides
an encrypted PDF, tell them this feature is unavailable and suggest they decrypt it with
another tool first.

### Handling large files

| File size | Expected behavior |
|---------|---------|
| < 50 MB | Processes normally |
| 50-200 MB | May be slow, 1-2 minutes |
| > 200 MB | Recommend splitting first, or increase the timeout |

**Memory usage**: roughly 2-3× the file size. A 100 MB PDF needs about 300 MB of memory.

### Scanned / image PDFs

If `extract text` returns `likely_scanned: true`, the PDF content is images rather than
text. In that case use `extract image` to export images page by page, convert each page
to base64, and pass it to the model's vision capability for content recognition — rather
than asking the user to OCR it themselves.

### Error recovery

If a command fails midway:
- **Merge**: an incomplete output file may exist; delete it and retry
- **Split**: some pages may have been written; check the output directory
- **Form fill**: the original file is unchanged (output is written to a new file)
