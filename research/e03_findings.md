# E03 — Quadratic penalty findings

## Observed run (S01)
User-reported local execution, coefficient 0.625: optimal status, objective and bound 13000, gap 0, runtime 0.010168075561523438 seconds, one explored node. Every region receives 160 units and has shortage 40. Total allocation 800, shortage 200, allocation cost 8000, penalty 5000, aggregate and minimum regional fill rate 80%, population regional fill-rate standard deviation 0.

## Comparison with E01
Maximum shortage declined from 200 to 40 (80% reduction); minimum regional fill rate improved from 0% to 80%; fill-rate standard deviation declined from 0.4 to 0. Allocation cost and aggregate shortage were unchanged. Equal quadratic weights and fixed total shortage favor equal absolute shortages by strict convexity. H2 is supported in S01. This does not establish universal superiority or runtime differences. Raw objective values are not comparable across penalty functions.

## Next experiment
E04 uses convex piecewise linear interpolation of 0.625*v^2 at shortage breakpoints 0, 20, 40, 60, 100, 200 (plus the maximum demand if larger). Segment slopes are secants. The reference shortage of 40 is an explicit breakpoint, permitting a unique balanced optimum in S01. This design is selected for controlled validation; later experiments vary breakpoint placement and approximation error.
