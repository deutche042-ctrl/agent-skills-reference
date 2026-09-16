# Text Semantic Processing (excel-semantic-analysis)

This skill extracts unstructured text in Excel into structured fields, and performs normalization, categorization, and summary processing as needed.

**Applicable scenarios**: the user asks to distill key points/opinions/types from a text column, tag it, categorize it, normalize it, or produce statistical summaries. Limited to `.xlsx/.xls`.

## Quick Decisions

- **Clarify the goal and output**: first determine the extraction goal (which fields are needed) and the output form (label taxonomy, summary dimensions, output format)
- **Execution flow**: operate strictly within Excel, following the "probe → extract → categorize → summarize" flow

## Workflow

### 1. Probe and Determine Key Fields

- **Run the probe**: run the `scripts/probe_excel.py <excel_path> [output_json]` script
- **Analyze the structure**:
  - Inspect `sheet_names` and each sheet's `preview_rows` (the first 15 rows as a raw matrix) in the output, without omitting blank rows
  - Consult `merged_cells` and `merged_cells_by_row` to identify how merged cells affect the header and data regions
- **Identify key fields**: combine the header and the first few rows of data to identify the important columns relevant to semantic analysis
- **Determine the processing scope**: based on the user's needs, clarify the fields/columns/rows/range to focus on

### 2. Clarify Requirements and Caliber (throughout the whole flow)

- **Initial confirmation**: clarify the extraction fields (key points/opinions/types/entities, etc.), the label taxonomy, and the summary dimensions
- **In-process calibration**: if anomalies/doubts arise during categorization or extraction (boundary samples, conflicting labels, too high a share of "Other/Unknown", etc.), you must return to the user's requirement and the actual data to re-confirm the caliber or adjust the rules
- **Plan confirmation**: when the caliber is unclear, offer candidate options and ask the user to confirm (e.g. classification dimensions, whether "Other/Unknown" is allowed)

### 3. Locate the Text Region

- **Define the region**: determine the header row, the target text column, the data start/end rows, and abnormal rows (blank rows/notes/merged cells)

### 4. Extraction and Cleaning

- **Preserve the original**: keep the original text column and add a "cleaned text" column
- **Noise handling**: remove obvious noise (extra spaces, duplicate delimiters, placeholders) without changing the text meaning

### 5. Semantic Extraction

- **Field extraction**: extract fields such as key points, main opinions, type, entities, time, location, numbers, etc. as required
- **Structured output**: generate structured fields for each row, retaining an "evidence snippet" when necessary

### 6. Normalization and Categorization (favor explainability, allow approximation)

- **Normalization**: normalize synonymous/near-synonymous expressions (e.g. synonym mapping, unified format); you may refer to `scripts/type_division.py` for categorization
- **Multi-layer categorization strategy**: when text is irregular, avoid the hard rule of "merge only when exactly identical", and use the following strategies:
  - **Rule/dictionary categorization**: build a topic dictionary and keyword mapping to map related expressions into a unified category
  - **Similarity clustering**: vectorize the cleaned text and merge or cluster based on a similarity threshold to produce "approximately identical" groups
  - **Normalize before counting**: remove variable entities, normalize variables such as numbers and dates, then perform approximate merging and counting
- **Categorization principle**: categorization rules must be explainable; when a judgment cannot be made, assign to "Other/Unknown" and explain the reason in `notes`

### 7. Statistics and Summary

- **Dimensional statistics**: perform counts, proportions, TOP-N, cross-tabulation, etc. by the dimensions the user specifies
- **Result output**: write the summary results into a new sheet or a separate region, and state the caliber in the results

### 8. Traceable Output

- **Mapping**: each extraction result must retain its original row-number/column-number mapping
- **Output content**: include the original text, cleaned text, extracted fields, classification labels, and a caliber note for the summary

**Output field spec** (use the following fields when writing a new sheet or appending columns):

| Field name | Description |
|--------|------|
| source_sheet | Original sheet name |
| source_row | Original row number (Excel 1-based) |
| source_col | Target text column name or number |
| raw_text | Original text |
| cleaned_text | Cleaned text |
| key_points | Key-point summary (may be empty) |
| main_view | Main opinion/conclusion (may be empty) |
| entities | Entity list (may be empty) |
| category | Level-1 category |
| subcategory | Level-2 category (may be empty) |
| labels | Multi-labels (joined with a delimiter) |
| normalized_value | Normalized result (may be empty) |
| evidence | Evidence snippet (may be empty) |
| notes | Notes / uncertainty explanation (may be empty) |

**Example summary-sheet fields**: category_count (count by category), category_label_pivot (category × labels cross-tabulation), top_entities (entity TOP-N)

**Caliber note**: in the summary results, clearly state the classification taxonomy, the synonym-mapping rules, and how the Unknown class is handled.

### 9. Processing Notes and Method Disclosure

- **Written explanation**: besides the Excel results, you must provide a written explanation or a readable summary that clearly describes the processing
- **Content of the explanation**: at least include the following
  - Source of the classification data (which columns/ranges it is based on, whether columns were merged)
  - Classification method (rules/dictionary/similarity clustering/manual confirmation, etc.)
  - Classification logic (whether it further subdivides an existing classification, or re-partitions solely based on the text column)

## Quality Requirements

- **Data integrity**: modify only within the scope the user requested; cells/columns/rows not requested must not be changed. If the user asks to keep the original table, output to a new sheet or a copy.
- **Traceability**: structured results must trace back to the original row/column numbers
- **Accuracy**: when rules are unclear, raise a clarifying question first rather than guessing

## References

- Recommended analysis-report output template: `references/template-report.md`
