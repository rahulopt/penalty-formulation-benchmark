"""Fixed-charge plus variable severity penalties, with controlled allocation."""
import argparse
import json
import statistics
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

from src.base_model import build_model
from src.config_loader import load_config


def run(config, output_dir, fixed=None, severity="linear", coefficient=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    fixed = config["penalties"]["fixed"]["coefficient"] if fixed is None else fixed
    coefficient = config["penalties"]["linear"]["coefficient"] if coefficient is None and severity == "linear" else (0.625 if coefficient is None else coefficient)
    if fixed < 0 or coefficient < 0 or severity not in ("linear", "quadratic"):
        raise ValueError("Invalid penalty settings")
    model, x, v, cost = build_model(config, soft=True)
    with model:
        regions = config["regions"]
        ids = [r["id"] for r in regions]
        demand = sum(r["demand"] for r in regions)
        capacity = config["inventory"]["available_units"]
        z = model.addVars(ids, vtype=GRB.BINARY, name="violated")
        for r in regions:
            i = r["id"]
            model.addConstr(v[i] <= r["demand"] * z[i], name=f"activate_{i}")
            model.addConstr(v[i] >= z[i], name=f"positive_{i}")
        model.addConstr(x.sum() == min(capacity, demand), name="controlled_allocation")
        variable_penalty = coefficient * gp.quicksum(v[i] if severity == "linear" else v[i] * v[i] for i in ids)
        model.setObjective(cost + fixed * z.sum() + variable_penalty, GRB.MINIMIZE)
        model.optimize()
        result = {
            "experiment": "E06", "scenario": config["experiment"]["scenario_id"],
            "severity": severity, "fixed_coefficient": fixed, "severity_coefficient": coefficient,
            "status_code": int(model.Status),
            "status": "OPTIMAL" if model.Status == GRB.OPTIMAL else "NOT_OPTIMAL",
            "runtime_seconds": model.Runtime, "node_count": model.NodeCount,
            "num_variables": model.NumVars, "num_constraints": model.NumConstrs,
        }
        if model.SolCount:
            rows = [{"region": r["id"], "demand": r["demand"],
                     "allocation": round(x[r["id"]].X), "shortage": round(v[r["id"]].X),
                     "violated": round(z[r["id"]].X)} for r in regions]
            allocation = sum(r["allocation"] for r in rows)
            affected = sum(r["violated"] for r in rows)
            rates = [r["allocation"] / r["demand"] for r in rows if r["demand"]]
            variable_cost = coefficient * sum(r["shortage"] if severity == "linear" else r["shortage"] ** 2 for r in rows)
            result.update({
                "regions": rows, "total_allocation": allocation,
                "total_shortage": sum(r["shortage"] for r in rows),
                "maximum_shortage": max(r["shortage"] for r in rows),
                "violated_regions": affected, "allocation_cost": cost.getValue(),
                "fixed_penalty": fixed * affected, "variable_penalty": variable_cost,
                "objective": model.ObjVal, "objective_bound": model.ObjBound,
                "mip_gap": model.MIPGap, "fill_rate": allocation / demand if demand else None,
                "minimum_regional_fill_rate": min(rates) if rates else None,
                "regional_fill_rate_std": statistics.pstdev(rates) if rates else None,
            })
        (output_dir / "e06_result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None)
    parser.add_argument("--output-dir", default="results/S01/E06")
    parser.add_argument("--fixed", type=float, default=None)
    parser.add_argument("--severity", choices=["linear", "quadratic"], default="linear")
    parser.add_argument("--coefficient", type=float, default=None)
    args = parser.parse_args()
    run(load_config(args.config), args.output_dir, args.fixed, args.severity, args.coefficient)
