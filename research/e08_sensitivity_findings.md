# E08 — Soft SLA sensitivity validation

All 17 user-reported runs returned OPTIMAL with zero MIP gap.

| mu | SLA shortfall | Weighted shortage | Objective |
|---:|---:|---:|---:|
|0|180|200|18000|
|25|180|200|22500|
|49|180|200|26820|
|50|180|200|27000|
|51|160|220|27160|
|75|160|220|31000|
|99|160|220|34840|
|100|160|220|35000|
|101|140|260|35140|
|125|140|260|38500|
|149|140|260|41860|
|150|140|260|42000|
|151|120|320|42120|
|199|120|320|47880|
|200|120|320|48000|
|201|100|400|48100|
|500|100|400|78000|

All reported solutions match the analytical marginal exchange predictions. At each exact threshold the reported solution has the higher adjacent SLA shortfall; intermediate integer allocations can also be optimal. The strict threshold mu>200 guarantees minimum aggregate shortfall in S03, not necessarily individual fairness. Coefficients 201 and 500 attain identical primary and secondary KPI values. Raw objectives across coefficients are not comparable as monetary savings. No repeated timing benchmark was performed.
