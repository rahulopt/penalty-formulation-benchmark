# S02 — Demand-normalized quadratic (power 1)

User-reported optimal run: coefficient 0.625, fixed allocation 800, shortages [80,50,30,24,16], allocations [320,200,120,96,64]. Objective and bound 8025, gap zero, runtime 0.014820098876953125 seconds, one node. Allocation cost 8000, penalty 25, maximum shortage 80, total shortage 200, all regional fill rates 80%, population fill-rate standard deviation zero.

For fixed total shortage S and uniform allocation costs, the continuous interior optimum of sum(v_i^2/d_i^p) is v_i=S*d_i^p/sum(d_j^p). For p=1 this is proportional shortage and is integer-feasible in S02. The observed decision matches relative minimax. Power 2 instead produced [120,47,17,11,5]. The earlier absolute quadratic run produced [40,40,40,40,40], but the separate controlled power-0 run remains unverified. These are conditional results, not universal equivalence claims. Runtime observations are single runs.

Next: S03 regional priority effects with uniform demands and costs; isolate weighted linear and weighted quadratic penalties using controlled allocation.
