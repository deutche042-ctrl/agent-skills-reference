---
name: pptx-deck-orchestrator
description: Create and edit polished, editable PowerPoint presentations (.pptx) from a topic, request, notes, documents, data, images, outlines, templates, or an existing deck. Use whenever the user asks to generate, make, rewrite, polish, redesign, or update a PPT, PPTX, slide deck, presentation, report deck, lesson deck, pitch deck, training deck, technical deck, or academic deck. Produce the actual presentation file rather than only an outline or instructions.
---

# PPTX Deck Orchestrator

Create one strong, editable `.pptx` from the user's request and source material. The requested deliverable is the actual presentation, not an outline, page plan, checklist, or explanation of how to make one.

## Generate the deck

1. Capture audience, purpose, required sections, slide count, aspect ratio, source material, style, and output path in a working brief.
2. Write an action-title storyline with one communication job per slide.
3. Separate supplied facts, verified facts, calculations, estimates, simulations, recommendations, and unknowns. Never invent numbers, sources, quotations, credentials, case outcomes, or product behavior.
4. Define one coherent visual system: page size, safe margins, typography, palette, spacing, image/chart treatment, footer, and page number.
5. Build the actual presentation with an available PPTX authoring tool or library. Keep text, shapes, tables, diagrams, charts, and other suitable objects editable.
6. Save the presentation to the requested `.pptx` path. Confirm that it exists, is non-empty, and opens as a PPTX.

Use the research, extraction, image, data, and authoring capabilities needed for the task. When source material is incomplete, make reasonable assumptions and identify them; do not fabricate evidence.

Keep every text-bearing object inside the canvas. Prevent clipping, collisions, tiny body text, unsafe shape-to-fit growth, and footer overlap. Shorten, enlarge, split, or change the layout when content does not fit.

Prefer charts for real quantitative comparisons, diagrams for systems and processes, images for visual evidence, and structured typography for explanation. Avoid repeated generic card grids, excessive pills, emoji decoration, arbitrary gradients, chartjunk, and dense text walls.

For edits, read [edit-mode.md](references/edit-mode.md).

If no PPTX authoring capability is available, return a concise blocker instead of substituting a text outline.

## Finish and deliver

- Treat the generated PPTX as an internal candidate until the selected final check is complete. Do not attach, link, upload, or otherwise expose it during generation, rendering, inspection, or repair.
- Default to exactly one user-visible file: the finished editable PPTX. Require its path to end in `.pptx` case-insensitively.
- Keep JPEG/JPG, PNG, WebP, GIF, SVG, PDF, screenshots, thumbnails, cover images, source assets, rendered slides, montage, render directories, JSON, check reports, and font inventories internal.
- Do not delete working files merely to satisfy delivery; omit them from the outgoing attachment and link list.
- Include another format, preview, check package, or source package only when the user explicitly requests it.
- Deliver only when the final report says `status=PASS`, `deliverable_allowed=true`, and `delivery_check.allowed=true`. If the final check is incomplete or fails, return a concise text-only blocker and expose no file.

## Run one internal final check

Default to **Lite**. Use **Mid** when the user explicitly asks for it or when at least one condition is material:

- four or more analytical chart pages;
- custom or brand fonts must render reliably;
- a long or dense deck makes one montage ambiguous;
- substantial structural edits to an existing deck;
- reference or brand fidelity requires selected full-size page inspection;
- medical, legal, financial, policy, safety, compliance, investor, or research claims need targeted checking.

Run only the selected profile. Mid replaces Lite for that candidate and reviews at most six selected pages.

For higher-risk material, use Mid and verify decisive numbers, dates, named entities, quotations, citations, causal conclusions, and regulatory or clinical recommendations with primary or authoritative sources. Preserve scope and uncertainty, and place concise provenance on the affected slide or in notes.

These checks inspect a finished candidate; they do not create or replace the presentation.

### Lite — default

Run after a coherent candidate exists:

```bash
python3 scripts/qa_lite.py output.pptx \
  --work-dir qa-lite \
  --expected-aspect-ratio 16:9
```

Inspect the 60 DPI montage for clipping, overlap, broken glyphs, blank pages, unreadable density, inconsistent hierarchy, and obvious chart problems. Open an individual rendered slide when the montage is ambiguous or the report identifies a risk page.

After inspection and any needed repair, finalize the candidate:

```bash
python3 scripts/qa_lite.py output.pptx \
  --work-dir qa-lite \
  --expected-aspect-ratio 16:9 \
  --visual-status pass
```

If the candidate changes during repair, rerun the same profile on the changed file. Deliver only when `status=PASS`, `deliverable_allowed=true`, and `delivery_check.allowed=true`.

### Mid — risk-triggered

Run Mid instead of Lite:

```bash
python3 scripts/qa_mid.py output.pptx \
  --work-dir qa-mid \
  --expected-aspect-ratio 16:9
```

Mid adds a font inventory, renders at 84 DPI, and creates `review-scope.json` with at most six pages chosen from opening, closing, chart, static-risk, and coverage pages. Inspect the montage plus those pages.

Finalize after inspection and any needed repair:

```bash
python3 scripts/qa_mid.py output.pptx \
  --work-dir qa-mid \
  --expected-aspect-ratio 16:9 \
  --visual-status pass \
  --reviewed-pages scope
```

Do not create a manual per-page review document. If the PPTX changes, rerun the same profile on the changed file.

## Final response

When the final check permits delivery, return one concise link to the editable PPTX and no other file link or attachment. State slide count and aspect ratio in plain text only when useful. Never claim the checks passed unless the final report says `PASS`.
