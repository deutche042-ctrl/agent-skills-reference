---
name: excel-skill
description: Full-scenario Excel/CSV data-processing skill, covering data analysis & insights, text semantic classification, numeric computation, quantitative modeling (prediction/evaluation/optimization), data mining, table creation and formatting, plus PivotTable/PivotChart enhanced presentation. Use this skill whenever a task involves processing, analyzing, or producing structured data — regardless of whether the user uploaded a file. Use it when the user uploads an Excel/CSV and asks to process it; when the user dictates data to be organized into a table; when the user asks to compute, aggregate, model, predict, classify, mine, or visualize; when the user asks to create or edit Excel; when the user asks for pivot tables, cross-analysis, or grouped-summary charts. This skill does not fetch external information — if additional data is needed, obtain it through other means first.
version: v4.15-0403
---

# Full-Scenario Excel Data-Processing Skill

## Quick Routing

After receiving a request, **first identify the scenario, then read the corresponding reference file** and execute the task under its guidance.

### Routing Decision Table

| Scenario | Typical signal words / intent | Reference to read |
|------|----------------|-----------------|
| **Data insights** | "analyze this", "take a look for me", "any findings", "give me insights", "interpret the data", "business diagnosis", "what's the trend", "how is it performing" | `references/guide-data-insights.md` |
| **Text semantic processing** | "extract key points", "categorize", "tag/label", "normalize text", "semantic extraction", "classify opinions", "summarize text" | `references/guide-semantic-analysis.md` |
| **Numeric computation & processing** | "compute", "aggregate", "sum", "formula", "process data", "handle formatting", "total values", "date/time calculation", "merge tables", "split data", "deduplicate", "format conversion" | `references/guide-data-processing.md` |
| **Quantitative modeling** | "build a model", "predict", "evaluate a model", "rank/score", "optimize allocation", "regression", "AHP", "TOPSIS" | `references/guide-data-modeling.md` |
| **Data mining** | "mine", "discover patterns", "association analysis", "clustering", "find rules", "correlation analysis", "feature extraction" | `references/guide-data-digging.md` |
| **Table creation & formatting** | "make a table", "organize into Excel", "generate a table", "create a report", "make a template", "tidy up the formatting" | `references/ref-xlsx-workflow.md` (includes default rules for row height / column width / truncation) |

### Scenario Boundaries

- **Insights vs. modeling**: insights focus on business conclusions ("what is the current state, why, and what to recommend"); modeling focuses on building a quantitative model (prediction / evaluation / optimization objective functions).
- **Insights vs. mining**: insights are business-problem driven; mining is centered on algorithmic methodology (clustering, association rules, etc.).
- **Computation vs. modeling**: computation is numeric processing with explicit formulas; modeling builds prediction / evaluation / optimization models.
- **Text semantics vs. insights**: text semantic processing targets unstructured text columns (extraction, categorization, tagging); insights analyze existing structured metrics.
- **Table creation vs. other scenarios**: use this route when the user has no existing data file and needs to create Excel from scratch (e.g. making a template, organizing information into a table); if analysis/modeling is also needed after creation, continue routing to the appropriate scenario once creation is done.

> **Multiple overlapping scenarios**: if a task spans multiple scenarios, pick the primary route based on the main request; the reference files for secondary scenarios can also be consulted as needed.

---

## General Execution Flow

The following flow applies to all scenarios. The specific analysis methods, modeling steps, etc. are guided by each reference file.

### 0. Key Principles (default for all tasks)

1. **Scope of modification is bounded by the goal**: by default you may modify the existing workbook within the scope necessary to complete the task (values, formulas, styles, merges, column widths / row heights, etc.), but do not introduce destructive changes unrelated to the task (e.g. deleting detail rows, changing the data caliber, renaming/deleting sheets). If the user explicitly requires that "no cell other than the specified location (including formatting/formulas/other sheets) may be touched", follow that constraint strictly.
2. **Output location follows the user's request**: if the user asks to "edit the original sheet directly / fill in a certain sheet / overwrite the original file", edit in place; if the user asks to "keep the original sheet / don't change the original sheet / keep a backup", copy the sheet or save to a new file so the original sheet stays unchanged.
3. **Write formulas into the final delivered table**: whenever a computation is needed, prefer writing Excel formulas into the corresponding cells of the table finally delivered to the user (the original sheet or the output sheet the user requested).
**⚠️ Critical: Excel formulas are always the first choice**

Whenever a formula can be used, you must compute with a formula.

✅ Correct (use formulas):
```python
ws['C2'] = '=A2+B2'
ws['D2'] = '=C2/B2*100'
ws['E2'] = '=SUM(A2:A100)'
```

❌ Forbidden (pre-computing in Python and hardcoding the value):
```python
result = value_a + value_b
ws['C2'] = result
```

Static values are only allowed in these cases:
- Externally scraped data
- Constants that never change
- Cases where using a formula would create a circular reference


### Step 1: Determine the Data Source

| Situation | Handling |
|------|---------|
| User uploaded an Excel/CSV file | Proceed directly to Step 2 |
| User dictated/pasted data but provided no file | First structure the information into a DataFrame and create the Excel as required; table layout (including row height / column width / truncation) follows `references/ref-xlsx-workflow.md`. If the generated Excel needs further data insights, etc., you may continue to Step 2 to refine it. |
| Information is insufficient to complete the task | Ask the user for more, or first dispatch another skill/tool to obtain the data before continuing |

### Step 2: Probe and Assess

Once you have the data file, **probe before you act**:

1. **Run the probe script** to understand the data structure (note: `probe_excel` is only a probing helper for understanding the data; to actually execute the task you must use `Read` to understand the file's full content):
   - Excel files: `python scripts/probe_excel.py <file_path>`
   - CSV files: preview with `pd.read_csv(..., nrows=15)`, mind the encoding (try `utf-8`/`utf-8-sig` first, and fall back to other encodings such as `latin-1` if decoding fails)

2. **Assess the data scale** to decide the execution strategy:
   - **Small data** (rows ≤ 1000, file ≤ 5MB): load and process in one pass
   - **Large data** (rows > 1000 or file > 5MB): use a batched strategy (per-sheet / row-batch processing / streaming reads / column pruning)
   - **Multi-sheet files**: run the full "probe → process → output" flow separately for each sheet

3. **Identify merged cells**: check the `merged_cells` field in the probe output; a merged cell's value is stored only in its top-left cell. Extraction tasks need `ffill`; when writing formulas / performing merges, values/formulas may only be written into the top-left cell — see `references/ref-xlsx-workflow.md`.

4. **Identify "unclear headers" and perform field understanding**: if there is no header / empty header columns / multi-row headers / the first few rows are titles or notes rather than headers:
   - Use `scripts/preview_excel_rows.py` to preview more rows (e.g. the first 30) of the suspect sheet, and combine with the data shape to judge which row is the true header
   - For empty-header columns, inspect the first 20 non-null values of that column (type and pattern: date/amount/ID/text category, etc.), and infer a temporary column name based on neighboring columns and user needs (e.g. `Unnamed_Amount`, `Unnamed_Date`, `Unnamed_ID`)
   - In subsequent mapping and computation, prefer anchoring the field source by "column coordinate / column letter + row range" to avoid referencing the wrong column due to a missing header

5. **Identify "special rows / special cells" and handle them specially**: if there are rows such as "Total / Grand Total / Subtotal / Summary / Cumulative" whose caliber differs from the detail rows:
   - Locate these rows in the `special_rows` field of the probe output and confirm via preview whether they are summary rows
   - Before aggregation / statistics / modeling, exclude these summary rows from the detail data to avoid double counting

### Step 3: Requirement–Data Calibration

Before processing, confirm how the user's metrics/concepts map to the fields in the data. Which column is the "revenue" the user mentioned? How is the "completion rate" computed? Avoid "answering the wrong question".

### Step 4: Execute by Scenario Route

Read the reference file corresponding to the routing decision table and execute the task following its workflow.

### Step 4.5: PivotTable Enhancement Decision

After the main route task is done and before delivery, decide whether to add a PivotTable/PivotChart on top. **The PivotTable is an enhancement layer; it does not change the main-route logic.** If you anticipate or find on inspection that the PivotTable adds little value, you may skip generating it.

**Activation conditions** (activate if any one is met):

1. **Explicit**: the user mentions "PivotTable", "pivot table", "summarize with charts", "cross-analysis", "grouped comparison chart".
2. **Implicit**: the data satisfies rows >= 50 + at least 1 categorical field + 1 numeric field + the task involves grouped summary/comparison/proportion, and the task is not so complex that the resulting PivotChart would look poor.

**When activated, execute**:

1. Read `references/guide-pivot-table.md` and follow its workflow: field planning → pandas computation → openpyxl formatting → chart generation → **mandatory five-point validation** → visual check → delivery.
2. The mandatory five checks: raw-data integrity, pivot-data accuracy, chart validity, zero formula-recalc errors (`recalc.py`), file usability.
3. If any check fails and cannot be fixed quickly → delete the pivot Sheet, fall back to delivering the non-pivot version, and present the pivot data as a markdown table in the delivery message as an alternative.

**Toolchain**: `Bash` (run Python scripts; convert to PDF for the visual check) → `open_url_in_browser` + `take_screenshot` (screenshot the PDF) → `NotifyHuman` (file delivery).

### Step 5: Delivery

- **Match the change strategy to the request**: by default you may modify within the necessary scope to complete the task; if the user asks to "only change the specified location / keep the original table / don't change the original sheet", follow it strictly and implement via new sheet / copied sheet / save-as, etc.
- **Preservation requests take priority**: preserve the original table only when the user asks to (copy the sheet or save-as); when preservation is not requested, filling directly into the original table is allowed.
- **Formulas in the delivered table**: write computed results as Excel formulas at the location in the finally delivered table; do not compute in a temporary/intermediate sheet and then paste back the numeric values.
- **Conclusions over process**: the final deliverable focuses on the conclusions and recommendations the user needs, filtering out intermediate process.
- **Professional formatting**: charts must have titles / axes / legends; row heights and column widths of newly created tables must follow the "column-width / row-height auto-fit spec" below; other formatting details are in `references/ref-xlsx-workflow.md` and the quality spec below.
- **Do not proactively do external search to fill gaps**: unless the user asks, do not search on your own to augment data; when information is insufficient, confirm with the user first.

### Step 6: Plausibility Check of Information (mandatory when generating/inferring information)

When the task requires "generating information", "filling missing values", "organizing dictated information into a table", "outputting conclusions/recommendations", or "constructing example data", a plausibility check is mandatory before delivery.

Key checks (not limited to):

1. **Reasonable units**:
   - Liquids prefer volume units (ml/L), non-liquids prefer mass units (g/kg); if the user mixes them, correct by common sense and annotate.
   - Currency, quantity, percentage, temperature, etc. must be consistent; state the unit clearly in the header (e.g. `Revenue ($)`, `Weight (g)`).
2. **Value ranges**:
   - Time/duration/quantity should generally not be negative; a negative value is preferentially judged an input error and corrected (e.g. take absolute value or blank it) with the reason annotated.
   - Percentages are generally in `[0, 1]` or `[0%, 100%]`; if something like `120%` appears, judge whether it is a "1.2" vs "120" format confusion and unify it.
3. **Date/time consistency**:
   - The end time must not be earlier than the start time; if it spans days, state it explicitly or split the date.

---

## Excel Output Quality Spec

All output Excel files must meet the following standards (including formatting, row height / column width / truncation, formula recalculation and validation). For the detailed technical workflow see `references/ref-xlsx-workflow.md`.

### Basic Spec

| Item | Requirement |
|------|------|
| **Font** | Use a single professional font throughout (e.g. Arial, Calibri); keep fonts consistent across regions |
| **Formula errors** | Zero formula errors before delivery (`#REF!` `#DIV/0!` `#VALUE!` `#N/A` `#NAME?`); validate with `scripts/recalc.py` |
| **Existing templates** | When modifying an existing file, match its formatting, styles, and conventions exactly; existing template conventions take priority over this spec |
| **Formula vs. hardcoding** | Computed results must be written as Excel formulas (e.g. `=SUM(B2:B9)`); you must **not** compute in Python and hardcode the value into the cell |

### Column-Width / Row-Height Auto-Fit Spec

When generating or modifying Excel tables, column widths and row heights must auto-fit the content so the table is neither cramped nor wasteful of space.

**Column width**: scan all cells in the column, take the display width of the longest content (full-width / double-width characters count as width 2) + 3 characters of padding. Lower bound 8, upper bound 40. Columns exceeding the upper bound enable `wrap_text=True` for automatic wrapping.

**Row height**: header row 30, normal data row 20, summary row 26, rows containing wrapped cells 36.

**Padding**: provide breathing room via column-width padding (+3) and `Alignment(indent=1)` on the row-label column.

For the detailed implementation functions (`auto_fit_columns`, `set_row_heights`) see the general formatting rules chapter of `references/guide-pivot-table.md`; **all newly created Sheets and table regions should call them**. When modifying a user's existing template, keep the original row heights and column widths unchanged (unless the user asks to adjust them).

### Financial-Model-Specific Spec

**Color coding** (industry standard; follow when the user has not specified otherwise):

| Color | Meaning |
|------|------|
| Blue text `RGB(0,0,255)` | Hardcoded input values, user-scenario adjustable items |
| Black text `RGB(0,0,0)` | All formulas and computed results |
| Green text `RGB(0,128,0)` | Cross-sheet references (within the same workbook) |
| Red text `RGB(255,0,0)` | Cross-file external links |
| Yellow fill `RGB(255,255,0)` | Key assumptions needing attention or items to be filled in |

**Number formats**:

| Type | Format |
|------|------|
| Year | Text string, e.g. `"2024"`, not a number format |
| Currency | `$#,##0`, with the unit noted in the header (e.g. `Revenue ($mm)`) |
| Zero value | Displayed as `-`, format `$#,##0;($#,##0);-` |
| Percentage | `0.0%` (one decimal place) |
| Multiple | `0.0x` (e.g. EV/EBITDA, P/E) |
| Negative | Shown in parentheses `(123)`, not with a minus sign `-123` |

**Formula spec**:
- Put all assumptions (growth rate, margin, multiple, etc.) in dedicated assumption cells; formulas reference the cell rather than writing the number directly
  - Correct: `=B5*(1+$B$6)`, Wrong: `=B5*1.05`
- Hardcoded values must be annotated with their source alongside, in the format: `Source: [source], [date], [specific reference]`

---

## PivotTable Enhancement Module

The PivotTable is an **add-on enhancement capability**, layered on after the main route task is done; it does not change the original routing logic.

### Capability Overview

- Use `pandas.pivot_table()` to compute multi-dimensional summary data
- Use `openpyxl` to write the result into a new Sheet with professional formatting (two styles: Monochrome / Finance)
- Use `openpyxl.chart` to generate accompanying charts (bar/line/pie, auto-selected by data characteristics)
- Convert the workbook to PDF (`soffice --headless --convert-to pdf`), then use `open_url_in_browser` + `take_screenshot` to visually verify the chart effect (avoid HTML export — it drops charts for multi-sheet files)

### Mandatory Quality Requirements

After adding a PivotTable, it must pass five checks; if any fails, roll back:

1. **Raw-data integrity**: after adding the pivot Sheet, the original data Sheet's row/column counts are unchanged and spot-checked values match
2. **Pivot-data accuracy**: independently recompute the aggregates with pandas and compare them one-by-one against the pivot Sheet (error < 0.01)
3. **Chart validity**: openpyxl confirms the chart has data series and a title + a screenshot visually confirms it is not an empty shell
4. **Formula recalculation**: `python scripts/recalc.py output.xlsx` → total_errors == 0
5. **File usability**: openpyxl reloads without error and the pivot Sheet exists

**Detailed implementation guidance**: `references/guide-pivot-table.md`

### Toolchain

| Step | Tool | Purpose |
|------|------|------|
| Preview data | `Read` / `Bash` (probe_excel.py) | Quickly understand data structure and suitability |
| Compute + format + chart | `Bash` (Python scripts) | pandas aggregation → openpyxl write → chart generation |
| Formula validation | `Bash` (recalc.py) | Confirm zero formula errors |
| Visual check | `Bash` (convert to PDF) → `open_url_in_browser` + `take_screenshot` | Convert to PDF (`soffice --convert-to pdf`), then screenshot the PDF to confirm chart effect (HTML export drops charts) |
| File delivery | `NotifyHuman` | Push the final Excel file |
