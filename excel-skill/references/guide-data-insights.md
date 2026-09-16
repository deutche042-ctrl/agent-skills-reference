# Data Insights (excel-data-insights)

The core value of this skill is to **distill insights from data** — discover patterns, pinpoint problems, and give recommendations.

Specific capabilities include:
- **Descriptive analysis**: What is the current state of the data? How are the key metrics performing?
- **Diagnostic analysis**: Why is this happening? What is the root cause of an anomaly?
- **Trend and comparative analysis**: How does it change over time? What differences exist across dimensions?
- **Prediction and recommendations**: What might the future look like? What action should be taken?

During analysis you may need light data cleaning (e.g. handling missing values, format conversion) — this is part of the insight work, just do it. If the user's core need is complex data processing (e.g. large-scale table merges, complex ETL), that is out of scope for this scenario.

## Workflow

Flexibly choose and combine the steps below based on the specific task; you do not have to perform all of them every time.

### 1. Requirement Understanding

- Understand the user's business context and analysis goal: What do they want to know? What problem do they want to solve?
- Clarify the key metrics, analysis dimensions, time range, and comparison baseline
- Confirm the deliverable form (report, chart, data table, interactive HTML, etc.)

### 2. Data Acquisition and Understanding

- **Excel/CSV files**: run `scripts/preview_excel_rows.py` to preview the first 15 rows
  - Reads the active sheet by default; use the `--sheet` argument when the user specifies a sheet name
  - Output includes: a data-preview table, a list of non-empty columns, and the total row count
  - For more Excel operation methods see `references/ref-xlsx-workflow.md`
- Focus on understanding: the business meaning of each field, its data type, value range, and data quality

### 3. Requirement–Data Calibration

- **Understand the metric definitions in the requirement deeply**: Is the "revenue" the user mentioned tax-inclusive or tax-exclusive? What is the definition of an "active user"?
- **Verify against the data**: don't guess meaning from field names alone; look at actual data samples to confirm
- **Establish a mapping**: which fields each analysis metric corresponds to and how it is computed
- If there is ambiguity, confirm with the user before continuing

### 4. Analysis Execution

Choose an appropriate analysis method based on the requirement:

- **Descriptive statistics**: mean, median, distribution, frequency, and other basic profiling
- **Grouped aggregation and comparison**: break metrics down by dimension to find differences and patterns
- **Time-trend analysis**: year-over-year, period-over-period, moving average, seasonality detection
- **Anomaly detection**: outlier identification, volatility attribution, root-cause location
- **Correlation analysis**: association relationships between variables
- **Predictive modeling**: use appropriate methods as the business requires (e.g. time series, regression)

During analysis, be sure to record:
- The calculation caliber and formula of key metrics
- The data filtering conditions and their impact (sample-size change before vs. after filtering)
- How outliers were handled and the rationale

### 5. Deliverable

**Deliverable content** (choose based on analysis depth and user needs):
- **Core conclusions**: the most important findings, summarized in concise language
- **Analysis process**: key steps, computation logic, filtering conditions
- **Visualization charts**: intuitively show trends, comparisons, distributions, etc.
- **Action recommendations**: concrete, data-based recommendations that are actionable and prioritized

**Format spec**:
- **Charts**: PNG format, clearly labeled with title, axes, units, and legend
- **Data tables**: Excel format, including field descriptions
- **Analysis report**: Markdown or Word format, clearly structured
- **Interactive content** (optional): HTML format, openable directly in a browser

**Pre-delivery confirmation**:
1. Conclusions are supported by data and the computation logic is correct
2. Metric calibers are consistent throughout
3. Charts are clear and readable, and the report structure is coherent
4. Recommendations are concrete and feasible, with a clear implementation path

If the number of deliverables is ≥ 4, compress all files into a single archive before delivering.

## Analysis Quality Principles

- **Accuracy first**: better to say less than to say something wrong. Every conclusion must be backed by data.
- **Avoid superficiality**: don't just report numbers — explain what they mean; after "what is it", ask "why" and "what to do".
- **Mind caliber consistency**: the same metric must be computed the same way across different dimensions and time periods.
- **Distinguish fact from inference**: clearly mark which are facts directly reflected by the data and which are inferences and recommendations based on the data.
