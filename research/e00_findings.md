# E00 — Hard constraint baseline

## Observed results (S01, user-reported local run)
Gurobi 13.0.0 build v13.0.0rc1, Apple M1, macOS ARM64, one solver thread, seed 42.

- Total demand: 1,000; inventory: 800.
- Status: INFEASIBLE (3); no incumbent.
- Optimization runtime: 0.0023810863494873047 seconds.
- Model: 6 rows, 5 integer columns, 10 nonzeros.
- Explored nodes: 0.
- IIS: inventory_capacity and all five regional demand constraints; zero bounds; IISMinimal=true.
- IIS runtime: approximately 0.01 seconds (rounded solver log).

## Interpretation
The hard demand equalities imply total allocation of 1,000, contradicting the capacity upper bound of 800. The IIS identifies the irreducible conflict but does not select which business constraints to relax. Preserve physical capacity and introduce nonnegative shortage variables into regional demand balances in E01.

Runtime is one observation, not a general performance benchmark.
