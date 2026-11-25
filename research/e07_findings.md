# E07 — Absolute minimax penalty

User-reported S01 run: optimal objective and bound 10000, gap 0, runtime 0.009886980056762695 seconds, one node, 11 variables and 12 constraints. All five regions receive 160 units and incur 40 shortage. Total allocation 800, shortage 200, maximum shortage 40, allocation cost 8000, penalty 2000, aggregate and minimum regional fill rate 80%, population fill-rate standard deviation zero.

The maximum shortage is bounded below by 200/5=40 and equality is attainable. Minimax matches the quadratic decision in this symmetric instance, but the objectives are not generally equivalent. The formulation uses one additional continuous variable and five linking inequalities, plus a controlled allocation equality. Single-run timings are descriptive.

S02 introduces heterogeneous demands [400,250,150,120,80] with unchanged total demand, capacity and unit cost. Absolute minimax predicts equal shortage 40; relative minimax predicts shortage [80,50,30,24,16], yielding 80% fill in every region. These are predictions pending execution. S02 is a heterogeneous-demand scenario; the earlier proposed scenario numbering was provisional.
