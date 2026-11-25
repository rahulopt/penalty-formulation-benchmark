# E04 — Piecewise linear penalty findings

## Observed S01 run
User-reported Gurobi execution with quadratic reference coefficient 0.625 and breakpoints [0,20,40,60,100,200].
- Optimal objective and bound: 13000; MIP gap: 0.
- Runtime: 0.006299018859863281 seconds; node count: 1.
- Model size: 15 variables and 31 constraints.
- All five regions: allocation 160, shortage 40, penalty 1000 each.
- Total allocation 800, shortage 200, maximum shortage 40, allocation cost 8000.
- PWL penalty and quadratic reference penalty: 5000 each; approximation error at solution: 0.
- Aggregate and minimum regional fill rate: 80%; population fill-rate standard deviation: 0.

The convex epigraph formulation reproduces the quadratic optimum in S01 because 40 is an explicit breakpoint. This supports H3 for the selected grid, not for arbitrary breakpoints. Observed runtime is about 38% lower than the single E03 run, but no general performance inference is justified.

## Follow-up E04B
Remove breakpoint 40 using [0,20,60,100,200]. All shortage distributions with each shortage between 20 and 60 and total shortage 200 are PWL-optimal. The PWL penalty is 6250 (objective 14250), while the quadratic penalty evaluated at the returned solution depends on the distribution. This tests loss of strict convexity and approximation error. Compare also grids [0,40,200] and [0,200] in separate output directories.
