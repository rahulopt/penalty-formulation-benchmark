# Penalty Formulation Benchmark

**How should an optimizer distribute unavoidable shortages?**

A reproducible Operations Research case study investigating how violation penalties influence inventory allocation, regional service, business priorities and computational performance.

![Python](https://img.shields.io/badge/Python-3.12-blue) ![Gurobi](https://img.shields.io/badge/Gurobi-13.0.0-blue) ![License](https://img.shields.io/badge/License-MIT-green)

[Research report](research/research_report.md) · [Published data](data/benchmark_results/) · [Dashboard source](app.py) · [Experimental methodology](research/methodology.md)

## Business problem

Five regions request 1,000 units, but only 800 units are available. The remaining 200 units must be allocated as shortages. Should the optimizer concentrate the shortage, distribute it evenly, protect high-priority regions, or maximize the worst regional service level?

Different mathematical penalty formulations can produce very different decisions even when aggregate inventory utilization is identical.

| Demand | Available inventory | Unavoidable shortage |
|---:|---:|---:|
| 1,000 | 800 | 200 |

## Key findings

- **Linear penalty:** in the symmetric experiment, a concentrated shortage was optimal, but all distributions with the same total shortage were equally optimal.
- **Quadratic penalty:** distributed shortages evenly in the symmetric experiment and reduced shortage severity in the coupled network.
- **Piecewise Linear (PWL) penalty:** breakpoint placement mattered; targeted breakpoints reproduced the controlled quadratic optimum with fewer constraints than the finer approximation.
- **Relative fairness:** equal absolute shortages did not imply equal regional fill rates under heterogeneous demand.
- **Business priorities and service targets:** analytical sensitivity thresholds and the Pareto frontier quantified the cost of improving service guarantees.
- **Computational performance:** at 50 regions, PWL met the configured solver deadline more often than quadratic, but neither was universally superior.

### Controlled allocation example

All rows below have 200 units of total shortage and 80% aggregate fill rate.

| Formulation | Shortage across five regions | Worst regional fill |
|---|---|---:|
| Linear | 0, 0, 0, 0, 200 | 0% |
| Quadratic | 40, 40, 40, 40, 40 | 80% |
| Piecewise Linear — targeted breakpoints | 40, 40, 40, 40, 40 | 80% |
| Fixed | 0, 0, 0, 0, 200 | 0% |
| Fixed + quadratic | 0, 0, 0, 100, 100 | 50% |

### Computational benchmark

54 runs: three network sizes, three independent instance seeds per size, two repeats and three formulations. Gurobi 13.0.0, one thread, 15-second solver limit, 0.1% relative mixed-integer optimality gap tolerance.

| Regions | Linear median runtime | Quadratic median runtime | Piecewise Linear median runtime |
|---:|---:|---:|---:|
| 10 | 0.005 s | 0.051 s | 0.053 s |
| 25 | 0.052 s | 0.776 s | 0.259 s |
| 50 | 0.095 s | 15.000 s* | 8.404 s |

*All six quadratic runs at 50 regions reached the time limit; these are censored observations, not times to proven optimality.*

| Formulation | Solver deadline and gap tolerance met |
|---|---:|
| Linear | 18/18 |
| Quadratic | 12/18 |
| Piecewise Linear | 16/18 |

All 54 runs produced feasible incumbents. At 50 regions, the observed mean maximum region-SKU shortages were 188, 46.33 and 51.33 units for linear, quadratic and PWL respectively. Speed alone does not establish business solution quality.

[Detailed scalability findings](research/e11_scalability_findings.md)

## Mathematical framework

The model minimizes allocation cost plus shortage penalties, subject to inventory capacity and demand balance.

$$
\begin{aligned}
\min_{x,v}\quad &\sum_i c_i x_i+P(v)\\
\text{subject to}\quad &x_i+v_i=d_i\quad\forall i\\
&\sum_i x_i\le C\\
&x_i,v_i\in\mathbb Z_{\ge0}
\end{aligned}
$$

Here x is allocation, v is shortage, d is demand, c is allocation cost and C is available inventory. Controlled distribution comparisons use fixed or verified full allocation; network experiments allow utilization to vary.

## Research scope

| Scenario | Purpose |
|---|---|
| S01 | Equal regional demands and priorities; isolate penalty shape |
| S02 | Heterogeneous demand; compare absolute and relative fairness |
| S03 | Different regional priorities; explore service guarantees |
| E11 | Coupled warehouse-region-SKU network; measure scalability |

Methods include hard constraints, linear and weighted penalties, quadratic and normalized penalties, convex piecewise linear approximations, fixed and hybrid penalties, minimax, hard and soft service-level agreements (SLAs), lexicographic optimization and epsilon-constraint optimization.

Analytical checks: 15/15 hybrid sensitivity cases, 17/17 reported soft SLA cases, and 83/83 epsilon-budget oracle flags. The controlled Pareto sweep contains 81 distinct nondominated KPI pairs.

## Explore the interactive dashboard

The dashboard reads published benchmark results; viewing it does **not** require a Gurobi license.

```bash
git clone https://github.com/rahulopt/penalty-formulation-benchmark.git
cd penalty-formulation-benchmark
python -m venv .venv
source .venv/bin/activate
python -m pip install streamlit pandas plotly
python -m streamlit run app.py
```

Open http://localhost:8501.

Explore allocation and fairness, hybrid sensitivity, service guarantees, efficient business trade-offs and solver scalability. Public deployment and full browser smoke testing are pending; no hosted dashboard URL is claimed.

## Reproduce the experiments

Use Python 3.12 and Gurobi 13.0.0 with a compatible license. Solver execution requires a license; dashboard viewing does not.

```bash
python -m pip install gurobipy==13.0.0 pyyaml pytest numpy pandas scipy matplotlib seaborn
python -m pytest -q
python -m src.config_loader
python -m experiments.e00_hard_constraint
python -m experiments.e01_linear_penalty
python -m experiments.e03_quadratic_penalty --coefficient 0.625
python -m experiments.e11_scalability --sizes 10 25 50 --seeds 42 43 44 --repeats 2 --limit 15
python export_results.py
```

For additional experiments, inspect their command-line options with `python -m experiments.<module> --help`. Raw local results are ignored by Git; the export script publishes allowlisted metrics under data/benchmark_results. Runtime will vary with hardware and solver environment.

## Repository layout

```text
configs/                 Scenario configuration
src/                     Shared optimization model and configuration loader
experiments/             Individual formulation and benchmark experiments
tests/                   Automated tests
research/                Working paper, methodology and experiment findings
data/benchmark_results/  Published research metrics
app.py                   Interactive Streamlit dashboard
export_results.py        Sanitized result export
```

## Research documentation

- [Full working paper and references](research/research_report.md)
- [Hybrid penalty analytical thresholds](research/e06c_findings.md)
- [Absolute versus relative fairness](research/s02_findings.md)
- [Soft SLA coefficient sensitivity](research/e08_sensitivity_findings.md)
- [Lexicographic optimization](research/e09_lexicographic_findings.md)
- [Epsilon-constraint Pareto frontier](research/e10_pareto_findings.md)
- [Full scalability benchmark](research/e11_scalability_findings.md)

## Limitations

This is an independent working paper, not a peer-reviewed publication. Instances are synthetic; only three independent network instances were tested per size. Repeated runs are not independent observations. Solver-only time excludes model construction, memory profiling and end-to-end latency. Raw objectives across different penalty scales are not directly comparable. Time-limited incumbents are not certified optimal. The conclusions are conditional on the tested models and settings.

## License

MIT — see [LICENSE](LICENSE). Gurobi is separately licensed.
