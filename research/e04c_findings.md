# E04C — Reduced breakpoint grid

User-reported S01 run: breakpoints [0,40,200], quadratic reference coefficient 0.625, slopes [25,150]. Optimal objective and bound 13000, zero gap, runtime 0.009436845779418945 seconds, one explored node, five root simplex iterations. Original model: 15 variables, 16 constraints. Presolved model: 10 integer variables, 6 constraints, 15 nonzeros.

Each region receives 160 units, with 40 shortage and penalty 1000. Total allocation 800, shortage 200, maximum shortage 40, allocation cost 8000, aggregate and minimum fill rate 80%, population fill-rate standard deviation zero. PWL and quadratic reference penalties both 5000; approximation error at returned solution zero.

Relative to E04A, total constraints decrease from 31 to 16 (48.39%), preserving the unique balanced allocation in S01. The penalty epigraph uses 10 rather than 25 segment inequalities. Global approximation accuracy is not preserved: on [40,200], the maximum interpolation error is 0.625*(200-40)^2/4 = 4000 at v=120. Exactness at the selected optimum does not imply exactness elsewhere. Runtime was about 50% higher than the single E04A observation; repeat runs and larger instances are needed before attributing performance differences to formulation size.

Next: E04D single segment [0,200] to test the limiting case where the approximation becomes a linear penalty with slope 125.
