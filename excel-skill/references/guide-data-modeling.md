# Quantitative Modeling (data-modeling)

This skill builds quantitative models from Excel/CSV data, supporting three decision scenarios: prediction, evaluation, and optimization.

## Way of Working

Work in three steps: understand the problem → execute the analysis → give conclusions.

### Step 1: Understand the Problem (OFACE framework)

After receiving a request, first use the OFACE framework to quickly organize the problem elements. The user will not supply more information; for missing items, make reasonable assumptions based on the data file and common sense.

**O — Objective**: determine the problem type

| Type | Signal words | Corresponding reference |
|------|--------|---------------|
| Prediction | predict, estimate, trend, future, forecast | `references/modeling-prediction.md` |
| Evaluation | evaluate, rank, score, rating, comprehensive assessment, select the best | `references/modeling-evaluation.md` |
| Optimization | optimize, optimal, maximize, minimize, allocate, planning | `references/modeling-optimization.md` |

**F — Frame (object and granularity)**: what the modeling object is, its granularity (entity × time × category), and whether there are exclusion rules. Infer from the data's row/column structure.

**A — Assets (data and variables)**: first read the data header and the first few rows to understand the data overview (sample size, column names, data types, missing situation), and identify the target variable Y and features X. For CSV files, mind encoding issues; try `utf-8`/`utf-8-sig` first, and fall back to other encodings if decoding fails.

**C — Criteria (evaluation criteria)**: choose default metrics based on problem type — RMSE/R² for regression, F1/AUC for classification, ranking robustness for evaluation, objective-function value for optimization. User-specified metrics take priority.

**E — Explain (explanation needs)**: what does the user want to understand? Factor importance, group differences, scenario simulation? By default, output at least a factor-importance ranking.

After organizing, briefly output to the user: the problem type, the list of key assumptions, and the planned methods.

### Step 2: Execute the Analysis

1. **Read the corresponding reference file** and complete the analysis following its execution flow (see the table above)
2. The reference provides execution steps and method guidance; based on it, write a Python script adapted to the user's data
3. When plotting, use a clear, readable font and make sure it supports all characters in your labels, so titles and labels display correctly
4. Save charts as PNG files

### Step 3: Give Conclusions

After modeling, **you must distill directly usable business conclusions from the results**. This is the most important part of the whole analysis — what the user wants is not tables and metrics, but "so what is the conclusion".

The last step of each reference, "Conclusion distillation", gives the conclusive questions that must be answered for that scenario; be sure to answer each one.

When answering:
- **Answer in business language**, not a pile of technical metrics. For example, "the biggest factor affecting sales is promotions, followed by unit price" rather than merely listing feature-importance values
- **Interpret with the charts**, pointing out the key information and noteworthy patterns in the figures
- **Give concrete numbers**: predicted values, ranking scores, optimal plans, etc. must all be given as concrete numbers — don't just say "higher" or "better"
- **Give actionable recommendations** that provide decision support based on the analysis results
- **List the assumptions**, marking which assumptions have a large impact on the conclusion

## Output Format

Reply in Markdown by default. If the analysis generates charts that need to be shown in the report, you may generate a self-contained HTML file with the images embedded as base64, viewable simply by opening it in the user's browser.

## Output Quality Requirements

- Code must be directly runnable; list any packages that need installing in comments at the top
- All charts must have titles, axis labels, and legends (in the output language)
- In the end you must **answer the user's question**, not just output the model and data and stop

## References

For detailed modeling methods see the reference files below (read the file corresponding to the problem type):
- Prediction scenario: `references/modeling-prediction.md`
- Evaluation scenario: `references/modeling-evaluation.md`
- Optimization scenario: `references/modeling-optimization.md`
