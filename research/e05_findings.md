# E05 — Fixed violation penalty

Observed S01 run reported by the user: optimal objective and bound 18000, zero gap, runtime 0.006270885467529297 seconds, zero nodes, 15 variables, 17 constraints. Shortages [0,0,0,0,200] in configuration order; exactly one violated region. Total allocation 800, total shortage 200, maximum shortage 200, allocation cost 8000, fixed penalty 10000, aggregate fill rate 80%, minimum fill rate 0%, population fill-rate standard deviation 0.4.

Unlike E01, whose objective is indifferent among distributions with total shortage 200, E05 explicitly minimizes the number of affected regions. With controlled allocation of 800 and equal regional demands of 200, one violated region is both necessary and sufficient. The identity of that region is not unique.

The fixed penalty represents an incident or contractual cost rather than shortage severity. Explicit maximum feasible aggregate allocation was imposed to isolate distribution; this is an experimental control not present explicitly in E01, E03 and E04, although those runs achieved the same allocation. Single-run timing is descriptive only.

E06 compares fixed plus uniform linear severity and fixed plus quadratic severity under the same controlled allocation. Uniform linear severity is constant when total shortage is fixed, so it cannot change E05's optimal distributions. Quadratic severity creates a trade-off between affected-region count and concentration.
