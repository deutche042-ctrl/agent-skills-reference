# Numeric Computation & Processing (calculating-skills)

This skill provides a complete workflow and execution standard — from requirement understanding to result delivery — for complex computation tasks on structured data such as spreadsheets (e.g. Excel). The core goal is to ensure the computation logic is accurate, the process is robust, and the deliverables are professional and compliant.

## 1. Intent Understanding and Subject Mapping

The prerequisite for accurate computation is deep understanding of the requirement, not simple keyword matching.

1. **Two-way requirement–data calibration**: before starting a computation, you must cross-verify the user's text requirement against the provided data sample:
   - Analyze the requirement carefully and clarify the core analysis target (the "subject")
   - Inspect the data's column names and example rows to understand the actual business meaning of each field
   - Ensure the requirement matches the data structure, avoiding starting a computation based on a wrong understanding

2. **Precisely identify the analysis subject**: when the data contains multiple similar fields with different roles, you must use the surrounding context to map the analysis subject accurately to the corresponding field. This step is the basis for ensuring subsequent analysis revolves around the correct object.

## 2. Data Preprocessing

All computation must be based on clean, well-formed data. Before applying formulas, systematic data preprocessing must be completed.

1. **Probe analysis (for Excel attachments)**:
   - When the user's attachment is an Excel file (.xlsx, .xls), first run the probe script to obtain the data-structure information
   - Probe script location: `scripts/probe_excel.py`
   - Run command: `python scripts/probe_excel.py <excel_file_path>`
   - The probe output includes: all sheet names, each sheet's row and column counts, a preview of the first 15 raw rows, merged-cell ranges, the data-type distribution and missing-value statistics per column, and suspected total/subtotal special rows (`special_rows`)

2. **Identify and handle special summary rows**:
   - Identify rows containing keywords such as "Total / Grand Total / Subtotal / Summary / Cumulative" and confirm, together with the value distribution, whether they are of a summary caliber
   - By default exclude these summary rows during detail analysis / aggregation / modeling to avoid double counting; when they must be kept, output them separately and note the caliber

3. **Unify format and type**:
   - Inspect the columns participating in the computation and ensure consistent data types
   - Convert text-formatted numbers to numeric type
   - Unify differently written dates into standard datetime objects
   - For columns containing non-numeric characters (e.g. the units "pcs", "$"), extract the numeric part first, then compute

4. **Anomaly and missing-value handling**:
   - Identify anomalous entries in the data such as nulls (`null`), error markers (`#N/A`), etc.
   - Adopt an appropriate strategy based on business logic:
     - Fill with a neutral value (e.g. 0 or the mean)
     - Ignore anomalous records directly in aggregate computations
     - Mark anomalous values and explain them in the final result

5. **Compound-field splitting**:
   - Proactively identify and parse a single field that contains multiple pieces of information
   - For example, split a time-range field (e.g. `09:00-18:00`) into two independent fields, "start time" and "end time"
   - Ensure the split fields can be used directly in subsequent computation

## 3. Time and Date Handling

Time and date computation easily goes wrong due to format and logic issues; strictly follow the handling principles below.

1. **Use standardized time objects**:
   - Before any time-related operation (e.g. difference, comparison), ensure all operands have been converted to standard datetime objects
   - Fundamentally avoid computation errors caused by inconsistent text formats

2. **Interval parsing first**:
   - When encountering text representing a time period, strictly follow the "split first, then compute" principle
   - Parse the time period into two independent time points before computing duration or interval

3. **Output human-readable formats**:
   - When generating the final deliverable (especially when writing to Excel), ensure all datetime fields are presented in a human-readable format (e.g. `YYYY-MM-DD HH:MM`)
   - Avoid Excel's raw date serial-number format (i.e. the numeric day-count since the base date)
   - For format conversion, see `references/ref-xlsx-workflow.md`

## 4. Formula Design and Boundary Handling

Robust computation logic must cover both normal scenarios and boundary cases.

1. **Align logic with the business caliber**:
   - When designing computation formulas, strictly follow the clarified business caliber
   - For ratio metrics (e.g. completion rate, conversion rate), clearly define the exact numerator and denominator
   - When encountering special computation formulas (e.g. policy- or finance-related), call the `general_search` function to look up implementation details

2. **Zero-denominator fault tolerance**:
   - Before a division, you must check whether the denominator could be zero
   - Define a clear fallback output strategy: return 0, a null, or a specific marker text (e.g. `N/A`)
   - Avoid program interruption or misleading results such as infinity

3. **Null and extreme-value handling**:
   - In aggregate computations (e.g. average, sum), clarify the null-handling strategy:
     - Nulls that do not affect the computation and analysis are treated as 0
     - For nulls that do affect the computation and analysis, avoid the related computation and explain the null situation and handling plan in the output
   - Review the plausibility of the computed result and beware of distortion caused by extreme values

## 5. Delivery and Safety

1. **Separate result from process**:
   - The final deliverable must not contain any trace of the internal implementation process
   - Filter out thinking process, tool-call logs, intermediate code, or commands
   - Present only the clean, final computed result or conclusion

2. **Packaging and usability assurance**:
   - Determine the deliverable form based on the user's needs
   - Package all downloadable deliverables (e.g. reports, data files) through the proper channel
   - Ensure delivery links are valid and files open and work normally

3. **Format professionalism**:
   - Moderate table column widths
   - Consistent display of numbers, percentages, and dates
   - Ensure information is clear at a glance and easy to understand

## References

- Code references for Excel file read/write, time-format conversion, row/column operations, etc.: `references/ref-xlsx-workflow.md`
