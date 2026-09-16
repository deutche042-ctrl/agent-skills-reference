# Optimization Modeling — Execution Flow

Complete optimization modeling following the steps below. At each step, write code tailored to the user's specific data.

---

## Step 1: Identify the Optimization Problem Structure

Extract the three elements from the user's description and the data:

| Element | Question | Example |
|------|------|------|
| Decision variables | What needs to be determined? | Output of each product, investment amount of each project |
| Objective function | What to optimize? Maximize or minimize? | Maximize total profit, minimize total cost |
| Constraints | What are the limits? | Resource caps, min/max output, budget |

## Step 2: Determine the Problem Type and Choose a Solver Method

```
Are the objective function and constraints all linear?
├── Yes → linear programming
│   ├── Continuous decision variables → LP (use PuLP)
│   ├── Decision variables must be integers → IP (use PuLP, cat='Integer')
│   └── Mixed → MIP (use PuLP)
└── No → nonlinear optimization (use scipy.optimize.minimize)
```

Most business problems (production planning, resource allocation, transportation scheduling) are linear programming.

## Step 3: Model and Solve

### Linear Programming (PuLP)

Modeling steps:
1. Create the problem: `prob = LpProblem("name", LpMaximize or LpMinimize)`
2. Define decision variables: `LpVariable("name", lowBound=lower, upBound=upper)`
3. Add the objective function: `prob += objective_expression`
4. Add constraints: `prob += constraint_expression, "constraint_name"`
5. Solve: `prob.solve(PULP_CBC_CMD(msg=0))`

Key notes:
- Use `PULP_CBC_CMD(msg=0)` to suppress solver output
- Use `cat='Integer'` for integer variables, `cat='Binary'` for 0-1 variables
- If there are "minimum output" and "maximum output", set them directly as the variable's lowBound and upBound
- The upper bound of a decision variable must consider multiple limits at once (e.g. min(max output, monthly average demand))

### Nonlinear Optimization (scipy.optimize)

```python
from scipy.optimize import minimize
result = minimize(objective_fn, x0=initial_point, method='SLSQP', bounds=variable_ranges, constraints=constraint_list)
```

Constraint format: `{'type': 'ineq', 'fun': lambda x: ...}` denotes an inequality constraint of the form >= 0.

## Step 4: Result Analysis

After solving, you must check:

1. **Solve status**: whether an optimal solution was found (LpStatus is 'Optimal')
2. **Value of each decision variable**: display in a list
3. **Optimal objective-function value**
4. **Constraint utilization**: which constraints are binding (resource exhausted) and which have slack (slack > 0)
5. **Sensitivity analysis** (as needed): how the optimal solution changes when key parameters vary by ±10%/20%

## Step 5: Mandatory Deliverables

The following must not be omitted, even if the user did not request each one explicitly:

1. **Mathematical-model description**: use concise text/formulas to state the objective function and main constraints so the user knows what model was built
2. **Optimal-plan table**: the value of each decision variable and the corresponding optimal objective value
3. **Constraint analysis**: which constraints are binding (bottleneck resources), what the resource utilization is, and how much slack remains
4. **Sensitivity note**: how the optimal solution changes when key parameters (e.g. the cap of a resource, a product's profit margin) vary

Mandatory charts:
- **Optimal-plan bar chart**: the value of each decision variable
- **Constraint-utilization chart**: horizontal bar chart, binding constraints in red

Charts as needed:
- Sensitivity-analysis line chart
- Pareto front (for multi-objective)

## Step 6: Conclusion Distillation

Based on the optimization results, you must clearly answer the following questions:

- **Optimal-plan summary**: state in one sentence what the optimal plan is and the objective value (e.g. "under the optimal production plan the total profit is $583k")
- **Resource bottlenecks**: which resources are bottlenecks (binding constraints)? If a bottleneck constraint is relaxed, by how much can the objective improve?
- **Plan characteristics**: what are the features of the optimal plan? Which decision variables hit their upper/lower bounds? Why?
- **Alternative-plan suggestions**: if the user has room to adjust some constraints (e.g. increase the budget, extend the schedule), give an "if… then…" comparison plan
- **Recommended actions**: based on the optimization results, what should the user execute first?

Example conclusion: "The optimal plan yields a total profit of $583k: produce 200 units of Product A, 150 units of Product B, and none of Product C. The bottleneck resource is machine hours (100% utilization), while raw materials are only 72% used. If machine hours increase by 10%, profit can rise to $631k (+8.2%); we recommend prioritizing capacity expansion."

## Common Pitfalls

- No feasible solution usually means contradictory constraints — check the data or relax constraints
- An unbounded solution usually means a missing constraint — check for omitted upper/lower bounds
- The upper bound of a decision variable must consider multiple limits at once (e.g. min(max output, monthly average demand))
- The units of the objective function and constraints must be consistent
