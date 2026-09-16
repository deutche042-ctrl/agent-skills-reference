# Evaluation Modeling — Execution Flow

Complete the multi-metric comprehensive evaluation following the steps below. At each step, write code tailored to the user's specific data.

---

## Step 1: Identify Metric Direction

Classify each evaluation metric in the data into three types:

| Type | Meaning | Example |
|------|------|------|
| Benefit-type (larger is better) | The larger the value, the better | Quality pass rate, revenue, satisfaction |
| Cost-type (smaller is better) | The smaller the value, the better | Unit price, response time, defect rate |
| Nominal-type (closer to a target is better) | An optimal value exists | pH (optimal 7), body temperature (optimal 36.5) |

The user usually hints which metrics are "the lower the better". If not hinted, judge by the metric's meaning.

For qualitative metrics (e.g. "yes/no", tier) quantify first: "yes"=1 / "no"=0, or encode tiers as numbers.

## Step 2: Positive-Orientation Processing

Unify all metrics into "larger is better":

- **Cost-type**: `x' = max(x) - x`
- **Nominal-type**: `x' = 1 - |x - best| / max(|x - best|)`

## Step 3: Choose a Weighting Method

```
Did the user specify weights or importance preferences?
├── Yes → use the user's weights directly (or quantify with AHP, only for ≤9 metrics)
├── No → objective weighting (entropy weight method recommended)
└── Want both → combined weighting (subjective weight × objective weight, then normalize)
```

### Entropy Weight Method (recommended default)

A metric with greater dispersion has stronger discriminating power and a higher weight.

Computation steps:
1. Min-max normalize to [0, 1]
2. Compute the proportion matrix p_ij = x_ij / Σx_ij
3. Information entropy e_j = -k × Σ(p × ln(p)), where k = 1/ln(n)
4. Weight w_j = (1 - e_j) / Σ(1 - e_j)

### CRITIC Method (alternative)

Considers both contrast intensity (standard deviation) and metric conflict (correlation coefficient). Suitable when metrics are correlated.

### AHP (when the user has preferences)

Build a pairwise comparison matrix (1–9 scale), solve for weights via the eigenvalue method, and check the consistency ratio CR < 0.1.

## Step 4: Comprehensive Evaluation (TOPSIS recommended)

TOPSIS is the most general comprehensive evaluation method:

1. Vector normalization: `r_ij = x_ij / sqrt(Σx_ij²)`
2. Weighting: `v_ij = w_j × r_ij`
3. Determine the positive-ideal solution V⁺ (max of each column) and the negative-ideal solution V⁻ (min of each column)
4. Compute distances: `D⁺ = sqrt(Σ(v_ij - V⁺_j)²)`, `D⁻ = sqrt(Σ(v_ij - V⁻_j)²)`
5. Composite score: `C = D⁻ / (D⁺ + D⁻)`, the closer to 1 the better

Note: cost-type metrics must be reversed when determining the ideal solution (the positive-ideal solution takes the minimum).

Alternative methods:
- **Grey relational analysis**: use when the sample size is small or the data is incomplete
- **RSR (rank-sum ratio) method**: statistics-oriented, based on ranks

## Step 5: Mandatory Deliverables

The following must not be omitted, even if the user did not request each one explicitly:

1. **Metric-direction table**: list each metric and its direction (benefit/cost/nominal) so the user can confirm how the metrics are handled
2. **Weight table**: list each metric's weight (and an explanation of the weighting method); if using the entropy weight method, attach the intermediate information-entropy values
3. **Composite ranking table**: list the composite score and final rank of all evaluation objects, and state the ranking caliber (e.g. "based on the entropy-weight-TOPSIS method; higher score is better")
4. **Recommendation and rationale for the top-ranked**: explain why they rank at the top using the specific metric data

Mandatory charts:
- **Composite-score ranking bar chart** (horizontal bar chart, scores arranged from high to low)
- **Metric-weight distribution chart** (bar chart or pie chart)

Charts as needed:
- **Radar chart**: compare how the top-ranked and bottom-ranked differ across dimensions
- **Heatmap**: normalized scores of all objects across all metrics

## Step 6: Conclusion Distillation

Based on the evaluation results, you must clearly answer the following questions:

- **Final recommendation**: who ranks first in the comprehensive evaluation? What is the rationale (using specific metric data)?
- **Tier division**: into how many tiers can all evaluation objects be divided? What are the dividing lines and characteristics of each tier? (e.g. "the first tier scores >0.7, 3 in total, superior to the mean on both quality and price")
- **Strengths/weaknesses of each object**: what are the respective strengths and weaknesses of the top-ranked? (e.g. "supplier A has the best quality but a longer delivery cycle")
- **Key differentiating factors**: which metrics have the largest weight and best discriminate quality? Which metrics differ little across objects and have weak discriminating power?
- **Recommended actions**: based on the ranking, how should the user choose or adjust?

Example conclusion: "The comprehensive evaluation recommends supplier A (score 0.84); its quality pass rate of 98.9% is the highest in the field and its unit price of $28 is the lowest, giving it a significant overall advantage. Supplier B ranks second (0.71), with an advantage in delivery speed but a price 15% higher. We recommend A as the primary supplier and B as an emergency backup. The largest-weight metrics are quality pass rate (0.35) and unit price (0.28), together contributing 63% of the evaluation weight."

## Common Pitfalls

- Forgetting to positively orient cost-type metrics will invert the ranking
- Metrics with different units must be normalized first
- Two highly correlated metrics (r > 0.9) will double-count the weight; consider merging them
- When there are < 5 evaluation objects, the ranking has limited statistical significance
- You must clearly state the ranking caliber and evaluation method so the user knows how the ranking was derived
