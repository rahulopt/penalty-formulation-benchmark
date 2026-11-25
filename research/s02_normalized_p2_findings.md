# S02 — Squared relative shortage (normalization power 2)

Observed user-reported run with coefficient 0.625 and controlled allocation 800. Optimal objective and bound 8000.094060920139, zero gap, runtime 0.004143953323364258 seconds, one node. Shortages [120,47,17,11,5], allocations [280,203,133,109,75], demands [400,250,150,120,80]. Total shortage 200, maximum shortage 120, allocation cost 8000, penalty 0.09406092013888888, aggregate fill rate 80%, minimum fill rate 70%, population regional fill-rate standard deviation 0.08525423417311569.

For the continuous interior problem with fixed total shortage and uniform costs, minimizing sum(v_i^2/d_i^2) yields v_i proportional to d_i^2 by the first-order conditions. Integer solution is close to this prediction. The squared relative objective is not equivalent to minimizing maximum relative shortage or demand-weighted squared relative shortage (sum(v_i^2/d_i)). The latter predicts proportional shortage in this scenario.

Compared with observed absolute quadratic and relative minimax results, power 2 has lower fill-rate dispersion than absolute quadratic but higher dispersion than relative minimax. Raw objective values are not comparable because penalty scales differ. Controlled allocation is essential here: without it, the very small penalty coefficient relative to allocation cost could change inventory utilization.

Only power 2 output from the normalized quadratic batch has been supplied so far. Power 0 and power 1 normalized-run results remain unverified; do not label them as observed until outputs are available. Earlier absolute quadratic run is independently observed but does not include the explicit controlled-allocation equality.
