# Comparative Analysis of Violation Penalty Formulations in Mathematical Optimization
## Solution quality, fairness and computational performance

**Research report — version 1.0 (working paper; not peer reviewed)**

## Abstract

When resource availability is insufficient to satisfy demand, optimization models must decide how to distribute unavoidable violations. This study compares linear, quadratic, piecewise linear (PWL), fixed, hybrid, weighted and minimax penalties, as well as hard and soft service-level constraints, lexicographic optimization and the epsilon-constraint method. Three controlled inventory scenarios isolate demand heterogeneity and priority effects. Analytical predictions are compared with integer optimization results; a separate coupled warehouse-region-product benchmark evaluates computational performance. All 15 hybrid sensitivity checks, 17 reported soft-SLA cases and 83 epsilon-budget checks match their analytical predictions. In the 54-run network benchmark, linear, quadratic and PWL formulations meet the configured solver deadline and optimality tolerance in 18, 12 and 16 runs, respectively. Results highlight the distinction between aggregate service, distributional fairness and solver performance. Conclusions are conditional on the synthetic instances and solver settings.

## 1. Motivation and research questions

A feasible allocation can be operationally undesirable even when mathematically optimal. With a shortage of 200 units, distributing all shortage to one region and sharing it across five regions may yield the same total unmet demand but radically different service outcomes.

This study asks:
1. How does penalty shape influence shortage concentration and severity?
2. How do demand normalization and business priorities affect fairness?
3. Can analytical penalty thresholds replace arbitrary large weights?
4. How can conflicting service and priority objectives be represented explicitly?
5. How do linear, quadratic and PWL models trade off solution quality and computational deadlines?

The contribution is a reproducible, controlled computational case study, not a claim that the underlying optimization methods are novel.

## 2. Mathematical framework

Let $i$ index regions, $d_i$ be integer demand, $x_i$ allocation, $v_i$ shortage, $c_i$ unit allocation cost, $C$ available inventory and $w_i$ positive priority. The basic soft-demand model is:



$
\begin{aligned}
\min_{x,v}\quad &\sum_i c_i x_i+P(v)\\
\text{subject to}\quad &x_i+v_i=d_i &&\forall i\\
&\sum_i x_i\le C\\
&x_i,v_i\in\mathbb Z_{\ge 0} &&\forall i
\end{aligned}
$



For distribution-only comparisons, allocation is either explicitly fixed to min(C, total demand) or verified to equal that quantity in the observed solution. The network benchmark does not fix total allocation.

### 2.1 Penalty families

| Family | Penalty or objective component | Interpretation |
|---|---|---|
| Linear | $\lambda\sum_i v_i$ | Constant marginal cost |
| Weighted linear | $\lambda\sum_i w_i v_i$ | Priority-dependent marginal cost |
| Quadratic | $\lambda\sum_i v_i^2$ | Increasing marginal cost |
| Weighted quadratic | $\lambda\sum_i w_i v_i^2$ | Priority and severity |
| Normalized quadratic | $\lambda\sum_i\frac{v_i^2}{d_i^p}$ | Demand-dependent severity |
| Fixed | $F\sum_i z_i$ | Charge per affected region |
| Hybrid | $F\sum_i z_i+\lambda\sum_i v_i^2$ | Concentration versus severity |
| Absolute minimax | $\lambda t,\quad t\ge v_i$ | Worst absolute shortage |
| Relative minimax | $\lambda t,\quad d_it\ge v_i$ | Worst percentage shortage |
| Piecewise linear | $\sum_i p_i$ | Convex linear approximation |

For integer shortage, binary activation is exact when

$
v_i\le d_i z_i,\qquad v_i\ge z_i,\qquad z_i\in\{0,1\}
$

Convex PWL interpolation over adjacent breakpoints $a,b$ can be represented by

$
p_i\ge\lambda a^2+\lambda(a+b)(v_i-a)
$

The maximum of these affine segments equals the interpolant on its covered domain. Minimizing with positive coefficients on $p_i$ needs no additional segment binaries. The local maximum interpolation error is

$
\max_{v\in[a,b]}\bigl(P_{\mathrm{PWL}}(v)-\lambda v^2\bigr)=\frac{\lambda(b-a)^2}{4}
$



### 2.2 Analytical predictions

For uniform costs and fixed total shortage S, strict convexity of the unweighted quadratic penalty gives equal continuous shortages, subject to bounds. With positive demand and interior continuous solutions, the normalized quadratic first-order condition gives:



$
v_i^*=\frac{S d_i^p}{\sum_j d_j^p}
$



Thus $p=0$ promotes equal absolute shortage, $p=1$ proportional shortage, and $p=2$ favors larger demands bearing disproportionately more shortage. For weighted quadratic with equal costs, $v_i$ is proportional to $1/w_i$. These formulas require appropriate bounds and integer rounding or exact integer optimization.

For the symmetric hybrid model with $k$ affected regions, define

$
a=\left\lfloor\frac{S}{k}\right\rfloor,\qquad r=S\bmod k
$

The minimum severity penalty and combined penalty are

$
\begin{aligned}Q(k)&=\lambda[(k-r)a^2+r(a+1)^2]\\P(k)&=Fk+Q(k)\end{aligned}
$

Adjacent ties occur at

$
F=Q(k)-Q(k+1)
$



### 2.3 Service levels and multi-objective trade-offs

A hard minimum regional fill rate $\alpha$ requires

$
x_i\ge\lceil\alpha d_i\rceil
$

A soft requirement introduces nonnegative integer slack $s_i$:

$
x_i+s_i\ge\lceil\alpha d_i\rceil,\qquad s_i\in\mathbb Z_{\ge0}
$

The actual SLA shortfall, even when slack is unpenalized, is

$
s_i^{\mathrm{actual}}=\max(0,\lceil\alpha d_i\rceil-x_i)
$



The soft-SLA objective is

$
\min\quad\sum_i c_i x_i+\lambda\sum_i w_i v_i+\mu\sum_i s_i
$

Lexicographic optimization instead orders objectives strictly, using zero objective degradation tolerances:

$
\operatorname{lexmin}\left(\sum_i s_i,\ \sum_i w_i v_i,\ \sum_i c_i x_i\right)
$

The epsilon-constraint method minimizes weighted shortage subject to an explicit budget, with secondary SLA minimization to avoid dominated ties.

$
\begin{aligned}\min\quad &\sum_i w_i v_i\\\text{subject to}\quad &\sum_i s_i\le\epsilon\end{aligned}
$



## 3. Experimental methodology

| Scenario | Demand | Priorities | Supply |
|---|---|---|---|
| S01 | [200,200,200,200,200] | All 1 | 800 |
| S02 | [400,250,150,120,80] | All 1 | 800 |
| S03 | [200,200,200,200,200] | [5,4,3,2,1] | 800 |

Controlled unit cost is 10. Total demand is 1000. Observed feasible controlled comparisons allocate 800 units. Gurobi 13.0.0 on Apple M1, one solver thread, seed 42 for controlled experiments. Individual timings are descriptive. Network benchmark uses 10, 25 and 50 regions, three stock keeping units (SKUs), three instance seeds, two repeats per instance, and three formulations (54 runs). Each region has two eligible warehouses and at most one active warehouse. Shared supply, transport costs and activation decisions couple demand allocations. Solver time limit is 15 seconds and relative MIP gap tolerance 0.001. Repeated runs of the same instance are not independent instances.

Evaluation: aggregate fill rate, minimum region or region-SKU fill rate, maximum shortage, population fill-rate standard deviation, weighted shortage, transportation and activation cost, solver runtime, work units, nodes, model size and optimality gap. Solver SLA denotes optimal termination within time and gap tolerances, distinct from regional service targets. Raw objectives from different penalty scales are not directly comparable.

## 4. Controlled experimental results

### 4.1 Symmetric shortage distribution

| Formulation | Observed shortage vector | Minimum fill rate |
|---|---|---:|
| Linear | [0,0,0,0,200] | 0% |
| Quadratic | [40,40,40,40,40] | 80% |
| PWL, targeted breakpoints [0,40,200] | [40,40,40,40,40] | 80% |
| Fixed | [0,0,0,0,200] | 0% |
| Fixed + quadratic, F=5000 | [0,0,0,100,100] | 50% |
| Absolute minimax | [40,40,40,40,40] | 80% |

Linear is indifferent among distributions with the same total shortage in S01; the observed concentrated solution is not uniquely required. The fixed penalty explicitly favors concentration. Absolute minimax reaches the lower bound 200/5=40. These decisions need not coincide on other instances.

### 4.2 Piecewise linear approximation

With coefficient 0.625, breakpoints [0,20,40,60,100,200] achieve the quadratic optimum in S01. Removing the breakpoint at 40 produces an observed [60,60,40,20,20] solution, with quadratic reference penalty 6000 versus optimal 5000. Targeted breakpoints [0,40,200] recover the optimum using 16 constraints instead of 31. A single segment [0,200] permits the concentrated solution with quadratic reference penalty 25000 despite zero interpolation error at that solution. Local interpolation error alone does not guarantee decision quality. No general runtime superiority follows from these small cases.

### 4.3 Hybrid sensitivity

For S01, S=200 and lambda=0.625, integer severity costs Q(1..5) are 25000,12500,8333.75,6250,5000. Adjacent thresholds for increasing fixed charge are 1250,2083.75,4166.25,12500. All 15 observed solver checks agree with the oracle, including ties. The selected count decreases from five to one as F increases, and maximum shortage increases from 40 to 200.

### 4.4 Demand normalization and relative fairness

| S02 formulation | Shortage vector | Minimum fill | Fill-rate std. dev. |
|---|---|---:|---:|
| Absolute quadratic | [40,40,40,40,40] | 50% | 13.99 pp |
| Absolute minimax | [40,40,40,40,40] | 50% | 13.99 pp |
| Demand-normalized quadratic, p=1 | [80,50,30,24,16] | 80% | 0 pp |
| Relative minimax | [80,50,30,24,16] | 80% | 0 pp |
| Squared relative shortage, p=2 | [120,47,17,11,5] | 70% | 8.53 pp |

Power 0 uses the earlier absolute quadratic observation; the separate controlled power-0 batch output was not supplied. Equal absolute shortage is not equal percentage service. Power 1 and relative minimax coincide here, but are not universally equivalent.

### 4.5 Priority weights and hard SLA

Weighted linear yields [0,0,0,0,200], weighted shortage 200. Weighted quadratic yields [17,22,29,44,88], weighted shortage 436 and minimum fill 56%. For a 60% hard floor, linear and quadratic yield weighted shortages 360 and 454, respectively; both reach minimum fill 60%. At 80% all five shortages equal 40. At 90% the model is infeasible because required inventory is 900. The ambiguous quadratic solver status INF_OR_UNBD was resolved to INFEASIBLE by disabling DualReductions and reoptimizing.

The 60% floor increases linear objective from 18000 to 26000 and quadratic objective from 18950 to 19013.75. These are within-formulation objective changes, not comparable monetary losses across formulations.

### 4.6 Soft SLA, hierarchy and efficient frontier

At a 90% target, unavoidable aggregate SLA shortfall is at least 100. Under the weighted linear coefficient 50, moving 20 units each from progressively higher-priority regions to Central yields marginal penalties 50,100,150,200. All 17 reported soft-SLA runs match this prediction. Strict mu>200 guarantees aggregate shortfall 100 in S03; exactly at a threshold multiple optimal KPI values can occur. This does not guarantee equitable individual regional service.

| SLA shortfall | Weighted shortage |
|---:|---:|
| 100 | 400 |
| 120 | 320 |
| 140 | 260 |
| 160 | 220 |
| 180 | 200 |

Lexicographic SLA-first and priority-first match the two endpoints. Both retain allocation cost 8000. The epsilon sweep returned 82 optimal cases and one infeasible case, with all 83 oracle checks passed and 81 distinct nondominated integer KPI pairs. The marginal weighted shortage cost of additional SLA improvement rises from 1 to 4 per unit. This explains the soft penalty thresholds.

## 5. Computational scalability

| Regions | Linear median runtime (s) | Quadratic | PWL | Linear SLA | Quadratic SLA | PWL SLA |
|---:|---:|---:|---:|---:|---:|---:|
|10|0.00496|0.05057|0.05325|6/6|6/6|6/6|
|25|0.05199|0.77616|0.25857|6/6|6/6|6/6|
|50|0.09455|15.00008|8.40416|6/6|0/6|4/6|

All 54 runs produced feasible incumbents; 46 met the solver SLA. The six quadratic runs at size 50 reached their time limit; elapsed times are censored observations, not proven time to optimum. Status OPTIMAL means within configured tolerances.

| Mean metric, 50 regions | Linear | Quadratic | PWL |
|---|---:|---:|---:|
| Aggregate fill rate (%) |79.79|79.52|79.67|
| Minimum region-SKU fill rate (%) |0|17.88|6.12|
| Maximum shortage |188|46.33|51.33|
| Fill-rate std. dev. (pp) |36.57|15.63|17.96|
| Transport + activation cost |67229|77793|77267|

Matched PWL decisions evaluated on the common quadratic reference cost are on average about 2.31%, 2.22% and 2.03% above the observed quadratic incumbents at sizes 10,25,50. These are incumbent comparisons, not certified approximation losses. Linear sacrifices shortage distribution for lower transportation cost in the observed benchmark. PWL meets the deadline more often than quadratic at size 50, but some PWL instances also time out and its worst-service performance is weaker on average.

## 6. Decision guidance

Use linear penalties when constant marginal cost is the intended policy; quadratic for severity-sensitive allocation; convex PWL for a linear approximation with an explicitly evaluated breakpoint design; relative minimax for worst percentage service; weights for priority differentiation; hard floors for non-negotiable feasible guarantees; soft floors for negotiable service targets; lexicographic optimization for strict objective order; and epsilon constraints for explicit business trade-off exploration. Choose based on business requirements, then test computational feasibility under the actual operating deadline.

## 7. Limitations and future work

Synthetic data, three independent network instances per size, fixed three SKUs and a restricted eligibility structure limit generalization. The benchmark measures solver time, not end-to-end latency, model construction time or memory. Network utilization is not fixed and can differ by formulation. Controlled comparisons sometimes differ in explicit allocation constraints. Fairness metrics are not comprehensive definitions of equity. No statistical significance or universal superiority is claimed. Future work should investigate broader instance families, adaptive PWL refinement, asymmetric penalties, variable costs, robust or stochastic demand, independent solver comparisons and end-to-end production profiling.

## 8. Reproducibility and evidence

Run the experiment modules from the repository root with the documented configurations. Use export_results.py to publish allowlisted metrics and app.py for the interactive dashboard. A fresh public clone can display results only after the exported dataset is committed; publication has not been independently verified in this report.

Primary evidence: the experiment scripts and configuration files in this repository, user-reported solver outputs recorded in the individual research findings, especially [hybrid sensitivity](e06c_findings.md), [heterogeneous demand](s02_findings.md), [soft SLA sensitivity](e08_sensitivity_findings.md), [lexicographic optimization](e09_lexicographic_findings.md), [Pareto frontier](e10_pareto_findings.md) and [network benchmark](e11_scalability_findings.md).

A formal external literature review and verified bibliography are pending. This working paper documents the empirical investigation; it does not establish novelty relative to published research.
