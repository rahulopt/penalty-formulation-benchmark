# S03 — Weighted quadratic shortage penalty (E02B)

Observed user-reported Gurobi run: coefficient 0.625, regional weights [5,4,3,2,1], demands 200 each, controlled allocation 800. Optimal objective and bound 18950, gap zero, runtime 0.006600856781005859 seconds, one node.

Shortages [17,22,29,44,88], allocations [183,178,171,156,112], fill rates [0.915,0.89,0.855,0.78,0.56]. Total shortage 200, maximum shortage 88, weighted shortage 436, allocation cost 8000, penalty 10950, aggregate fill rate 0.8, minimum fill rate 0.56, population regional fill-rate standard deviation 0.1283354978172446.

For fixed shortage and uniform allocation costs, continuous interior optimum satisfies w_i*v_i = constant, yielding v_i proportional to 1/w_i. Observed products [85,88,87,88,88] are close to the continuous relationship. The observed integer allocation matches the predicted priority-sensitive trade-off. Higher priorities receive better service, but lower-priority regions incur larger shortages. Compared with the observed S01 unweighted quadratic reference, weighted shortage evaluated using S03 weights decreases from 600 to 436, while maximum shortage increases from 40 to 88. This is a trade-off, not universal improvement.

Weighted linear E02A output has not yet been supplied. Its predicted unique shortage vector for S03 is [0,0,0,0,200], objective 18000, weighted shortage 200. Do not label it observed until execution output is available. Runtime comparisons remain descriptive single-run observations.
