# E11 — Full scalability benchmark

Parsed all 54 JSON records from the user-supplied terminal output, excluding the three 10-second smoke-test records. Three sizes (10,25,50 regions), three instance seeds (42,43,44), two repeats, three formulations, one solver thread, 15-second limit and relative MIP gap tolerance 0.001. Each size/formulation group contains six runs across three independent instances. Repeats are not independent instances.

| Regions | Mode | Median runtime (s) | SLA successes/6 | Median gap (%) | Median work | Median nodes |
|---:|---|---:|---:|---:|---:|---:|
|10|linear|0.00496|6|0.069|0.00242|1|
|10|quadratic|0.05057|6|0.060|0.01396|53|
|10|pwl|0.05325|6|0|0.02647|26|
|25|linear|0.05199|6|0.047|0.03608|1|
|25|quadratic|0.77616|6|0.080|0.53340|1659|
|25|pwl|0.25857|6|0.073|0.25090|311|
|50|linear|0.09455|6|0.036|0.08087|1|
|50|quadratic|15.00008|0|3.489|12.18992|13095|
|50|pwl|8.40416|4|0.099|10.07500|8169|

All runs had feasible incumbents; 46/54 met the solver SLA. Linear 18/18, quadratic 12/18, PWL 16/18. All six 50-region quadratic runs and both 50-region PWL seed-43 runs reached the time limit. Status OPTIMAL denotes optimal within configured solver tolerances, not necessarily zero gap. Time-limited runtime is censored time to optimality.

At 50 regions, mean fill rates for linear/quadratic/PWL were 0.79788/0.79519/0.79671; mean minimum region-SKU fill rates 0/0.17879/0.06122; mean maximum shortages 188/46.333/51.333; mean population fill-rate deviations 0.36571/0.15630/0.17960; mean transport plus activation costs 67228.67/77793.33/77266.67. Total allocation was not fixed, so utilization differences must be accounted for.

Matched PWL reference quadratic cost relative to quadratic incumbent: mean +2.30954%, +2.21827%, +2.02526% for sizes 10,25,50 respectively. At 50 regions the reference quadratic incumbents are not proven optimal; these are not exact approximation losses. Linear has substantially greater shortage concentration despite lower transport cost. PWL has higher SLA success than quadratic on these tested 50-region instances, but neither a universal speed advantage nor identical fairness is established.

Limitations: only three independent instances per size; synthetic network with two eligible warehouses per region and one active warehouse per region; fixed three SKUs; solver-only runtime, no model construction time or memory; objective scales differ; no end-to-end latency measurements. Raw solver logs containing license identifiers must not be published. The benchmark results are sufficient for the core comparative report, with optional formulation refinement experiments clearly distinguished from validated findings.
