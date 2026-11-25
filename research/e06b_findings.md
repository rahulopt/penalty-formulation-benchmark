# E06B — Fixed plus quadratic penalty

User-reported S01 run: fixed coefficient 5000, quadratic coefficient 0.625, optimal objective and bound 30500, zero gap, runtime 0.03356194496154785 seconds, six nodes, 15 variables, 17 constraints. Shortages [0,0,0,100,100], two affected regions, allocation 800, total shortage 200, maximum shortage 100, allocation cost 8000, fixed penalty 10000, quadratic penalty 12500, aggregate fill rate 80%, minimum fill rate 50%, population fill-rate standard deviation 0.2449489742783178.

The hybrid formulation trades off affected-region count and shortage severity. Region identities are interchangeable in S01. Runtime is a single observation.

For k affected regions, integer-balanced shortage minimizes squared shortage. Let a=floor(200/k), r=200 mod k; the minimum penalty is F*k + 0.625*((k-r)*a^2+r*(a+1)^2). Exact adjacent transition thresholds for increasing F are 1250 (5 to 4), 2083.75 (4 to 3), 4166.25 (3 to 2), 12500 (2 to 1). Both adjacent counts are optimal at a threshold. These results are specific to symmetric S01 with fixed allocation.

E06C sweeps coefficients and compares solver output against the exact analytical oracle, including ties.
