# Penalty Formulation Benchmark

A research-oriented comparison of violation variables and penalty formulations using Python and Gurobi.

## Current stage
S01 controlled scenario and E00 hard-constraint feasibility baseline. Results are pending local execution.

## Run
Use Python 3.12 and Gurobi 13.0.0 with a compatible license.

```bash
python -m pip install gurobipy==13.0.0 pyyaml pytest
python -m src.config_loader
python -m pytest -q
python -m experiments.e00_hard_constraint
```

E00 should be infeasible because demand exceeds inventory. The experiment saves a JSON summary and an IIS model under results/S01/E00/.

See [methodology](research/methodology.md) and [hypotheses](research/hypotheses.md).
