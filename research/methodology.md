# Experimental methodology

## Research question
How does penalty structure influence violation distribution under resource scarcity?

## Controlled scenario S01
Five regions each demand 200 units, allocation costs 10 per unit, and inventory is limited to 800 units. Minimum aggregate shortage is 200 units.

E00 tests feasibility under hard demand constraints. Subsequent soft models compare linear, weighted linear, quadratic, convex piecewise linear, fixed-charge, hybrid, minimax, asymmetric and lexicographic objectives. For distribution-only comparisons, fix total allocation at 800; investigate endogenous allocation separately. Initial penalty coefficients are provisional.

## Evaluation
Record allocation cost, total and maximum shortage, regional fill rates and dispersion, solver status, runtime, node count, incumbent, bound and gap where available. Compare common KPIs rather than raw objectives with different units. Repeat timing runs and record hardware and software versions. Separate time-limited incumbents from proven optima.

Target environment: Python 3.12.7 and Gurobi 13.0.0, one solver thread, seed 42, 60-second time limit and relative MIP gap 0.0001. The optimization time limit is not an end-to-end SLA; track diagnostic and processing time separately.

## Limitations
Synthetic data and symmetric initial scenario restrict generalization. No experimental outcomes have been recorded yet.
