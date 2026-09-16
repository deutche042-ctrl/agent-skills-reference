---
name: artifact-preview
description: >-
  Render workspace artifacts (pdf/pptx/docx/xlsx/html/png/jpg) into text
  + page screenshots + thumbnail + multi-page collages, saved to a
  deterministic directory under ./.preview/{hash}/. Use Read on the
  resulting jpg/png files to visually inspect your own deliverables
  before NotifyHuman; use it to spot issues that verifier cannot catch
  — text truncation, color clashes, chart title clipped, layout drift,
  blank slides. Triggered by: "show me what the artifact looks like", "visual self-check", "preview
  pptx", "render artifact", "screenshot pdf", "render the artifact", "does my report
  look good", "are the charts complete".
---

# Artifact Preview

Render any workspace deliverable into text + screenshots so you can
visually inspect it before delivery. Pairs with `verifier-hub` (which
does deterministic numerical / structural checks) — `verifier`
answers "is the file structured correctly", `artifact-preview`
answers "does the file *look* right".

## When to use

Use after `verifier rubric check-file-format` passes and **before**
every `NotifyHuman` call that uploads a renderable artifact. The check
takes ~5 s for typical PPT/PDF and is cached — repeated calls on an
unchanged file are free.

You should `preview render` artifacts of these kinds:

| Kind | Visual value |
|------|--------------|
| `.pptx` / `.ppt` | High — slide layout, color, chart fit, text overflow |
| `.pdf`           | High — page layout, image positioning, CJK rendering |
| `.html`          | High — viewport rendering, broken styles, missing assets |
| `.docx`          | Medium — table layout, headings (text-mostly content) |
| `.xlsx`          | Low — cells dump as text; visual rendering not supported |
| `.png` / `.jpg`  | Low — already an image; preview just thumbnails it |

## CLI interface

Tool: **`preview`**. Prefer invoking it through its workspace-relative path:

```
./.skills/artifact-preview/bin/preview
```

Every subcommand writes a JSON object to stdout. Path fields contain absolute
paths so you can pass them directly to `Read`.

## Quick usage

### 1. Render
```bash
./.skills/artifact-preview/bin/preview render ./report.pptx
```
The CLI prints a JSON summary pointing at the manifest, text dump,
thumbnail, and collage paths. Sample output:

```json
{
  "ok": true,
  "output_dir": "/home/user/.../workspace/.preview/abc123def456",
  "manifest": "/.../.preview/abc123def456/manifest.json",
  "kind": "pptx",
  "page_count": 12,
  "rendered_page_count": 12,
  "collage_count": 2,
  "extracted_text_chars": 4521,
  "text": "/.../.preview/abc123def456/text.md",
  "thumbnail": "/.../.preview/abc123def456/thumb.jpg",
  "collages": ["/.../c1.jpg", "/.../c2.jpg"],
  "pages": ["/.../pages/p001.png", ...],
  "warnings": []
}
```

### 2. Read what you need

Use `Read` on the paths the JSON returned. Recommended order to save
tokens:

1. `Read` the **thumbnail** first to get a fast visual gist.
2. `Read` the **text** dump if you need to verify content.
3. `Read` specific **collages** when the thumbnail flags a region of
   interest.
4. `Read` individual **pages** only when collage resolution is
   insufficient.

```
Read ./.preview/abc123def456/thumb.jpg     ← always cheap, do this first
Read ./.preview/abc123def456/text.md
Read ./.preview/abc123def456/c1.jpg        ← page 1-6 in one image
```

`Read` returns image content directly to you as a multimodal LLM —
you'll see the picture, not the path.

### 3. Iterate

Found a problem? Fix the source file, re-run `preview render <file>`.
The output hash is content-derived, so the new render lives in a
fresh directory automatically. Old previews are kept; clean with
`preview clean <hash>` or `preview clean --all`.

## Subcommands

```bash
preview render <file>             # render and emit JSON summary
preview render <file> --text-only # skip image rendering
preview render <file> --no-collage --no-thumbnail
preview render <file> --max-pages 5
preview render <file> --page-range "1-3,7,10-12"
preview render <file> --force     # ignore cache; re-render

preview info <file|hash|dir>      # dump full manifest as JSON
preview list                      # list all cached previews
preview clean <hash>              # remove one cache entry
preview clean --all               # remove all cache entries
```

## Visual self-check checklist

When you `Read` the thumbnail/collages, look for these problems that
`verifier-hub` will not catch:

| Problem | What to look for |
|---------|-----------------|
| Text overflow | Words spilling outside text frames, ellipsis where text was cut |
| Title clipping | Slide / chart titles missing top/bottom or shifted off-canvas |
| Color clash | Indigo/purple-heavy palette (avoid unless explicitly requested) |
| Layout drift | Misaligned columns, unintended gutters, inconsistent margins |
| Chart errors | Empty bars, missing legend, wrong axis labels |
| Blank pages | Empty slides between content (often pasted-from-template artifacts) |
| Wrong locale | CJK rendered as boxes (font fallback failed) |

## Integration with verifier-hub

These two skills are complementary. A typical pre-delivery flow:

```bash
# Format & structure (verifier)
./.skills/verifier-hub/bin/verifier rubric check-file-format ./report.pptx --expected-ext .pptx
./.skills/verifier-hub/bin/verifier pptx list-slides ./report.pptx

# Visual inspection (this skill)
./.skills/artifact-preview/bin/preview render ./report.pptx
# Then Read ./.preview/<hash>/thumb.jpg, then collages as needed.

# If everything looks good, deliver:
# NotifyHuman ...
```

In `summary` of the eventual `NotifyHuman`, reference verifier for
structural facts ("12 slides, all charts have legends") and reserve
any visual claim ("layout is balanced, color palette is consistent")
for points you actually inspected via Read.

## Output directory layout

```
.preview/<source-hash>/
├── manifest.json       JSON; read this first to learn what's available
├── text.md             extracted text (per-page sections for pdf/pptx)
├── thumb.jpg           single overview image, ≤768px longest side
├── pages/              per-page images at full DPI
│   ├── p001.png
│   └── ...
└── collages/           tiled multi-page composites
    ├── c1.jpg          covers pages 1..N
    ├── c2.jpg
    └── ...
```

Source hash is content-derived (SHA-256 prefix of the file bytes).
Two files with identical bytes share the same hash and the same
cache entry.

## Limits and behavior

- `max_pages` defaults to **12**. Use `--max-pages` for longer
  documents.
- Files larger than 100 MB use a fast prefix-hash for cache keys;
  correctness is preserved (rare collisions still re-detected via
  size mismatch).
- `pptx` requires LibreOffice for screenshots. Without it, text is
  still extracted but `pages` is empty and a warning is recorded —
  the JSON still has `"ok": true` so downstream code doesn't fail.
- `html` requires a system Chromium binary (`chromium-browser` /
  `chromium` / `google-chrome` / `chrome`) on `$PATH`. Without it,
  only `text.md` is produced and a warning is recorded.
- `xlsx`/`docx` never produce images by design — they dump as
  pipe-delimited text. Visual rendering would require LibreOffice
  round-tripping for marginal gain.
- Missing Python deps (PyMuPDF, python-pptx, openpyxl, Pillow)
  degrade gracefully: text/pages corresponding to that format will
  be empty + a warning is recorded. To re-enable a format, install
  its dep:

  ```bash
  pip install pymupdf python-pptx python-docx openpyxl Pillow
  apt-get install -y chromium-browser   # system browser for HTML
  ```

## Cache root

By default previews are written to `./.preview/<hash>/` under CWD.
Override with environment variable `ARTIFACT_PREVIEW_HOME` or with
`--output-root` on `render`/`info`/`clean`.
