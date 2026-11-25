# E04B — Breakpoint removal

Observed user-reported S01 run: breakpoints [0,20,60,100,200], coefficient 0.625, optimal objective and bound 14250, zero gap, runtime 0.007653951644897461 seconds, one node, 15 variables and 26 constraints.

Regional shortages in North, South, East, West, Central order: [60,60,40,20,20]. Total shortage 200, maximum 60, allocation cost 8000, aggregate fill rate 80%, minimum fill rate 70%, population fill-rate standard deviation 0.08944271909999162.

PWL penalty 6250; quadratic penalty evaluated at returned allocation 6000; quadratic optimum penalty 5000. Approximation error at returned solution = 250. Quadratic optimality loss = 1000. Total PWL optimal objective minus quadratic optimal objective = 1250, the sum of these two terms for this instance.

The constant slope of 50 on [20,60] permits alternative optimal distributions with total shortage 200. Balanced shortage is also PWL-optimal, but not uniquely so. Removing breakpoint 40 therefore loses the unique balanced optimum, not necessarily the possibility of balance. The single observed timing does not establish a performance ranking. Fewer constraints alone do not guarantee faster optimization.

Next: execute E04C and E04D using distinct output directories before drawing broader conclusions.
