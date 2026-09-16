# Excel File Technical Workflow (xlsx workflow)

This file covers the complete technical process for creating, editing, formula-recalculating, and validating Excel files.

## Tool Selection

| Tool | Applicable scenario |
|------|---------|
| **pandas** | Data analysis, bulk read/write, simple data export |
| **openpyxl** | Complex formatting, writing formulas, Excel features (merged cells, colors, styles) |

The two can be combined: pandas handles the data logic, openpyxl handles formatting and formulas.


## Reading Excel

```python
import pandas as pd

df = pd.read_excel('file.xlsx')                          # first sheet
all_sheets = pd.read_excel('file.xlsx', sheet_name=None)  # all sheets → dict

# Specify types to avoid inference errors
df = pd.read_excel('file.xlsx', dtype={'id': str}, parse_dates=['date_col'])
```

### Handling Merged Cells

A merged cell's value exists only in the top-left cell; the rest read as `NaN`. After reading, fill down/right:

```python
from openpyxl import load_workbook

wb = load_workbook('file.xlsx')
ws = wb.active

# Inspect merged ranges
print(list(ws.merged_cells.ranges))

# Unmerge cells and fill values (suitable for extraction tasks)
ws.unmerge_cells('A1:A3')
# Or use pandas ffill to fill NaN
df = pd.read_excel('file.xlsx')
df.ffill(inplace=True)
```

When you need to write a formula onto a merged cell, or merge a region that contains formulas, follow the rules below to avoid `#REF!`, lost formulas, or blank display:

1. In Excel semantics a merged region keeps only the top-left cell (anchor). After merging, only the anchor cell may hold a value/formula; the rest must be empty.
2. Writing a formula to a merged region: write the formula to the anchor cell, then run `merge_cells` on the region.
3. Merging a "region that contains formulas": first move/write the formula you want to keep into the anchor cell, clear the `value` of the other cells in the region, then merge.
4. Referencing a merged region in a computation: use the anchor coordinate when referencing; if the coordinate you have is inside the merged range, first resolve it to the anchor before generating the formula reference.

```python
from openpyxl.utils.cell import range_boundaries

def merged_anchor_cell(ws, row, col):
    for merged_range in ws.merged_cells.ranges:
        if merged_range.min_row <= row <= merged_range.max_row and merged_range.min_col <= col <= merged_range.max_col:
            return (merged_range.min_row, merged_range.min_col)
    return (row, col)

def write_formula_to_merged(ws, cell_range, formula):
    min_col, min_row, max_col, max_row = range_boundaries(cell_range)
    ws.cell(row=min_row, column=min_col).value = formula
    for r in range(min_row, max_row + 1):
        for c in range(min_col, max_col + 1):
            if r == min_row and c == min_col:
                continue
            ws.cell(row=r, column=c).value = None
    ws.merge_cells(cell_range)
```

## Creating an Excel File

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
ws = wb.active

ws['A1'] = 'Title'
ws['B2'] = '=SUM(B3:B10)'   # write a formula, not a hardcoded computed value

ws['A1'].font = Font(bold=True, color='FF0000')
ws['A1'].fill = PatternFill('solid', start_color='FFFF00')
ws['A1'].alignment = Alignment(horizontal='center')
ws.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```

## Cell Settings (Row Height / Column Width / Truncation)

If you are outputting results into a **new sheet or a new table region** and the user has not specified details such as row height/column width, you may apply a unified layout based on the table shape; if you are modifying the user's existing template and the user did not ask to "tidy up the format / unify row heights and column widths", keep the original row heights, column widths, and alignment unchanged.

### Rules (default)

- Multi-row multi-column (rows > 1 and columns > 1): row height 50, column width 80, truncate
- Single-column table (columns = 1): column width 150, truncate
- Single-row table (rows = 1): row height 50, truncate

### Meaning of Truncation

- No wrapping: `wrap_text=False`
- Truncate very long strings by characters and add an ellipsis to avoid overflow hurting readability

```python
from __future__ import annotations

from typing import Optional, Tuple

from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


def _used_range(ws: Worksheet) -> Tuple[int, int]:
    max_row = 0
    max_col = 0
    for row in ws.iter_rows(values_only=False):
        for cell in row:
            if cell.value is None:
                continue
            max_row = max(max_row, cell.row)
            max_col = max(max_col, cell.column)
    return max_row, max_col


def _truncate_text(value: object, max_chars: int) -> object:
    if not isinstance(value, str):
        return value
    s = value.strip()
    if len(s) <= max_chars:
        return value
    if max_chars <= 1:
        return "…"
    return s[: max_chars - 1] + "…"


def _col_width_chars(ws: Worksheet, col_index: int, default_width: int = 10) -> int:
    letter = get_column_letter(col_index)
    width = ws.column_dimensions[letter].width
    if width is None:
        return default_width
    try:
        return max(1, int(round(float(width))))
    except (TypeError, ValueError):
        return default_width


def apply_table_cell_settings(
    ws: Worksheet,
    *,
    target_range: Optional[Tuple[int, int]] = None,
) -> None:
    max_row, max_col = target_range or _used_range(ws)
    if max_row <= 0 or max_col <= 0:
        return

    set_row_height = (max_row == 1) or (max_row > 1 and max_col > 1)
    set_col_width = (max_col == 1) or (max_row > 1 and max_col > 1)

    row_height = 50
    col_width = 150 if max_col == 1 else 80

    align = Alignment(wrap_text=False, vertical="center")

    if set_col_width:
        for c in range(1, max_col + 1):
            ws.column_dimensions[get_column_letter(c)].width = col_width

    if set_row_height:
        for r in range(1, max_row + 1):
            ws.row_dimensions[r].height = row_height

    for r in range(1, max_row + 1):
        for c in range(1, max_col + 1):
            cell = ws.cell(row=r, column=c)
            if cell.value is None:
                continue
            max_chars = col_width if set_col_width else _col_width_chars(ws, c)
            cell.value = _truncate_text(cell.value, max_chars)
            cell.alignment = align
```

## Editing an Existing Excel File

```python
from openpyxl import load_workbook

wb = load_workbook('existing.xlsx')
ws = wb.active  # or wb['SheetName']

ws['A1'] = 'New value'
ws.insert_rows(2)
ws.delete_cols(3)

new_ws = wb.create_sheet('NewSheet')
new_ws['A1'] = 'Data'

wb.save('modified.xlsx')
```

> **Note**: opening with `data_only=True` and then saving permanently loses formulas, keeping only values.

## Formula Recalculation (mandatory step)

Formulas written by openpyxl are just strings; the cells have no computed value. **Any delivered file containing formulas must be recalculated**:

```bash
python scripts/recalc.py output.xlsx
# Or specify a timeout (default 30 seconds)
python scripts/recalc.py output.xlsx 60
```

Dependency: requires LibreOffice installed (the `soffice` command available). The script auto-configures the macro on first run.

**Degraded behavior when LibreOffice is unavailable**: if `soffice` is not installed, the script degrades automatically — it skips recalculation, only scans the file for existing formula-error values, and returns `status: "skipped_no_libreoffice"` with a warning. In this case the formula cells have no computed value, and the delivered file should tell the user to refresh manually in Excel (`Ctrl+Alt+F9`).

### Interpreting recalc.py Output

```json
{
  "status": "success",        // or "errors_found"
  "total_errors": 0,
  "total_formulas": 42,
  "error_summary": {          // only present when there are errors
    "#REF!": {
      "count": 2,
      "locations": ["Sheet1!B5", "Sheet1!C10"]
    }
  }
}
```

When `status` is `errors_found`, fix them one by one using the locations in `error_summary`, then re-run recalculation until `status` is `success`.

## Formula Validation Checklist

Before writing formulas, verify:

- [ ] **Test 2-3 references**: confirm the referenced values are correct before building in bulk
- [ ] **Column-number mapping**: Excel columns start at 1, DataFrame at 0; column 64 = BL, not BK
- [ ] **Row-number offset**: Excel rows start at 1; DataFrame row 5 = Excel row 6 (including the header)
- [ ] **NaN handling**: check the denominator with `pd.notna()` before division
- [ ] **Cross-sheet references**: the format is `Sheet1!A1`
- [ ] **Avoid circular references**: check the formula dependency chain

## Common Errors and Fixes

| Error | Cause | Fix direction |
|------|------|---------|
| `#REF!` | Referenced a non-existent cell/range | Check whether the row/column number is out of bounds or was deleted |
| `#DIV/0!` | Denominator is zero or empty | Add an `IF` check: `=IF(B2=0,"",A2/B2)` |
| `#VALUE!` | Data-type mismatch (e.g. text in a computation) | Ensure the columns in the computation are numeric |
| `#NAME?` | Function name misspelled | Check the formula's function name |
| `#N/A` | VLOOKUP/MATCH found no match | Add `IFERROR` or check the data source |

## Code Style

When generating Excel-operation code:
- Keep the code concise, without redundant comments
- Don't print intermediate-process logs
- Add a note in the adjacent cell for complex formulas or key assumptions

---

## Time-Format Conversion

When encountering Excel raw time serial numbers, use the following function to convert them to a readable format:

```python
import datetime
from typing import Union

def excel_time_to_readable(excel_time: Union[float, int, str], date1904: bool = False) -> str:
    """Convert an Excel time serial number to human-readable time (e.g. 2023-12-31 12:00:00)"""
    excel_time = float(excel_time)
    base_date = datetime.datetime(1904, 1, 1) if date1904 else datetime.datetime(1899, 12, 30)
    days = int(excel_time)
    time_fraction = excel_time - days
    target_date = base_date + datetime.timedelta(days=days)
    seconds = int(time_fraction * 86400)
    time_obj = datetime.timedelta(seconds=seconds)
    if days == 0:
        return str(time_obj)
    return (target_date + time_obj).strftime("%Y-%m-%d %H:%M:%S")
```

**Time-range splitting**: when encountering the `09:00-18:00` format, first split it into start/end columns, then compute the duration:

```python
df[['start_time', 'end_time']] = df['time_range'].str.split('-', expand=True)
df['start_time'] = pd.to_datetime(df['start_time'], format='%H:%M')
df['end_time'] = pd.to_datetime(df['end_time'], format='%H:%M')
df['duration_hours'] = (df['end_time'] - df['start_time']).dt.total_seconds() / 3600
```

---

## Row/Column Operations

### openpyxl Row/Column Operations

```python
from openpyxl import load_workbook

wb = load_workbook("data.xlsx")
ws = wb.active

ws.insert_rows(5, 3)   # insert 3 rows at row 5
ws.delete_rows(5, 2)   # delete 2 rows starting at row 5
ws.insert_cols(3, 2)   # insert 2 columns at column 3
ws.delete_cols(3, 1)   # delete 1 column starting at column 3
ws.column_dimensions['C'].hidden = True  # hide column C
```

### pandas Row/Column Operations

```python
import pandas as pd

df = pd.read_excel("data.xlsx")

# Add/drop columns
df["Profit"] = df["Revenue"] - df["Cost"]
df.insert(2, "InsertedColumn", value=0)
df = df.drop(columns=["UnwantedColumn"])
df = df.rename(columns={"OldName": "NewName"})

# Add/drop rows
new_row = {"FieldA": "value", "FieldB": 100}
df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
df = df.drop(index=[0, 5])
df = df.reset_index(drop=True)
```

### Batch-Processing Example (pandas + openpyxl combined)

```python
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment

def process_excel(input_file, output_file):
    df = pd.read_excel(input_file)
    df = df.dropna(thresh=len(df.columns) * 0.5)
    cols_to_drop = [col for col in df.columns if "Unnamed" in str(col)]
    df = df.drop(columns=cols_to_drop)
    if "Revenue" in df.columns and "Cost" in df.columns:
        df["Profit"] = df["Revenue"] - df["Cost"]
        df["ProfitMargin"] = (df["Profit"] / df["Revenue"] * 100).round(2)
    df.to_excel(output_file, index=False)

    wb = load_workbook(output_file)
    ws = wb.active
    for col in ws.columns:
        lengths = []
        needs_wrap = False
        for cell in col[:501]:
            s = str(cell.value or "")
            if len(s) > 40:
                needs_wrap = True
            lengths.append(min(len(s), 100))
        lengths.sort()
        p95 = lengths[int(0.95 * (len(lengths) - 1))] if lengths else 0
        width = max(8, min(p95 + 2, 40))
        col_letter = col[0].column_letter
        ws.column_dimensions[col_letter].width = width
        if needs_wrap:
            for cell in col[1:501]:
                cell.alignment = Alignment(wrap_text=True)
    wb.save(output_file)
```
