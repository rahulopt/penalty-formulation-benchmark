# S03 — Weighted linear penalty (E02A)

User-reported optimal run: coefficient 50, objective and bound 18000, gap zero, runtime 0.004981040954589844 seconds, zero nodes. Shortages [0,0,0,0,200] in configuration order; allocation 800, shortage 200, weighted shortage 200, maximum shortage 200, allocation cost 8000, penalty 10000, aggregate fill rate 80%, minimum fill rate 0%, population fill-rate standard deviation 0.4.

With fixed total shortage, uniform allocation costs and strictly ordered priority weights, shortage is assigned first to the cheapest region up to its demand. In S03 the lowest-priority region alone can absorb all shortage. Weighted quadratic instead yields [17,22,29,44,88], weighted shortage 436 and minimum fill 56%. Neither objective is universally preferable. Runtime observations are single runs.

Next experiment imposes a hard minimum regional fill rate. This changes the feasible set and is not merely a penalty calibration. With 60% floor the weighted linear prediction is [0,0,40,80,80]; at 80% floor all shortages must equal 40; above 80% aggregate required service exceeds supply.