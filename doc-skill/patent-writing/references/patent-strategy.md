# Patent Portfolio Strategy and Planning

From protecting a single technical solution to planning an overall patent portfolio, this document covers the core methodology of patent strategy: portfolio strategy planning, design-around analysis, and FTO (freedom to operate) assessment.

---

## Table of Contents

- [Patent Portfolio Strategy Planning](#patent-portfolio-strategy-planning)
- [Design-around Analysis](#design-around-analysis)
- [FTO Freedom-to-Operate Analysis](#fto-freedom-to-operate-analysis)
- [Patent Portfolio Management](#patent-portfolio-management)

---

## Patent Portfolio Strategy Planning

The goal of a patent portfolio strategy is to maximize protection coverage of the technical solution with a limited number of patents. A good portfolio not only protects your own products but also constrains competitors' room to act.

### The Dimension-Decomposition Method

Decompose the technical solution along different dimensions, and for each dimension consider whether it is worth filing a separate patent:

| Decomposition dimension | Description | Example |
|---|---|---|
| **Core algorithm/method** | The core steps for achieving the goal | A data processing method based on XX |
| **System architecture** | How the modules are combined | A data processing system comprising XX and YY |
| **Data structure/format** | A unique way of organizing data | A data index structure for XX |
| **Pre-processing/post-processing** | Auxiliary steps before and after the core workflow | A data pre-processing method for XX |
| **Interface/interaction** | The way of interacting with external systems or users | An interaction control method for XX |
| **Optimization/improvement** | Performance optimization of the basic solution | A method for improving the efficiency of XX |
| **Application scenario** | The core solution applied to a specific scenario | A medical diagnosis method based on XX |
| **Hardware/apparatus** | The hardware form that executes the solution | An XX processing apparatus |

Not every dimension needs a separate application. The criterion for judgment is: **Does the solution for this dimension have independent commercial value or serve to block competitors?**

### Choosing a Portfolio Strategy

Choose a suitable portfolio strategy according to the enterprise's goals and resources:

**Offensive Portfolio**
- Goal: prevent competitors from entering the technical field
- Approach: file densely around the core technology, covering all feasible implementation paths
- Applicable: during a phase of technical leadership, or in fields with high technical barriers

**Defensive Portfolio**
- Goal: protect your own products from infringement accusations
- Approach: focus on protecting the technical solutions actually used in the product, and accumulate bargaining chips for cross-licensing
- Applicable: technology followers, or fields with high intellectual-property risk

**Reserve Portfolio**
- Goal: stake out positions in advance and pave the way for future technology roadmaps
- Approach: file in advance for technical directions that may be used in the future
- Applicable: when the technology roadmap is not yet clear but the directional judgment is clear

### Portfolio Planning Output

When developing a portfolio plan for the user, output the following content:

```
## Patent Portfolio Plan

### Overview of the Technical Solution
[Briefly describe the core technical solution and technical advantages]

### Portfolio Objective
[Offensive/defensive/reserve, and the specific objective]

### Patent Application List

| No. | Application subject | Protection dimension | Priority | Relationship to the core patent |
|------|---------|---------|-------|----------------|
| 1    | ...     | Core algorithm | High  | Core patent     |
| 2    | ...     | System architecture | High | Core patent     |
| 3    | ...     | Pre-processing | Medium | Peripheral patent |
| ...  | ...     | ...     | ...   | ...            |

### Recommended Filing Order
[Which to file first, which can be filed later, and why]

### Risk Notes
[Weak links in the portfolio and points that require attention]
```

---

## Design-around Analysis

Design-around means achieving a similar or equivalent technical effect without infringing others' patents. The reverse of design-around analysis also holds: analyze how others might design around your own patents, so you can plug the gaps when building the portfolio.

### Analysis Framework

#### Step 1: Parse the Claims of the Target Patent

Break the independent claim down into its individual technical features:

```
Claim 1: An XX method, comprising:
  Feature A: ...
  Feature B: ...
  Feature C: ...
  characterized in that:
  Feature D: ...
  Feature E: ...
```

#### Step 2: Analyze the Design-around Possibility Feature by Feature

Assess whether each technical feature can be designed around:

| Feature | Design-around possibility | Design-around approach | Does it affect the technical effect? |
|---|---|---|---|
| Feature A | Low | A general means, hard to design around | - |
| Feature B | Medium | Can be replaced with XX | Effect essentially unchanged |
| Feature C | High | The step can be omitted | Effect slightly reduced but acceptable |
| Feature D | High | Can use a completely different YY solution | Effect may be even better |
| Feature E | Low | No effective alternative | - |

#### Step 3: Design the Design-around Solution

Infringement determination follows the "all-elements rule"—infringement is constituted only when the accused solution contains all the technical features of the claim. Therefore, as long as any one technical feature is missing (or substantively replaced), infringement may not be constituted.

The design-around solution must achieve:
1. At least one technical feature differs from the claim
2. This difference does not constitute an "equivalent feature"—i.e., it does not use substantially the same means to perform substantially the same function to achieve substantially the same effect
3. The designed-around solution can still achieve the commercial objective

#### Step 4: Assess the Risk of Infringement Under the Doctrine of Equivalents

Even if the claim is literally designed around, you still need to assess whether there is a risk of "infringement under the doctrine of equivalents". The criteria for equivalence:

- **Are the means substantially the same?** Using a different technology to implement the same function
- **Is the function substantially the same?** Does the alternative play the same role in the system?
- **Is the effect substantially the same?** Is the technical effect ultimately achieved comparable?

If all three are "substantially the same", then even if it is literally different, it may still be found to infringe under the doctrine of equivalents.

### Anti-design-around Analysis of Your Own Patent

When drafting your own patent, examine the claims from the perspective of someone designing around them:

1. For each feature in the independent claim, can a competitor find an alternative?
2. If so, is that alternative covered in a dependent claim?
3. Is the generalization of the independent claim broad enough to cover the main equivalent implementations?

---

## FTO Freedom-to-Operate Analysis

FTO (Freedom to Operate) analysis assesses whether a product or technical solution infringes others' valid patent rights.

### Analysis Process

#### Step 1: Define the Scope of Analysis

- **Product/technical solution**: What is the specific technical solution to be assessed? Be precise down to the level of technical features
- **Target market**: In which countries/regions will the product be sold or used? Patent rights in different regions are independent
- **Time frame**: When will the product launch? You need to consider currently valid patents, as well as applications that are published but not yet granted

#### Step 2: Identify Relevant Patents

Based on the key features of the technical solution, determine the scope of patents to be screened:

- Search by technical keywords (in a web-chat scenario, you can help the user develop a search strategy, with the user performing the search)
- Search by technical classification number
- Search by competitor name
- Pay attention to frequently cited patents in the same field

#### Step 3: Assess the Risk of Infringement

Perform an infringement comparison for each relevant patent:

```
| Patent no. | Patentee | Key points of the independent claim | Infringement risk | Risk analysis |
|--------|-------|---------|---------|---------|
| CN...  | XX Corp. | An ...  | High/Medium/Low | The product solution contains all features of the patent / feature X can be designed around |
```

Risk-level judgment:
- **High risk**: The product solution fully covers the claim, with no obvious room to design around
- **Medium risk**: There is partial overlap, or it may constitute infringement under the doctrine of equivalents
- **Low risk**: There are clear distinguishing features, and no equivalence is constituted

#### Step 4: Risk-Response Recommendations

For the identified risk patents, give response recommendations:

| Response strategy | Applicable scenario |
|---|---|
| Design around | There is a technically feasible alternative |
| Apply for a license | Cannot design around, but the licensing cost is acceptable |
| Cross-license | You hold a patent the other party needs, so you can exchange |
| File for invalidation | The risk patent itself has novelty/inventive-step defects |
| Wait for expiry | The risk patent is close to expiry |

### FTO Report Output Format

```
## FTO Analysis Report

### Subject of Analysis
[Description of the product/technical solution]

### Scope of Analysis
[Target market, time frame, search strategy]

### List of Risk Patents
[Categorized list of high-risk/medium-risk/low-risk patents]

### Detailed Analysis of High-risk Patents
[Analyze the infringement risk and design-around possibility for each]

### Response Recommendations
[Specific action plans arranged by priority]

### Conclusion
[Overall risk assessment and recommendations]
```

---

## Patent Portfolio Management

### Portfolio Assessment Dimensions

When the user needs to assess an existing patent portfolio, analyze it from the following dimensions:

| Dimension | Focus |
|---|---|
| **Coverage** | Are all core technical solutions covered by patents? Are there any protection gaps? |
| **Layering** | Is there a layered structure of core patents + peripheral patents? Do the dependent claims provide sufficient fallback positions? |
| **Diversity** | Does it cover multiple types such as method, apparatus, and system? |
| **Validity** | Are the patents still within their term? Are the maintenance fees paid on time? |
| **Quality** | Are the claims clear, and is the scope of protection reasonable? |

### Portfolio Optimization Recommendations

Based on the assessment results, give specific optimization directions:

- **Fill the gaps**: Identify key technical points that are not protected, and recommend new applications
- **Strengthen weak links**: For patents with a scope of protection that is too narrow, consider filing new applications to supplement them
- **Prune low-value patents**: For patents whose scope of protection has already been designed around or whose technology is obsolete, consider abandoning them to save maintenance costs
- **Watch expiry dates**: For core patents approaching expiry, is there a follow-on patent to carry the baton?
