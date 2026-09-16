# Data Analysis Report Template

> **Usage**: this template applies to various analysis tasks such as data insights, semantic analysis, and data mining; adjust the sections flexibly based on actual needs. Data-mining tasks should keep the "V. Model Building and Evaluation" section; descriptive-analysis tasks may omit it.

---

# Executive Summary

## Analysis Background and Objective
- **Analysis purpose**: briefly state the core problem this analysis solves or the goal it achieves
- **Business background**: describe the business scenario and relevant background
- **Analysis scope**: clarify the data range, time range, business domain, etc. covered

## Key Findings
> Summarize the most important findings in 3-5 points; each finding should include data support, and each point should be no fewer than 300 words

1. **Finding 1**: brief description, e.g. "Metric A grew X% over the previous period, driven mainly by factor B"
2. **Finding 2**: brief description, e.g. "Group C and group D differ significantly on metric E (p<0.05)"
3. **Finding 3**: brief description, e.g. "Factor F is strongly positively correlated with result G (r=0.85)"

## Main Recommendations
> 2-3 actionable recommendations based on the findings

1. **Recommendation 1**: specific action and expected effect
2. **Recommendation 2**: specific action and expected effect

---

# I. Data Description

## 1.1 Data Source
| Item | Description |
|------|------|
| **Data source** | Collection channel or system name |
| **Data provider** | Providing department or individual |
| **Collection time** | Specific time of data collection |
| **Report date** | Date this report was generated |

## 1.2 Data Scale
| Metric | Value | Description |
|------|------|------|
| **Total records** | X | Total raw data volume |
| **Valid records** | Y | Records used for analysis after cleaning |
| **Number of fields** | Z | Number of fields/variables included |
| **Time span** | start date - end date | Time range the data covers |
| **Data completeness** | XX% | Proportion of key fields with no missing values |

## 1.3 Field Description

### Key Field Definitions

| Field name | Data type | Definition | Value range/example | Missing rate |
|----------|----------|----------|---------------|--------|
| Field A | Numeric | Business meaning of field A | 0-100 | 0% |
| Field B | Categorical | Business meaning of field B | Category1/Category2/Category3 | 2% |
| Field C | Date | Business meaning of field C | YYYY-MM-DD | 0% |

### Derived Field Description
> Computed fields created during analysis

| Field name | Formula | Business meaning |
|----------|----------|----------|
| Derived field X | Field A / Field B | Unit cost |
| Derived field Y | (Field C - Field D) / Field D | Growth rate |

## 1.4 Data Quality Assessment

| Problem type | Problem description | Impact | Handling method | Post-handling status |
|----------|----------|----------|----------|------------|
| Missing values | Field A missing rate 5% | Medium | Mean imputation | Handled |
| Outliers | Field B has 3 extreme values | Low | Kept and annotated | Annotated |
| Duplicate records | 10 duplicate records found | Low | Removed duplicates | Handled |
| Inconsistent format | Date field format not unified | Medium | Unified format | Handled |

**Data limitations**: sample bias notes, data timeliness, key-field missing constraints.

---

# II. Analysis Method

## 2.1 Analysis Framework
```
Problem definition → Data preprocessing → Exploratory analysis → Model building (mining tasks) → Result interpretation → Business recommendations
```

## 2.2 Statistical Method Description

### Descriptive Statistics
| Statistic | Method | Applicable scenario |
|--------|----------|----------|
| Central tendency | Mean, median, mode | Distribution center of numeric variables |
| Dispersion | Standard deviation, IQR, coefficient of variation | Dispersion of numeric variables |
| Frequency statistics | Count, percentage | Distribution of categorical variables |

### Inferential Statistics
| Analysis method | Applicable condition | Application scenario |
|----------|----------|----------|
| Pearson correlation | Continuous variables, linear relationship | Degree of linear correlation between variables |
| Spearman correlation | Ordinal variables or nonlinear relationships | Degree of monotonic correlation between variables |
| Independent-samples t-test | Two-group comparison, normal distribution | Test the difference in means between two groups |
| One-way ANOVA | Multi-group comparison, normal distribution | Test the difference in means across groups |
| Chi-square test | Categorical variables | Test the independence of categorical variables |

## 2.3 Analysis Tools
- **Data processing**: Python (pandas, numpy)
- **Statistical analysis**: Python (scipy, statsmodels, scikit-learn)
- **Visualization**: Python (matplotlib, seaborn, plotly)

---

# III. Data Exploration and Preprocessing

## 3.1 Data Overview

| Data type | Number of fields | Share | Example fields |
|----------|----------|------|----------|
| Numeric | X | XX% | Field A, Field B |
| Categorical | Y | YY% | Field C, Field D |
| Date | Z | ZZ% | Field E, Field F |

## 3.2 Descriptive Statistics Results

### Numeric Variable Statistics
| Field name | Sample size | Mean | Std dev | Min | Median | Max | Missing rate |
|----------|--------|------|--------|--------|--------|--------|--------|
| Field A | 1000 | 50.5 | 15.2 | 10 | 50 | 100 | 0% |

### Categorical Variable Statistics
| Field name | Category | Frequency | Percentage | Cumulative percentage |
|----------|------|------|--------|------------|
| Field C | Category1 | 400 | 40% | 40% |
| | Category2 | 300 | 30% | 70% |

## 3.3 Data Preprocessing Process

### Missing-Value Handling
| Field name | Missing rate | Handling method | Rationale |
|----------|--------|----------|----------|
| Field A | 5% | Mean imputation | Low missing proportion, randomly distributed |

### Outlier Handling
| Field name | Number of outliers | Detection method | Handling method |
|----------|------------|----------|----------|
| Field A | 3 | 3σ rule | Kept and annotated |

---

# IV. Analysis Results

## 4.1 Univariate Analysis

**[Figure 1: Key variable distribution analysis]** (histogram + box plot)
- Describe the distribution shape, central tendency, outliers, and business interpretation

## 4.2 Bivariate Analysis

**Correlation analysis**:

| Correlation coefficient | Value | p-value | Significance |
|----------|------|-----|--------|
| Pearson r | 0.75 | <0.001 | *** |

**[Figure 2: Scatter plot and regression line]**

**Group comparison analysis**:

| Group | Sample size | Mean | Std dev | Difference from population | Significance |
|------|--------|------|--------|------------|--------|
| Group 1 | 300 | 55.2 | 12.5 | +5.2 | p<0.01** |

## 4.3 Multivariate Analysis

**[Figure 3: Correlation heatmap]** (color intensity indicates correlation strength)

**Time trend** (if date data is available):

| Period | Mean | Period-over-period change | Trend |
|--------|------|----------|------|
| 2023Q1 | 45.2 | - | Baseline |
| 2023Q2 | 48.6 | +7.5% | Rising |

## 4.4 Segmentation Analysis

| Segment | Sample share | Metric A mean | Metric B mean | Rank |
|--------|----------|-----------|-----------|------|
| Segment 1 | 25% | 65.2 | 78.5 | 1 |
| Segment 2 | 30% | 58.7 | 72.3 | 2 |

---

# V. Model Building and Evaluation (section specific to data-mining tasks)

> Descriptive-analysis tasks may omit this section.

## 5.1 Method Selection

| Analysis stage | Method name | Method description | Application scenario | Parameter settings |
|----------|----------|----------|----------|----------|
| Exploratory analysis | Descriptive statistics | Compute basic statistics | Understand data distribution | - |
| Modeling stage | Random Forest | Decision-tree ensemble learning | Classification/regression | n_estimators=100 |
| Modeling stage | K-means | Distance-based clustering | Customer segmentation | n_clusters=3 |
| Evaluation stage | Cross-validation | Model performance evaluation | Verify model robustness | k=5 |

## 5.2 Model Evaluation

| Evaluation metric | Train set | Validation set | Test set | Note |
|----------|--------|--------|--------|------|
| Accuracy | XX% | XX% | XX% | Classification model |
| F1 score | XX | XX | XX | Classification model |
| RMSE | XX | XX | XX | Regression model |
| R² | XX | XX | XX | Regression model |
| Silhouette coefficient | XX | - | - | Clustering model |

- **Feature importance**: sorted by influence from high to low, explaining the business meaning of key features
- **Error analysis**: analyze the patterns and main causes of prediction errors
- **Overfitting check**: compare the metric gap between train set vs. test set

## 5.3 Model Comparison
- **Comparison across models**: compare the performance metrics of multiple candidate models
- **Basis for final model choice**: a combined consideration of accuracy, interpretability, and computational cost

---

# VI. Key Findings and Insights

## 6.1 Summary of Core Findings

### Finding 1: [specific finding title]
- **Finding description**: detailed description with data support and statistical significance
- **Data evidence**: key metric XX, changed YY% from baseline; p-value < 0.05
- **Business meaning**: significance and impact on the business
- **Recommended action**: specific action based on this finding

## 6.2 Pattern Recognition
Describe the patterns or regularities identified in the data, explaining the detection method, applicable scope, and business application value.

## 6.3 Anomaly Identification
Describe the anomalous behavior, possible causes, and handling recommendations.

---

# VII. Conclusions and Recommendations

## 7.1 Main Conclusions

| Conclusion | Supporting evidence | Confidence |
|------|---------|---------|
| Conclusion 1 | Statistical result XX, Figure X | High/Medium/Low |
| Conclusion 2 | ... | ... |

## 7.2 Business Recommendations

### Short-term recommendations (1-3 months)
1. **Recommendation 1**: specific action plan, expected effect XX, implementation difficulty Low/Medium/High, priority P0/P1/P2

### Mid-term recommendations (3-6 months)
1. **Recommendation 1**: specific action plan, key milestones

### Long-term recommendations (6-12 months)
1. **Recommendation 1**: strategic-level recommendation, resource needs

## 7.3 Risk Warnings

| Risk | Level | Description | Mitigation |
|------|------|------|---------|
| Risk 1 | High/Medium/Low | Detailed description | Mitigation strategy |

## 7.4 Recommendations for Further Analysis
1. Direction 1: analysis purpose, required data, expected output
2. Direction 2: ...

---

# VIII. Analysis Limitations

- **Data limitations**: sample bias, timeliness, field-missing issues, etc.
- **Method limitations**: whether statistical assumptions are met, the applicable scope of the method
- **Conclusion limitations**: applicable conditions, confidence level, external validity
- **Improvement directions**: suggestions to improve data quality, follow-up validation methods

---

# Appendix

## Appendix A: Detailed Data Tables
> Complete statistical result tables, cross-tabulations, and other detailed data

## Appendix B: Supplementary Charts
> Charts not shown in the main text but of reference value

## Appendix C: Analysis Code
> Code snippets of the key analysis

## Appendix D: Glossary
| Term | Definition |
|------|------|
| Term A | Definition A |

---

# Report Information

| Item | Content |
|------|------|
| **Report title** | [Data analysis report title] |
| **Report version** | V1.0 |
| **Generated date** | YYYY-MM-DD |
| **Analyst** | [Analyst name] |
| **Data cutoff date** | YYYY-MM-DD |

> **Disclaimer**: this report is derived from analysis of the available data; the conclusions are for reference only. Actual decisions should be judged comprehensively in light of the real business situation.
