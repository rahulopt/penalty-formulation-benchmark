# E01 — Linear penalty findings

## Observed run (S01)
User-reported Gurobi execution: optimal status, objective and bound 18000, MIP gap 0, runtime 0.009791135787963867 seconds, zero explored nodes.

| Region | Demand | Allocation | Shortage |
|---|---:|---:|---:|
| North | 200 | 200 | 0 |
| South | 200 | 200 | 0 |
| East | 200 | 200 | 0 |
| West | 200 | 200 | 0 |
| Central | 200 | 0 | 200 |

Allocation cost 8000, penalty 10000, aggregate fill rate 80%, maximum shortage 200, population standard deviation of regional fill rates 0.4.

## Interpretation
With equal costs and penalties, the objective reduces to 10000 + 40 * total shortage. Therefore every feasible distribution with total shortage 200 is optimal. The observed concentrated shortage is one optimal solution, not an inevitable outcome of linear penalties. H1 is supported for this controlled scenario. Aggregate fill rate masks regional service disparities.

Runtime is a single observation. The next experiment uses a calibrated quadratic penalty with the same marginal penalty (50) at a reference shortage of 40 units: coefficient 0.625. This calibration does not equate raw objective values.
