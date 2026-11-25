# E10 — Epsilon-constraint Pareto frontier

All 83 user-reported oracle checks passed. Epsilon 99 was infeasible; epsilon 100 through 181 returned optimal solutions. The 81 distinct nondominated KPI pairs occur at integer SLA shortfall 100 through 180; epsilon 181 repeats the endpoint (180,200). Allocation cost is 8000 for all feasible cases.

| SLA shortfall | Weighted shortage |
|---:|---:|
|100|400|
|120|320|
|140|260|
|160|220|
|180|200|

The marginal weighted shortage increase per unit of SLA improvement is respectively 1, 2, 3, 4 when moving from 180 toward 100 in four 20-unit segments. Multiplication by the E08 weighted shortage coefficient 50 gives the observed soft penalty thresholds 50, 100, 150, 200. E09 lexicographic solutions correspond to the two extreme frontier points. E10 enumerates intermediate efficient alternatives without requiring coefficient calibration.

This is the complete integer KPI frontier for controlled S03, not a universal result for heterogeneous networks. Single-run timing is descriptive. The final multi-objective pass gap is not a combined objective gap.

Next priority: controlled scalability benchmarking on coupled allocation instances with resource/eligibility constraints, repeated runs and common KPI comparisons; then reproducible report and dashboard.
