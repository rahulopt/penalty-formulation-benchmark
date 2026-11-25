# S02 — Absolute versus relative fairness

User-reported Gurobi 13.0.0 runs on heterogeneous demand [400,250,150,120,80], capacity 800, uniform allocation cost 10.

| Model | Shortages | Objective | Runtime (s) | Gap |
|---|---|---:|---:|---:|
| E03 absolute quadratic | 40,40,40,40,40 | 13000 | 0.008806943893432617 | 0 |
| E07A absolute minimax | 40,40,40,40,40 | 10000 | 0.0009529590606689453 | 0 |
| E07B relative minimax | 80,50,30,24,16 | 8010 | 0.0008151531219482422 | 0 |

All runs optimal, one explored node, allocation 800, total shortage 200, allocation cost 8000 and aggregate fill rate 80%. Absolute models have maximum shortage 40, minimum fill rate 50%, population regional fill-rate standard deviation 0.1399301413007378. Relative minimax has maximum absolute shortage 80, maximum relative shortage 0.2, minimum fill rate 80%, standard deviation zero.

Equal absolute shortage is not equal proportional service. Relative minimax maximizes the worst service rate at fixed allocation and uniform cost in this scenario. It trades larger maximum absolute shortage for improved worst relative service. Raw objectives have different penalty scales and cannot be compared as business savings. Timings are individual observations.

Next: compare quadratic normalizations with fixed allocation. For continuous interior solutions, minimizing sum(v^2/d^p) gives v proportional to d^p for p=0,1,2. Integer and bound effects require computational validation. For S02, p=1 reproduces proportional shortage exactly; p=2 generally does not.
