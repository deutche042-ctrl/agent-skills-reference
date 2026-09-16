# Data Mining (data-digging)

This skill provides a complete execution framework for data-mining tasks, guiding the whole process from problem definition to result delivery, ensuring the analysis is accurate, deep, and professional. Through a systematic workflow and quality-control mechanisms, it helps the analyst effectively handle all kinds of data-mining tasks and discover valuable patterns, relationships, and insights from data.

## Quick Decisions

Before starting a data-mining task, quickly make the following key decisions:

- **Clarify the mining goal**: determine the specific analysis direction, e.g. correlation analysis, predictive modeling, clustering analysis, etc.
- **Identify data needs**: clarify the required data type, scale, and quality requirements
- **Choose the method path**: select an appropriate mining method based on the goal and data characteristics
- **Plan the deliverable form**: determine the form and content requirements of the final deliverable

## Workflow

### 1. Problem Analysis and Goal Definition

- **Requirement clarification**: deeply understand the user's problem and needs, and clarify the mining goal and expected output
- **Scope definition**: determine the time range, geographic range, and data range of the analysis
- **Success criteria**: define concrete metrics that measure the success of the mining results
- **Constraint identification**: identify constraints in time, data, technology, etc.

### 2. Data Acquisition and Preprocessing

- **Data collection**: identify and obtain the required data sources, and assess data quality and completeness
- **Data cleaning**: handle missing values, outliers, and duplicates; unify data formats and units; resolve data inconsistencies
- **Data transformation**: perform feature engineering (create derived variables), data standardization/normalization, and necessary dimensionality reduction

### 3. Exploratory Data Analysis

- **Descriptive statistics**: compute basic statistics to understand the distribution characteristics of the data
- **Visual analysis**: use various charts to explore patterns and anomalies in the data
- **Correlation analysis**: identify relationships and dependencies between variables
- **Data-quality assessment**: assess the data's suitability for the mining task

### 4. Mining Method Selection and Implementation

- **Method selection**: select a suitable mining algorithm based on the analysis goal, while assessing the algorithm's assumptions and applicable scope, and considering computational resources and time limits

**Choose the method by task type**:

| Task type | Recommended methods | Applicable scenario |
|---------|---------|---------|
| Descriptive mining | K-means / DBSCAN / hierarchical clustering | Discover natural groups in the data |
| Association rules | Apriori, FP-Growth | Discover association rules among data |
| Anomaly detection | Isolation Forest, LOF, 3σ/IQR | Identify outliers |
| Classification prediction | Random Forest, XGBoost, logistic regression | Predict discrete labels |
| Regression prediction | Linear regression, Ridge/Lasso, random forest regression | Predict continuous values |
| Time series | ARIMA/SARIMA, Prophet, lag features + XGBoost | Predict time-series data |
| Text mining | LDA/NMF (topics), dictionary/SVM (sentiment classification) | Structure text semantics |

**Adjust by data characteristics**:

| Data characteristic | Recommended adjustment |
|---------|---------|
| High-dimensional data | PCA reduction or t-SNE visualization; mind the curse of dimensionality |
| Imbalanced data | SMOTE oversampling or `class_weight='balanced'`; adjust evaluation metrics |
| Time-series data | Must split in chronological order; random shuffle is forbidden |
| Sparse data | Prefer linear or tree models; prevent overfitting |

- **Model building**: data splitting (train/validation/test set), model hyperparameter tuning, and cross-validation (K-fold; use TimeSeriesSplit for time series)
- **Model evaluation**:

| Model type | Evaluation metrics |
|---------|---------|
| Classification model | Accuracy, precision, recall, F1, AUC-ROC |
| Regression model | RMSE, MAE, R², MAPE |
| Clustering model | Silhouette coefficient, Davies-Bouldin index |
| Association rules | Support, confidence, lift |

Explain the business meaning of the model results, and compare train vs. test metrics to check for overfitting.

### 5. Result Validation and Interpretation

- **Result validation**: verify the consistency and reliability of the results, perform sensitivity analysis, and test the generalization of the results across different datasets
- **Result interpretation**: explain the business significance of the mining results, identify key influencing factors and patterns, and provide actionable insights and recommendations
- **Uncertainty analysis**: assess the confidence level of the results and identify potential biases and risks

### 6. Visualization and Report Generation

- **Result visualization**: choose an appropriate chart type (e.g. scatter plot, heatmap, dendrogram, network graph, etc.), and ensure charts are clear, attractive, and informative, avoiding overlapping text or chaotic layouts
- **Report writing**: ensure a clear structure and coherent logic with sufficient depth, avoiding superficial analysis, and present the necessary charts and data as required
- **Deliverable preparation**: prepare the main report (including method, results, conclusions), data files (processed data, model outputs), and code and documentation (analysis scripts, model descriptions)

### 7. Quality Control and Review

- **Data-accuracy check**: verify the accuracy of data statistics and computations, cross-validate key results, and ensure data identifiers and labels are correct
- **Method-rigor check**: avoid using unverified assumptions, ensure the analysis method is scientific and reasonable, and provide the rationale and explanation for the method choice
- **Result-consistency check**: verify the results are consistent with business logic, check the consistency of results across different analysis methods, and ensure conclusions have sufficient data support

## Common Problems and Solutions

### Data-Accuracy Problems

- Establish a data-validation process and cross-check key data; use automated scripts to verify data computations
- Keep detailed records of data sources and the processing procedure; implement a multi-level review mechanism

### Analysis-Method Problems

- Clarify the rationale and assumptions of the method choice; use multiple methods for cross-validation
- Perform model evaluation and validation; refer to domain best practices and standard methods

### Visualization and Format Problems

- Follow data-visualization best practices; use professional visualization tools and templates
- Ensure chart elements are clear and readable; unify document format and style

### Content-Quality Problems

- Develop a detailed analysis plan and depth requirements; analyze data from multiple angles to mine deep relationships
- Combine business knowledge to provide valuable insights; provide concrete, actionable recommendations

## Quality Requirements

- **Data integrity**: ensure the data is complete and accurate and the processing is traceable
- **Method rigor**: use scientific, reasonable analysis methods and avoid subjective assumptions
- **Result reliability**: ensure the analysis results are reliable and consistent, with sufficient data support
- **Report professionalism**: a clear report structure with sufficient depth and a well-formatted, attractive layout
- **Delivery completeness**: provide all necessary deliverables as required

## References

- Visualization best practices: `references/ref-visualization.md`
- Analysis-report template: `references/template-report.md`
