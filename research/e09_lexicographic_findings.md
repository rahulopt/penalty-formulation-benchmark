# E09 — Lexicographic optimization

Both user-reported S03 runs returned OPTIMAL at a 90% SLA target.

| Hierarchy | Allocation | SLA shortfall | Weighted shortage | Allocation cost | Runtime (s) |
|---|---|---:|---:|---:|---:|
| Priority-first | [200,200,200,200,0] | 180 | 200 | 8000 | 0.0013608932495117188 |
| SLA-first | [180,180,180,180,80] | 100 | 400 | 8000 | 0.014317989349365234 |

Both allocate 800 units and leave 200 demand shortage. The strict SLA-first hierarchy matches E08's solution at mu=500; priority-first matches the unpenalized SLA case. Hierarchical objectives avoid cross-objective penalty calibration but impose a strict ordering. Allocation cost is constant in S03, so the tertiary objective has no discriminatory effect. Single-run runtimes are descriptive. The reported final pass bound and gap should not be treated as a single combined multi-objective gap.

Next: epsilon-constraint method to enumerate efficient trade-offs between SLA shortfall and weighted shortage.
