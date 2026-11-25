# E11 — Coupled network smoke test

User-reported runs for 10 regions, 3 SKUs, instance seed 42, repeat 0, one solver thread, 10-second limit, MIP gap tolerance 0.001.

| Metric | Linear | Quadratic | PWL |
|---|---:|---:|---:|
| Runtime seconds | 0.0023179054260253906 | 0.0484919548034668 | 0.04439496994018555 |
| Work units | 0.0010124681176366074 | 0.013961741074632177 | 0.026465893132305 |
| Nodes | 1 | 42 | 26 |
| Variables | 110 | 110 | 140 |
| Constraints | 106 | 106 | 243 |
| Relative gap | 0.0007603901887940211 | 0.00004052561725580783 | 0 |
| Transport and activation cost | 12629 | 14922 | 15255 |
| Total shortage | 668 | 668 | 668 |
| Maximum shortage | 190 | 32 | 40 |
| Minimum region-SKU fill rate | 0 | 0.5217391304347826 | 0.5121951219512195 |
| Fill rate std | 0.37068108581759385 | 0.11224765747866407 | 0.11642852952290741 |
| Common quadratic reference cost | 57955.25 | 24675.75 | 25227.5 |

All three returned status 2 (optimal within configured tolerances) and met the defined solver SLA. Overall fill rate 0.7990373044524669 for all three. PWL reference cost is approximately 2.24% higher than the observed quadratic incumbent; not an exact optimality loss because the quadratic incumbent has a nonzero gap. Linear has lower transport cost but higher shortage dispersion. Model size and work units should be compared alongside runtime. These are single observations; no general computational superiority is established. The full benchmark will use matched instances, three seeds, two repeats, three sizes and 15-second limits. Memory and model-construction/end-to-end latency are not instrumented. Total allocation is not explicitly fixed in E11, so common KPI comparisons must also account for possible differences in utilization in larger instances.
