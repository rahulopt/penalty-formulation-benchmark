# E06C — Hybrid penalty sensitivity

All 15 user-reported solver runs passed the exact integer analytical oracle, with zero reported objective prediction error. The controlled S01 instance has total shortage 200 and quadratic coefficient 0.625.

| Fixed coefficient | Expected counts | Observed count | Objective |
|---:|---|---:|---:|
| 0 | 5 | 5 | 13000 |
| 1249 | 5 | 5 | 19245 |
| 1250 | 4 or 5 | 5 | 19250 |
| 1251 | 4 | 4 | 19254 |
| 2082.75 | 4 | 4 | 22581 |
| 2083.75 | 3 or 4 | 3 | 22585 |
| 2084.75 | 3 | 3 | 22588 |
| 4165.25 | 3 | 3 | 28829.5 |
| 4166.25 | 2 or 3 | 3 | 28832.5 |
| 4167.25 | 2 | 2 | 28834.5 |
| 5000 | 2 | 2 | 30500 |
| 12499 | 2 | 2 | 45498 |
| 12500 | 1 or 2 | 1 | 45500 |
| 12501 | 1 | 1 | 45501 |
| 20000 | 1 | 1 | 53000 |

The exact integer transition thresholds were confirmed by testing immediately below, at, and above each threshold. At ties, the solver returns one valid optimal count; the analytical oracle establishes the other. Maximum shortage increases from 40 to 200 as the preferred affected count decreases from five to one. Aggregate fill remains 80%. Findings are specific to S01; timing is not a repeated-run benchmark.
