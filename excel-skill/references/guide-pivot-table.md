# PivotTable Enhancement Guide

This document explains how to add a PivotTable/PivotChart to an Excel task, implemented with pandas + openpyxl. The PivotTable is a cross-scenario enhancement capability — layered on after the main route task is done, not a replacement for the original analysis.

## Table of Contents

- [Activation Conditions](#activation-conditions)
- [Field Planning](#field-planning)
- [Implementation Workflow](#implementation-workflow)
- [Formatting Spec](#formatting-spec)
- [Chart Selection and Generation](#chart-selection-and-generation)
- [Mandatory Quality Validation](#mandatory-quality-validation)
- [FAQ](#faq)

---

## Activation Conditions

The PivotTable feature is activated if **any** of the following conditions is met:

### Explicit Trigger

The user explicitly mentions keywords such as:
- "PivotTable", "pivot table"
- "show the summary with charts", "cross-analysis", "multi-dimensional summary"
- "aggregate by XX and make a chart", "grouped comparison chart"

### Implicit Trigger

When, after probing (Step 2), the model judges that the data **simultaneously** meets the following conditions, proactively suggest using a PivotTable for presentation:

1. **Data scale**: rows >= 50
2. **Field structure**: at least 1 categorical field (text/category type) + 1 numeric field
3. **Task nature**: involves grouped summary, comparative analysis, proportion analysis, or trend comparison

On an implicit trigger, first briefly state "the current data is suitable for PivotTable presentation; we can summarize the YY metric across the XX dimension", and proceed only after the user agrees or does not object.

---

## Field Planning

Before generating the PivotTable, plan four kinds of fields. This step determines the structure and analysis dimensions of the PivotTable.

| Field role | Description | Selection principle | Example |
|---------|------|---------|------|
| **Row field** (rows) | Primary categorical dimension | Moderate number of unique values (5~50); the main grouping basis of the analysis | Product Name, Department, Region |
| **Column field** (columns) | Secondary categorical dimension | **Few** unique values (<= 10), used for cross-comparison | Quarter, Year, Rating tier |
| **Value field** (values) | The numeric value being aggregated | Must be numeric, paired with an aggregation function | Sales:sum, OrderCount:count |
| **Filter field** (filters) | Optional filter condition | The user may want to slice by a dimension | Year, Product line |

### Aggregation Functions

| Function | Purpose | Applicable scenario |
|------|------|---------|
| `sum` | Summation | Cumulative metrics such as amount, quantity |
| `count` | Counting | Number of records, occurrence count |
| `mean` | Average | Average price, average rating |
| `max` / `min` | Max/Min value | Extreme-value analysis |
| `median` | Median | Skewed distributions such as salary, price |

### Field-Planning Example

```
Data: sales detail table (5000 rows)
Fields: Date, Region, Product Category, Salesperson, Sales, Quantity

Pivot plan:
  Row field: Product Category
  Column field: Region
  Value fields: Sales:sum, Quantity:sum
  Filter field: (none, or filter by Year)
```

---

## Implementation Workflow

Follow the steps below strictly; each step marks the skill tool used.

### Step 1: Probe to Confirm Data Suitability

```
[Tool: Read / Bash]
Run probe_excel.py or Read to preview the data, confirming:
- Categorical fields and numeric fields exist
- No serious data-quality issues (many nulls, messy formats)
- No merged cells (or already handled with ffill)
```

### Step 2: Plan the Field Mapping

Based on the user's needs and the data structure, determine the row/column/value/filter fields (see "Field Planning" above).

### Step 3: Compute the Pivot Data with pandas

```python
import pandas as pd

df = pd.read_excel('input.xlsx', sheet_name='Sheet1')

# Exclude summary rows (if any)
df = df[~df['ColumnName'].str.contains('Total|Grand Total|Subtotal', na=False)]

pivot = pd.pivot_table(
    df,
    index=['Product Category'],        # row field
    columns=['Region'],                # column field (optional; omit if none)
    values=['Sales', 'Quantity'],      # value fields
    aggfunc={'Sales': 'sum', 'Quantity': 'sum'},
    margins=True,                      # add summary row/column
    margins_name='Total'
)

# Flatten multi-level column index (for writing to Excel)
pivot.columns = [f'{v}_{c}' if c != '' else v for v, c in pivot.columns]
pivot = pivot.reset_index()
```

### Step 4: Write and Format with openpyxl

```python
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

wb = load_workbook('input.xlsx')
ws = wb.create_sheet('PivotTable')

# Write data
for r_idx, row in enumerate(dataframe_to_rows(pivot, index=False, header=True), 1):
    for c_idx, value in enumerate(row, 1):
        ws.cell(row=r_idx, column=c_idx, value=value)

# Apply formatting (see "Formatting Spec" below)
apply_pivot_style(ws, header_row=1, data_rows=len(pivot), data_cols=len(pivot.columns))

wb.save('output.xlsx')
```

### Step 5: Generate the Accompanying Chart

```python
from openpyxl.chart import BarChart, LineChart, PieChart, Reference

chart = BarChart()
chart.title = "Sales by Product Category"
chart.y_axis.title = "Sales"
chart.x_axis.title = "Product Category"

data = Reference(ws, min_col=2, min_row=1, max_col=5, max_row=len(pivot)+1)
cats = Reference(ws, min_col=1, min_row=2, max_row=len(pivot)+1)
chart.add_data(data, titles_from_data=True)
chart.set_categories(cats)
chart.shape = 4
ws.add_chart(chart, "A" + str(len(pivot) + 4))

wb.save('output.xlsx')
```

### Step 6: Run the Mandatory Quality Validation

See the [Mandatory Quality Validation](#mandatory-quality-validation) chapter below; only deliver after all five checks pass.

### Step 7: Visual Check

```
[Tool: Bash → open_url_in_browser + take_screenshot]
First convert the workbook to PDF (this reliably renders charts and every sheet;
do NOT use HTML export — LibreOffice's xlsx→HTML drops charts and mangles multi-sheet files):
  soffice --headless --convert-to pdf output.xlsx
  # tip: if a wide sheet paginates awkwardly, set the print area / fit-to-page first
Then open the PDF and screenshot it to confirm:
- The pivot data is complete and the formatting is clear
- The chart is not an empty shell; title / axes / legend are complete
- No overlap, overflow, or garbled text
```

### Step 8: File Delivery

```
[Tool: NotifyHuman]
Push the final Excel file to the user.
```

---

## Formatting Spec

### Monochrome Style (default, general analysis scenarios)

| Element | Format |
|------|------|
| Header row | Background `#333333` + white bold text, row height 30 |
| Row-label column | Background `#F5F5F5` + black bold text |
| Data region | White background, alternating light gray `#FAFAFA` |
| Summary row/column | Background `#E8E8E8` + bold |
| Number format | Right-aligned, thousands separator, 2 decimal places |
| Percentage | `0.0%` format |

### Finance Style (financial/revenue scenarios)

| Element | Format |
|------|------|
| Header row | Background `#1F4E79` + white bold text |
| Row-label column | Background `#D6E3F0` |
| Data region | White background, alternating light blue `#EDF2F7` |
| Summary row/column | Background `#BDD7EE` + bold |
| Currency format | `$#,##0` (or the locale's currency symbol), unit noted in the header |
| Negative | Shown in parentheses `(123)` + red font |

### General Formatting Rules

Effect goal: **the table is compact overall without being cramped, with breathing space between columns, and long and short content each fit well.**

- Hide gridlines: `ws.sheet_view.showGridLines = False`
- Start content at `B2` (not `A1`); the margin improves readability
- Freeze panes: freeze the header row and the row-label column

#### Column-Width Auto-Fit Rules

| Rule | Description |
|------|------|
| Computation | Scan all cells in the column, take the display width of the longest content + padding |
| Full-width characters | Each full-width / double-width character counts as 2 character widths |
| padding | Column width = longest content width + 3 (leave breathing room) |
| Lower bound | 8 characters (avoid truncating numbers when too narrow) |
| Upper bound | 40 characters (prevent one column being so wide it squeezes others) |
| Very long text | When content exceeds the upper bound, enable `wrap_text=True` for automatic wrapping |

#### Row-Height Rules

| Row type | Row height | Description |
|--------|------|------|
| Header row | 30 | Bold titles need more vertical space |
| Normal data row | 20 | Compact but not touching text; comfortable to read numbers |
| Summary row | 26 | Slightly taller than data rows for visual distinction |
| Row with wrapped data | 36 | Automatically increased when the row has a wrap_text cell |

#### Padding

Left/right breathing space is achieved via column-width padding (+3 characters); when data columns are right-aligned, right-side spacing is naturally left. The row-label column adds 1 character of indent before the first character via `Alignment(indent=1)`.

```python
from openpyxl.utils import get_column_letter


def auto_fit_columns(ws, header_row, data_rows, data_cols, min_width=8, max_width=40, padding=3):
    """Auto-adjust column widths based on content; enable wrapping for very long text"""
    for col in range(1, data_cols + 1):
        max_len = 0
        for row in range(header_row, header_row + data_rows + 1):
            val = ws.cell(row=row, column=col).value
            if val is not None:
                cell_len = sum(2 if ord(c) > 127 else 1 for c in str(val))
                max_len = max(max_len, cell_len)
        width = min(max(max_len + padding, min_width), max_width)
        ws.column_dimensions[get_column_letter(col)].width = width
        # Enable auto-wrap for columns with very long content
        if max_len + padding > max_width:
            for row in range(header_row, header_row + data_rows + 1):
                cell = ws.cell(row=row, column=col)
                cell.alignment = Alignment(
                    horizontal=cell.alignment.horizontal or 'left',
                    vertical='center',
                    wrap_text=True,
                )


def set_row_heights(ws, header_row, data_rows, data_cols, has_summary_row=True):
    """Set row heights by row type; rows with wrapped cells are auto-increased"""
    ws.row_dimensions[header_row].height = 30
    last_data_row = header_row + data_rows
    for row in range(header_row + 1, last_data_row + 1):
        is_summary = has_summary_row and (row == last_data_row)
        base_height = 26 if is_summary else 20
        # Check whether the row has a wrapped cell
        has_wrap = any(
            ws.cell(row=row, column=c).alignment and ws.cell(row=row, column=c).alignment.wrap_text
            for c in range(1, data_cols + 1)
        )
        ws.row_dimensions[row].height = 36 if has_wrap else base_height


def apply_pivot_style(ws, header_row, data_rows, data_cols, style='monochrome'):
    """Unified pivot formatting: color/font/alignment + column auto-fit + tiered row heights"""
    header_fill = PatternFill(start_color='333333', end_color='333333', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF', size=11)
    alt_fill = PatternFill(start_color='FAFAFA', end_color='FAFAFA', fill_type='solid')
    summary_fill = PatternFill(start_color='E8E8E8', end_color='E8E8E8', fill_type='solid')
    thin_border = Border(
        bottom=Side(style='thin', color='DDDDDD')
    )

    if style == 'finance':
        header_fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
        alt_fill = PatternFill(start_color='EDF2F7', end_color='EDF2F7', fill_type='solid')
        summary_fill = PatternFill(start_color='BDD7EE', end_color='BDD7EE', fill_type='solid')

    # Header
    for col in range(1, data_cols + 1):
        cell = ws.cell(row=header_row, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')

    # Data rows (alternating colors + row-label indent)
    last_data_row = header_row + data_rows
    for row in range(header_row + 1, last_data_row + 1):
        is_summary = (row == last_data_row)
        for col in range(1, data_cols + 1):
            cell = ws.cell(row=row, column=col)
            if is_summary:
                cell.fill = summary_fill
                cell.font = Font(bold=True)
            elif (row - header_row) % 2 == 0:
                cell.fill = alt_fill
            cell.border = thin_border
            if col == 1:
                cell.alignment = Alignment(horizontal='left', vertical='center', indent=1)
            elif col > 1:
                cell.alignment = Alignment(horizontal='right', vertical='center')
                cell.number_format = '#,##0.00'

    # Column auto-fit + tiered row heights
    auto_fit_columns(ws, header_row, data_rows, data_cols)
    set_row_heights(ws, header_row, data_rows, data_cols)

    ws.sheet_view.showGridLines = False
```

---

## Chart Selection and Generation

Choose the chart type based on data characteristics and analysis purpose:

| Analysis purpose | Recommended chart | openpyxl class | Applicable condition |
|---------|---------|------------|---------|
| Compare categories side by side | Clustered column chart | `BarChart` | Categories <= 15, 1~3 value fields |
| Time/series trend | Line chart | `LineChart` | Row field is time / an ordered series |
| Overall proportion | Pie chart | `PieChart` | Categories <= 6, single value field |
| Stacked comparison | Stacked column chart | `BarChart(grouping='stacked')` | Need to see each part's share of the total |

### Chart Quality Standards

- Must have a title (`chart.title`)
- Must have axis labels (`chart.x_axis.title` / `chart.y_axis.title`)
- The legend position is clear and does not obscure the data
- Place the chart below the data region, with at least a 2-row gap
- Reasonable chart size: width 15~20 cm, height 10~12 cm

---

## Mandatory Quality Validation

After adding a PivotTable, you **must** pass the following five validations; if any fails, fix it or roll back.

### Validation 1: Raw-Data Integrity

```
[Tool: Bash]
Use Python to compare before vs. after adding the pivot Sheet:
- The raw-data Sheet's row count is unchanged
- The raw-data Sheet's column count is unchanged
- Spot-check 5 key cell values for consistency
```

```python
from openpyxl import load_workbook
wb = load_workbook('output.xlsx', data_only=True)
ws = wb['RawDataSheetName']
assert ws.max_row == expected_rows, f"Row count changed: {ws.max_row} != {expected_rows}"
assert ws.max_column == expected_cols, f"Column count changed: {ws.max_column} != {expected_cols}"
```

### Validation 2: Pivot-Data Accuracy

```
[Tool: Bash]
Independently recompute the aggregation with pandas and compare value-by-value against the pivot Sheet:
```

```python
import pandas as pd
from openpyxl import load_workbook

df = pd.read_excel('output.xlsx', sheet_name='RawDataSheetName')
expected = df.groupby('CategoryField')['ValueField'].sum()

wb = load_workbook('output.xlsx', data_only=True)
ws = wb['PivotTable']
for idx, (category, exp_val) in enumerate(expected.items()):
    actual = ws.cell(row=idx+2, column=2).value
    assert abs(actual - exp_val) < 0.01, f"{category}: {actual} != {exp_val}"
```

### Validation 3: Chart Validity

```
[Tool: Bash]
Use openpyxl to confirm the chart object has real data references:
```

```python
wb = load_workbook('output.xlsx')
ws = wb['PivotTable']
assert len(ws._charts) > 0, "No chart in the PivotTable Sheet"
for chart in ws._charts:
    assert len(chart.series) > 0, "Chart has no data series"
    assert chart.title is not None, "Chart is missing a title"
```

```
[Tool: Bash → open_url_in_browser + take_screenshot]
Convert the workbook to PDF (`soffice --headless --convert-to pdf output.xlsx`), then open the PDF
and screenshot it to visually confirm the chart is not an empty shell. Do not use HTML export — it
drops charts for multi-sheet files.
```

### Validation 4: Formula Recalculation

```
[Tool: Bash]
python scripts/recalc.py output.xlsx
Confirm total_errors == 0
```

### Validation 5: File Usability

```
[Tool: Bash]
Reload the file with openpyxl and confirm no error:
```

```python
try:
    wb = load_workbook('output.xlsx')
    sheet_names = wb.sheetnames
    assert 'PivotTable' in sheet_names, "PivotTable Sheet does not exist"
    print(f"File OK, contains {len(sheet_names)} Sheets: {sheet_names}")
except Exception as e:
    raise RuntimeError(f"File cannot be opened normally: {e}")
```

### Fallback Strategy When Validation Fails

If any validation fails and cannot be fixed quickly:

1. Delete the PivotTable Sheet and restore the original file
2. Use `NotifyHuman` to inform the user of the rollback reason
3. Present the pivot data to the user as a markdown table in the `NotifyHuman` message as an alternative

---

## FAQ

### Merged-Cell Handling

When the source data contains merged cells, only the top-left cell of a merged region has a value and the rest are None. After reading, apply ffill:

```python
df = pd.read_excel('input.xlsx')
df.fillna(method='ffill', inplace=True)
```

### Null Handling

- `pivot_table` ignores NaN by default (`dropna=True`)
- To count the number of nulls, use `aggfunc='count'` (count excludes NaN) vs. `aggfunc='size'` (size includes NaN)
- Replace NaN in the pivot result with 0 or an empty string before writing to Excel: `pivot.fillna(0)`

### Large-Data Handling

When the data exceeds 10000 rows:
- Consider pre-aggregating by key dimensions before pivoting
- When there are too many chart data points (>50 categories), show only Top N + "Other"
- Use `Bash` to process in batches to avoid out-of-memory

### PivotTable vs. Plain Formula Summary

| Scenario | Use PivotTable | Use formulas |
|------|---------|-------|
| Multi-dimensional grouping (row+column cross) | Suitable | Not suitable (needs many SUMIFS) |
| 50+ rows of data | Suitable | Possible but hard to maintain |
| Need an accompanying chart | Suitable (pivot + chart together) | Need to build the chart separately |
| Simple single-column sum | Overkill | Suitable (one SUM is enough) |
| User requires "compute in place" | Not suitable (needs a new Sheet) | Suitable (write formula in the original Sheet) |
