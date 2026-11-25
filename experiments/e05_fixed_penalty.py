"""Fixed-charge (L0-like) penalty with controlled total allocation."""
import argparse
import json
import statistics
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

from src.base_model import build_model
from src.config_loader import load_config


def run(config, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model, x, v, cost = build_model(config, soft=True)
    with model:
        regions = config["regions"]
        ids = [r["id"] for r in regions]
        demand = sum(r["demand"] for r in regions)
        capacity = config["inventory"]["available_units"]
        coefficient = config["penalties"]["fixed"]["coefficient"]
        if coefficient <= 0:
            raise ValueError("Fixed penalty coefficient must be positive")
        z = model.addVars(ids, vtype=GRB.BINARY, name="violated")
        for r in regions:
            i = r["id"]
            # Integer shortages: z=1 if and only if v>=1.
            model.addConstr(v[i] <= r["demand"] * z[i], name=f"activate_{i}")
            model.addConstr(v[i] >= z[i], name=f"positive_{i}")
        model.addConstr(x.sum() == min(capacity, demand), name="controlled_allocation")
        model.setObjective(cost + coefficient * z.sum(), GRB.MINIMIZE)
        model.optimize()
        result = {
            "experiment": "E05",
            "scenario": config["experiment"]["scenario_id"],
            "status_code": int(model.Status),
            "status": "OPTIMAL" if model.Status == GRB.OPTIMAL else "NOT_OPTIMAL",
            "runtime_seconds": model.Runtime,
            "node_count": model.NodeCount,
            "fixed_penalty_coefficient": coefficient,
            "controlled_allocation": True,
            "num_variables": model.NumVars,
            "num_constraints": model.NumConstrs,
        }
        if model.SolCount:
            rows = [{"region": r["id"], "demand": r["demand"],
                     "allocation": round(x[r["id"]].X),
                     "shortage": round(v[r["id"]].X),
                     "violated": round(z[r["id"]].X)} for r in regions]
            allocation = sum(r["allocation"] for r in rows)
            rates = [r["allocation"] / r["demand"] for r in rows if r["demand"]]
            affected = sum(r["violated"] for r in rows)
            result.update({
                "regions": rows,
                "total_allocation": allocation,
                "total_shortage": sum(r["shortage"] for r in rows),
                "maximum_shortage": max(r["shortage"] for r in rows),
                "violated_regions": affected,
                "allocation_cost": cost.getValue(),
                "violation_penalty": coefficient * affected,
                "objective": model.ObjVal,
                "objective_bound": model.ObjBound,
                "mip_gap": model.MIPGap,
                "fill_rate": allocation / demand if demand else None,
                "minimum_regional_fill_rate": min(rates) if rates else None,
                "regional_fill_rate_std": statistics.pstdev(rates) if rates else None,
            })
        (output_dir / "e05_result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None)
    parser.add_argument("--output-dir", default="results/S01/E05")
    args = parser.parse_args()
    run(load_config(args.config), args.output_dir)
