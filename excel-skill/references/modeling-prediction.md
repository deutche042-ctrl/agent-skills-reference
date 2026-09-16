# Prediction Modeling — Execution Flow

Complete predictive modeling following the steps below. At each step, write code tailored to the user's specific data.

---

## Step 1: Determine the Prediction Type

Choose the route based on the nature of the target variable Y:

- **Y is a continuous value** (sales, amount, temperature…) → regression prediction
- **Y is binary** (yes/no, churn/retain…) → binary classification prediction
- **Y is multi-class** (tier, category…) → multi-class classification prediction
- **Y is ordered over time and the user cares about trend/extrapolation** → time-series prediction

If there is a clear time column and the user asks to "predict the next N periods", prefer the time-series route.

## Step 2: Identify Grouping Dimensions

If the data has grouping dimensions (e.g. city, product line, store), decide:
- Does the user need predictions **per group**? (e.g. "predict future sales for each city")
- If so, model each group independently, or add group features and model them jointly

## Step 3: Data Preprocessing

1. **Missing values**: fill with median/mode when the missing rate is <5%; use related columns to assist filling for 5–30%; convert to an "is-missing" flag or drop for >30%
2. **Categorical encoding**: use label encoding for ordinal categories; one-hot for nominal categories (cardinality <10) or frequency encoding (cardinality ≥10)
3. **Time features**: if there is a date column, extract year/month/quarter/day-of-week; construct lag features and rolling means
4. **Numeric standardization**: linear models need standardization; tree models do not
5. **Train/test split**: 80/20 random split for ordinary data; split time-series data in chronological order — do not shuffle

## Step 4: Modeling (compare at least 2 methods)

### Regression Prediction

| Method | Applicable scenario | Key parameters |
|------|---------|---------|
| Linear regression | Baseline, interpretable | No tuning needed |
| Ridge/Lasso | Multicollinearity, feature selection | alpha |
| Random Forest | Non-linear, feature interactions | n_estimators, max_depth |
| XGBoost | Pursue accuracy | learning_rate, max_depth, n_estimators |

### Classification Prediction

| Method | Applicable scenario | Key parameters |
|------|---------|---------|
| Logistic regression | Baseline, interpretable | max_iter |
| Random Forest | Complex features | n_estimators |
| XGBoost | Pursue accuracy | learning_rate, max_depth |

When samples are imbalanced (positive:negative > 1:5): use `class_weight='balanced'` or `scale_pos_weight`.

### Time Series

| Method | Applicable scenario |
|------|---------|
| Lag features + XGBoost | Preferred when there are multiple external features |
| ARIMA/SARIMA | Univariate, with trend and seasonality |
| Exponential smoothing (ETS) | Short-term, stable patterns |

Key time-series note: the split must be in chronological order, not random.

## Step 5: Evaluation

Compute metrics for each model and summarize them in a comparison table:

- **Regression**: RMSE, MAE, R², MAPE
- **Classification**: Accuracy, Precision, Recall, F1, AUC
- Compare train vs. test metrics to check overfitting
- Do 5-fold cross-validation (use TimeSeriesSplit for time series)

## Step 6: Mandatory Deliverables

The following must not be omitted, even if the user did not request each one explicitly:

1. **Feature-importance ranking table**: list the importance/coefficient of all features, sorted by influence from high to low
2. **Model-evaluation metrics table**: metric comparison across models (a simple table suffices)
3. **Prediction result table**: if the user asks to predict future values, you must give a concrete predicted-value table. If the data has grouping dimensions (city/product/store), output the prediction table by group × time
4. **Trend chart**: a trend comparison of historical values + predicted values. If there are grouping dimensions, draw a grouped trend chart (one line per group, or facets)

Charts as needed:
- Regression: actual vs. predicted scatter plot, residual distribution plot
- Classification: confusion-matrix heatmap, ROC curve
- Time series: historical trend + prediction curve

## Step 7: Conclusion Distillation

Based on the modeling results, you must clearly answer the following questions (choose those applicable to the scenario):

- **Core drivers**: what are the top 3–5 factors that affect Y the most? What is the direction and magnitude of each factor's effect? How to interpret it in business terms?
- **Prediction conclusion**: what is the predicted trend for the next N periods? Growth or decline? Is the growth rate changing? If there are groups, which grow fastest/slowest?
- **Risks and opportunities**: what risks (e.g. sales decline in a certain city) or opportunities (e.g. strong growth in a certain category) do the predictions expose?
- **Recommended actions**: based on the predictions, what should the user focus on and prioritize investing in?

Example conclusion: "The forecast shows the Beijing market will reach 12,500 units in 2025 (+18% YoY), while the Shanghai market slows to 3% growth. The core factors driving growth are promotion frequency (importance 0.32) and seasonality (0.24). We recommend increasing promotion investment in Beijing in Q2–Q3, and investigating the cause of Shanghai's weak growth."

## Common Pitfalls

- Feature-engineering `fit` may only be done on the training set, then `transform` the test set
- Features must not include columns directly derived from Y (e.g. if Y is revenue, features must not include profit = revenue − cost)
- Time-series data must never be split randomly
- A negative R² means the model is worse than predicting the mean; check the features or switch methods
- If there are grouping dimensions, the prediction results must be broken out by group — don't just give the aggregate value
