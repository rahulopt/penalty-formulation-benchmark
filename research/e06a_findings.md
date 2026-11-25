# E06A — Fixed plus linear penalty

User-reported S01 run: fixed coefficient 10000, linear coefficient 50, optimal objective and bound 28000, zero MIP gap, runtime 0.009045124053955078 seconds, zero nodes, 15 variables and 17 constraints. Regional shortages [0,0,0,0,200] in configuration order. Total allocation 800, total shortage 200, maximum shortage 200, one affected region, allocation cost 8000, fixed penalty 10000, linear penalty 10000, aggregate fill rate 80%, minimum regional fill rate 0%, population fill-rate standard deviation 0.4.

With fixed aggregate allocation, uniform linear severity is constant at 10000. The objective reduces to 18000 + 10000 * affected-region count. Thus the set of optimal decisions is unchanged relative to E05; the observed allocation also matches E05. This equivalence is conditional on fixed total shortage and equal linear coefficients. Runtime is a single observation.

E06B remains pending: fixed coefficient 5000 and quadratic coefficient 0.625. The predicted optimum affects two regions with shortage 100 each, objective 30500. Region identities are interchangeable in S01.
