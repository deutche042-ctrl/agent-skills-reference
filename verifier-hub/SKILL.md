---
name: verifier-hub
description: >-
  Deterministic CLI for pre-delivery checks on xlsx, docx, pdf, pptx, text,
  archives, and rubric-style assertions. Invoked before file handoff when
  structured validation is required; not for visual-only layout judgment.
---

# verifier-hub

The `verifier` CLI performs reproducible checks on artifact files (xlsx/docx/pdf/md, etc.).
It has two main use cases:

1. **General pre-delivery validation**: before a regular Agent calls `NotifyHuman` to upload a file, use verifier to confirm the file format and key content.
2. **Questionnaire scoring / evidence**: a grader checks the graded Agent's artifacts against a rubric and writes the evidence into `questionnaire.md`.

If the current workspace does not contain the scoring files `questionnaire.md`, `ARTIFACT_INVENTORY.txt`, or `run_verifiers.py`,
use the "general pre-delivery validation" flow — do not apply the questionnaire workflow.

## CLI

Tool: **`verifier`**. Prefer invoking the in-package script with **`python3`** (no dependency on the executable bit):

```
python3 ./.skills/verifier-hub/bin/verifier
```

If the environment has already set the executable bit on `bin/verifier`, you may also use `./.skills/verifier-hub/bin/verifier`.

Two-level subcommands:

```bash
verifier --help                       # list families
verifier <family> --help              # list subcommands within a family
verifier <family> <subcmd> --help     # view a subcommand's parameters
```

Each call prints one JSON object to stdout:

```json
{"ok": true,  "tool": "<family>.<sub>", "result": {...}, "evidence": {...}}
{"ok": false, "tool": "<family>.<sub>", "error": {"code": "...", "msg": "..."}}
```

`evidence.quote` is directly-quotable human-readable evidence; in questionnaire mode you can paste it into `rationale`.

## General pre-delivery validation

When you are about to upload a file via `NotifyHuman`, validate it with verifier first to confirm the format and key content are readable and meet the task requirements.

### Notes on how to invoke

Some runtimes additionally provide a **`VerifierCheck`**-style MCP/tool wrapper; if that tool **actually** appears in the tool list, you may call it with its structured parameters. Most environments have **only Bash**, in which case always use this package's CLI (below).

Recommended flow (default):

1. **Locate the file to deliver**: confirm the file really exists, with the correct path and extension.
2. **Format validation**: run at least once for each file:
   ```bash
   python3 ./.skills/verifier-hub/bin/verifier rubric check-file-format <path> --expected-ext <.ext>
   ```
3. **Content validation**: add one check directly relevant to the task, by file type, e.g.:
   - xlsx: `xlsx list-sheets`, `xlsx assert-value`, `xlsx eval-formula`
   - docx: `docx outline`, `docx table-list`, `docx page-count`
   - pdf: `pdf pages`, `pdf text-dump`, `pdf cjk-check`
   - pptx: `pptx list-slides`, `pptx slide-text`
   - text/md: `text must-contain`, `text placeholder-audit`
   - zip: `archive zip-list`, `archive zip-check-entries`
4. **Record evidence**: `NotifyHuman.summary` should only reference verifier commands and output you actually ran; do not present results computed by Python/Bash as verifier evidence.
5. **Then deliver**: once all files to upload pass validation, call `NotifyHuman` once for all of them.

You do not need to run `run_verifiers.py` or `fill_rubric.py`; those belong only to the questionnaire scoring mode.

## Workspace conventions (pure grader / scoring mode)

Use this section only when the current workspace contains files like `questionnaire.md`, `rubric_index.yaml`, `run_verifiers.py`.
In that case the current session workspace (`judge_<id>/`) has already been prepared by the harness:

| File                          | Purpose                                                          |
| ----------------------------- | --------------------------------------------------------------- |
| `task.md`                     | The task description the graded Agent received (**read-only**)  |
| `trajectory.jsonl`            | The graded Agent's full tool-call trajectory (**read-only**)    |
| `artifacts/*`                 | The files the graded Agent actually delivered (xlsx/pptx/docx/pdf/html…) |
| `ARTIFACT_INVENTORY.txt`      | bootstrap already ran `verifier file artifact-list artifacts/`; **cat this first**, don't re-run it |
| `PREFLIGHT.txt`               | bootstrap dry-run result of `verify_questionnaire.py`, confirming the environment is healthy |
| `questionnaire.md`            | The questionnaire you must fill (**the only writable file**)     |
| `rubric_index.yaml`           | Index of rubric_id → score_labels (**read-only**)               |
| `verify_questionnaire.py`     | Self-check script: after filling, you must run `python3 verify_questionnaire.py` and see `OK` (already `chmod 555`) |
| `fill_rubric.py`              | Write helper: single / batch (`--batch-file`) write to questionnaire.md (already `chmod 555`) |
| `run_verifiers.py`            | **Batch verifier scheduling**: run N verifiers in parallel in one Bash call (already `chmod 555`) |

### Recommended workflow (4 steps)

Prefer the batch workflow to reduce serial waiting and repeated calls:

1. **`cat ARTIFACT_INVENTORY.txt PREFLIGHT.txt task.md questionnaire.md`** — read the precomputed inventory and static info first.
2. **`python3 run_verifiers.py --spec /tmp/spec.yaml --output /tmp/evidence.json`** — the spec has one entry per
   rubric (`{id, cmd: [<family>, <subcmd>, <args...>]}`); the harness schedules them in parallel (default concurrency
   8); for the same subcommand over multiple files, open multiple entries. `evidence.json.results[*].stdout` is the raw verifier JSON envelope.
3. **`python3 fill_rubric.py --batch-file /tmp/decisions.yaml`** — decisions.yaml is a list of
   `{rubric_id, score, rationale}`, written all at once. If any one fails, only that one fails; already-written entries are kept.
4. **`python3 verify_questionnaire.py`** — done when you see `OK: N/N rubrics valid`.

#### `run_verifiers.py` batch spec example

```yaml
- id: hard_0
  cmd: [rubric, check-file-format, artifacts/report.pptx, --expected-ext, .pptx]
- id: hard_1
  cmd: [pptx, list-slides, artifacts/report.pptx]
# same subcommand over multiple files → multiple entries (run in parallel)
- id: soft_3_a
  cmd: [xlsx, assert-value, artifacts/data.xlsx, --sheet, Sum, --cell, B2, --expected, '1234']
- id: soft_3_b
  cmd: [xlsx, assert-value, artifacts/data2.xlsx, --sheet, Sum, --cell, B2, --expected, '5678']
```

Output envelope (written to `--output` or stdout):

```json
{
  "ok": true,
  "concurrency": 8,
  "elapsed_sec": 3.21,
  "results": [
    {"id": "hard_0", "ok": true, "exit_code": 0,
     "stdout": "{\"ok\": true, \"tool\": \"rubric.check-file-format\", \"evidence\": {...}}",
     "stderr": "", "elapsed_sec": 0.42},
    {"id": "soft_3_b", "ok": false, "exit_code": 1,
     "stdout": "...{\"ok\": false, \"error\": ...}", "stderr": "", "elapsed_sec": 0.38}
  ]
}
```

By `id`, copy the `evidence.quote` from the verifier envelope in `stdout` into the `rationale` field of decisions.yaml.

#### `fill_rubric.py` batch vs single

```bash
# Recommended: batch
python3 fill_rubric.py --batch-file /tmp/decisions.yaml      # file
python3 fill_rubric.py --batch-stdin < /tmp/decisions.yaml   # stdin

# Compatibility: single (only when patching up)
python3 fill_rubric.py <rubric_id> <score> "<rationale, <=30 words>"
python3 fill_rubric.py <rubric_id> <score> --rationale-file /tmp/r.txt
```

Use the old single/chained style (one Bash call per rubric) only when batch is genuinely unsuitable,
e.g. a rubric that must first read a lot of trajectory context and cannot be gathered as evidence in advance.

## Tool-family overview

| family    | # tools | typical use                                                        |
| --------- | ------- | ------------------------------------------------------------------ |
| `file`    | 4       | list artifacts / validate openable / extract text / count         |
| `xlsx`    | 12      | sheet/cell/formula/format/sum/column-number format; incl. `eval-formula` cross-cell formula check |
| `docx`    | 12      | outline/section extract/tables/revisions/signature block/layout/`page-count`(auto: soffice→XML heuristic)/image count/page setup |
| `pdf`     | 4       | page count+orientation/text extract/CJK font detection/image count |
| `pptx`    | 4       | slide list/text extract/find slide by regex/chart count |
| `text`    | 9       | must-contain/count-matches/section-length/lang-ratio/citation/placeholder/list-items/date-extract |
| `archive` | 2       | list zip contents / assert required entries (good for ".zip contains stems"-type rubrics) |
| `rubric`  | 11      | high-level DSL: common combinations in one line, incl. `check-cross-consistency` cross-file numeric consistency check |

---

## file — general file operations

| subcmd          | description                       | typical call |
| --------------- | --------------------------------- | -------- |
| `artifact-list` | recursively list all files under a dir + type classification | `verifier file artifact-list workspace/artifacts/` |
| `validate`      | file exists + opens successfully with the matching library | `verifier file validate report.docx --expected-ext .docx` |
| `extract-text`  | extract plain text from any file (xlsx/docx/pdf/pptx/text) | `verifier file extract-text report.pptx --max-chars 5000` |
| `count`         | file count / total bytes under a dir (with optional ext filter) | `verifier file count workspace/artifacts/ --ext .xlsx,.csv` |

**Scoring scenario**: `cat ARTIFACT_INVENTORY.txt` first. Only when the inventory is insufficient should you re-run
`verifier file artifact-list artifacts/`.

---

## xlsx — Excel workbook (read-only)

| subcmd          | description                           | typical call |
| --------------- | ------------------------------------- | -------- |
| `list-sheets`   | sheet names + dimensions              | `verifier xlsx list-sheets f.xlsx` |
| `get-value`     | get a cell's value (default data_only) | `verifier xlsx get-value f.xlsx --sheet Summary --cell C5` |
| `assert-value`  | compare a cell value with expected (with tol) | `verifier xlsx assert-value f.xlsx --sheet 'P&L' --cell F12 --expected 365.44 --tol-abs 1.0` |
| `get-formula`   | get a cell's formula text             | `verifier xlsx get-formula f.xlsx --sheet 'P&L' --cell F12` |
| `eval-formula`  | use adjacent cells as inputs, recompute SUM/AVERAGE/+-*/ and compare with the cached value | `verifier xlsx eval-formula f.xlsx --sheet 'P&L' --cell F12 --tol-abs 0.01` |
| `find-cell`     | find a cell by regex (within any sheet) | `verifier xlsx find-cell f.xlsx --sheet Derivation --regex 'MarginalProfit'` |
| `sheet-shape`   | rows × columns (optionally trimming trailing empties) | `verifier xlsx sheet-shape f.xlsx --sheet Summary --ignore-empty` |
| `header-check`  | whether the first row contains the expected header (strict / subset) | `verifier xlsx header-check f.xlsx --sheet Params --expected Item Value Unit --mode subset` |
| `nonempty-rows` | number of non-empty rows in a range   | `verifier xlsx nonempty-rows f.xlsx --sheet Derivation --range A2:F100` |
| `style-check`   | font weight / fill color / number format | `verifier xlsx style-check f.xlsx --sheet Derivation --cell A1 --expect-bold true --expect-fill C0C0C0 --expect-number-format '0.00%'` |
| `sum-range`     | sum a numeric range (reports non-numeric cells) | `verifier xlsx sum-range f.xlsx --sheet Derivation --range B2:B30` |
| `column-format` | **all** non-empty cells in a range share the same number_format (exact or regex) | `verifier xlsx column-format f.xlsx --sheet Revenue --range F2:F100 --expected-regex '\$\|USD'` |

---

## docx — Word document (read-only)

| subcmd            | description                                   | typical call |
| ----------------- | --------------------------------------------- | -------- |
| `outline`         | list H1/H2/H3 headings                        | `verifier docx outline contract.docx --max-level 3` |
| `section-text`    | extract the body under a heading              | `verifier docx section-text contract.docx --heading-regex 'Location Advantage'` |
| `count-chars`     | total character count (incl. CJK splitting)   | `verifier docx count-chars contract.docx` |
| `table-list`      | list all tables (index / rows / cols / first-row preview) | `verifier docx table-list contract.docx` |
| `table-field`     | read a cell of a table (row index or row header + col index) | `verifier docx table-field contract.docx --table-index 0 --row-header 'Party A' --col 1` |
| `has-revisions`   | detect revisions (insertions/deletions) and comments | `verifier docx has-revisions contract.docx` |
| `check-clauses`   | check whether all expected clause titles exist (subset semantics) | `verifier docx check-clauses contract.docx --expected 'Liability' 'Confidentiality' 'Signature' --match contains` |
| `signature-block` | detect signature / seal / `_____` blocks      | `verifier docx signature-block contract.docx` |
| `layout-compare`  | shape check (min/max headings/paragraphs/tables) | `verifier docx layout-compare contract.docx --min-headings 5 --min-tables 1` |
| `page-count`      | page count. Default `--method auto`: first tries LibreOffice headless (exact), and on failure/missing package **auto-falls-back** to the XML heuristic (`<w:lastRenderedPageBreak/>` + explicit break + section break). Can force `--method soffice` / `heuristic`; optional `--min-pages` / `--max-pages` assertion | `verifier docx page-count memo.docx --max-pages 1` |
| `count-images`    | inline + floating image total (including header/footer); optional `--min` lower bound | `verifier docx count-images report.docx --min 1` |
| `page-setup`      | each section's page size + orientation (portrait/landscape); optional `--expect-orientation` | `verifier docx page-setup chart.docx --expect-orientation landscape` |

---

## pdf — PDF document (read-only)

| subcmd         | description                                                | typical call |
| -------------- | ---------------------------------------------------------- | -------- |
| `pages`        | page count + each page's width/height + orientation; optional `--expect-orientation` / `--min-pages` / `--max-pages` | `verifier pdf pages plot.pdf --expect-orientation landscape` |
| `text-dump`    | extract text for a page range                              | `verifier pdf text-dump report.pdf --start 1 --end 3 --max-chars 5000` |
| `cjk-check`    | whether CJK fonts are embedded (incl. SimSun/STSong/PingFang/MS-/YaHei…) + sampled-page CJK character ratio | `verifier pdf cjk-check report.pdf --sample-pages 5` |
| `count-images` | total Image XObjects in the document; `--per-page` gives per-page distribution; `--min` assertion | `verifier pdf count-images cost_breakdown.pdf --min 1` |

---

## pptx — PowerPoint presentation (read-only)

| subcmd         | description                                                | typical call |
| -------------- | ---------------------------------------------------------- | -------- |
| `list-slides`  | each slide's index/title/n_shapes + has_picture/chart/table | `verifier pptx list-slides deck.pptx` |
| `slide-text`   | extract all text of a slide (`--slide N`) or all slides (`--all`) | `verifier pptx slide-text deck.pptx --slide 3 --max-chars 4000` |
| `find-slide`   | find the first matching slide by regex (searches full text by default, or `--title-only`) | `verifier pptx find-slide deck.pptx --regex '^Executive Summary'` |
| `count-images` | total images/charts across the deck (optional `--per-slide`) | `verifier pptx count-images deck.pptx --per-slide` |

---

## text — text / Markdown checks (no third-party deps)

| subcmd              | description                                         | typical call |
| ------------------- | --------------------------------------------------- | -------- |
| `must-contain`      | all/any of --terms are in the file                  | `verifier text must-contain --file report.md --terms competition gross-margin --mode all` |
| `must-not-contain`  | NONE of --terms are in the file (blacklist guard)   | `verifier text must-not-contain --file report.md --terms internal-codename PRIVATE` |
| `count-matches`     | occurrences of a single regex + sampled positions   | `verifier text count-matches --file report.md --regex 'GMV.*?bn'` |
| `section-length`    | character count of the section under a MD heading (min/max threshold) | `verifier text section-length --file report.md --heading-regex 'Executive Summary' --min-chars 200` |
| `lang-ratio`        | ratio of CJK characters to non-whitespace characters | `verifier text lang-ratio --file report.md` |
| `citation-check`    | find citation markers like URL / `[1]` / `(Doe, 2024)` | `verifier text citation-check --file report.md` |
| `placeholder-audit` | find leftover placeholders (TODO / TBD / `<XXX>` / `{{...}}`, etc.) | `verifier text placeholder-audit --file report.md` |
| `count-list-items`  | count list items (`-/*/+` or `1./1)`), optional `--heading-regex` to scope a section; `--expected/--min/--max` assertions | `verifier text count-list-items --file report.md --heading-regex 'Cost Drivers' --expected 4` |
| `date-extract`      | extract and normalize all dates (ISO/US/Month-D-Y/D-Month-Y); optional `--expected YYYY-MM-DD` | `verifier text date-extract --file soap_note.md --expected 2024-03-01` |

---

## archive — ZIP archive (read-only, stdlib only)

| subcmd              | description                                                | typical call |
| ------------------- | ---------------------------------------------------------- | -------- |
| `zip-list`          | list entries in the archive (name/size/kind), filter with `--ext .wav,.mp3` | `verifier archive zip-list bundle.zip --ext .wav` |
| `zip-check-entries` | assert all `--expected` entries exist (subset; mode=contains/exact/regex) | `verifier archive zip-check-entries bundle.zip --expected master.wav guitars.wav synths.wav --mode contains` |

---

## rubric — high-level DSL (recommended path)

The `rubric` family wraps the common "one rubric, one call" scenarios, saving the mental overhead of stitching multiple low-level families together.
The return value uniformly carries `passed: true|false|null` and `evidence_quote`, ready to feed back into the questionnaire.

| subcmd                  | description                                                         | typical call |
| ----------------------- | ------------------------------------------------------------------- | -------- |
| `check-file-format`     | file exists + extension matches + opens with the matching library  | `verifier rubric check-file-format report.docx --expected-ext .docx` |
| `check-section-exists`  | docx section exists + body ≥ min-chars                              | `verifier rubric check-section-exists contract.docx --heading-regex 'Location Advantage' --min-chars 80` |
| `check-table-field`     | docx table cell equals expected (exact/contains/regex/numeric)     | `verifier rubric check-table-field contract.docx --table-index 0 --row-header 'Total Price' --col 2 --expected 1200000 --mode numeric --tol-rel 0.01` |
| `check-keywords`        | all/any/none of --terms are in the text                            | `verifier rubric check-keywords report.md --terms competition gross-margin --mode all` |
| `check-numeric`         | value matches expected ± tol; source can be an xlsx cell or a text regex capture group | `verifier rubric check-numeric f.xlsx --source xlsx --sheet Derivation --cell F12 --expected 365.44 --tol-abs 1.0` |
| `check-formula`         | xlsx formula is consistent with the referenced cells' computation  | `verifier rubric check-formula f.xlsx --sheet Derivation --cell F12 --tol-abs 0.01` |
| `check-excluded`        | NONE of --banned are in the text                                   | `verifier rubric check-excluded report.md --banned internal-codename PRIVATE` |
| `check-revisions`       | docx has no revision marks / comments                              | `verifier rubric check-revisions contract.docx` |
| `check-signature-block` | docx contains a signature / seal block                            | `verifier rubric check-signature-block contract.docx` |
| `check-no-placeholder`  | text has no TODO / `<XXX>` / `{{...}}` placeholders                | `verifier rubric check-no-placeholder report.md` |
| `check-cross-consistency` | the same metric is numerically consistent across multiple files (within ±tol); source is like `KIND:k1=v1;k2=v2` (**semicolon-separated**, to avoid clashing with commas in regexes) | `verifier rubric check-cross-consistency --source 'xlsx:file=data.xlsx;sheet=Sum;cell=B2' --source 'text:file=memo.md;regex=Total: \\$([0-9,.]+)' --tol-rel 0.01` |

---

## Error codes (handy for writing the "why it failed" in a questionnaire rationale)

| code               | meaning                                                             |
| ------------------ | ------------------------------------------------------------------- |
| `FILE_NOT_FOUND`   | file does not exist (did the graded Agent not actually deliver it?) |
| `NOT_A_FILE`       | path exists but is not a regular file                              |
| `BAD_EXT`          | extension does not match expectation                              |
| `PARSE_ERROR`      | file exists but the chosen library cannot open it (corrupt / wrong format) |
| `LOCATOR_INVALID`  | --cell / --range / --locator is malformed                          |
| `NOT_FOUND`        | sheet / heading / row-header / table-index does not exist          |
| `DEP_MISSING`      | third-party library not installed (pdfplumber, etc.); `pip install` per the hint and retry |
| `BAD_ARGS`         | required parameter missing / wrong type                            |
| `INTERNAL`         | none of the known errors above (auto-caught and wrapped by the dispatcher) |

---

## Debugging guide

When a call fails / the output is unexpected:

1. `verifier <family> <subcmd> --help` to see the full parameters and defaults.
2. Use **Read** to open `skills/verifier-hub/lib/<family>.py` and read the source (each family ≤ 400 lines, easy to locate).
3. If `DEP_MISSING`, install the package per the hint and retry (containers usually have it pre-installed; the `openpyxl / python-docx / pdfplumber / pypdf / python-pptx / PyYAML` used by the rubric pipeline are all in `requirements.txt`).
4. If `LOCATOR_INVALID`, first list the structure with `xlsx list-sheets` / `docx outline` / `docx table-list`, then choose the cell / heading / row-header.

## When **not** to use verifier?

- When the rubric involves subjective judgment ("is the chart aesthetically pleasing", "is the tone professional") → tools alone cannot give decisive evidence; honestly read the text and then judge.
- When the rubric requires actual rendering (how HTML actually displays, the overall visual of a PPT) → verifier can only grep elements and cannot judge "does it look right".

For the remaining **structure / numeric / keyword / format / placeholder** rubrics, verifier gives more reliable verdicts than an LLM.
