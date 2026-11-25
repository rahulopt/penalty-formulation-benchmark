"""Minimize worst absolute or relative shortage under controlled allocation."""
import argparse
import json
import statistics
from pathlib import Path

from gurobipy import GRB
from src.base_model import build_model
from src.config_loader import load_config


def run(config, output_dir, mode="absolute"):
    if mode not in ("absolute", "relative"):
        raise ValueError("Unknown minimax mode")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model, x, v, cost = build_model(config, soft=True)
    with model:
        regions = config["regions"]
        demand = sum(r["demand"] for r in regions)
        capacity = config["inventory"]["available_units"]
        coefficient = config["penalties"]["maximum_violation"]["coefficient"]
        if coefficient <= 0:
            raise ValueError("Maximum violation coefficient must be positive")
        m = model.addVar(lb=0, name="maximum_violation")
        for r in regions:
            i = r["id"]
            if mode == "absolute":
                model.addConstr(m >= v[i], name=f"max_{i}")
            elif r["demand"] > 0:
                model.addConstr(r["demand"] * m >= v[i], name=f"max_{i}")
        model.addConstr(x.sum() == min(capacity, demand), name="controlled_allocation")
        model.setObjective(cost + coefficient * m, GRB.MINIMIZE)
        model.optimize()
        result = {"experiment": "E07", "scenario": config["experiment"]["scenario_id"],
                  "mode": mode, "coefficient": coefficient, "status_code": int(model.Status),
                  "status": "OPTIMAL" if model.Status == GRB.OPTIMAL else "NOT_OPTIMAL",
                  "runtime_seconds": model.Runtime, "node_count": model.NodeCount,
                  "num_variables": model.NumVars, "num_constraints": model.NumConstrs}
        if model.SolCount:
            rows = [{"region": r["id"], "demand": r["demand"],
                     "allocation": round(x[r["id"]].X), "shortage": round(v[r["id"]].X)}
                    for r in regions]
            rates = [r["allocation"] / r["demand"] for r in rows if r["demand"]]
            allocation = sum(r["allocation"] for r in rows)
            result.update({"regions": rows, "total_allocation": allocation,
                           "total_shortage": sum(r["shortage"] for r in rows),
                           "maximum_shortage": max(r["shortage"] for r in rows),
                           "violated_regions": sum(r["shortage"] > 0 for r in rows),
                           "maximum_violation_metric": m.X, "allocation_cost": cost.getValue(),
                           "violation_penalty": coefficient*m.X, "objective": model.ObjVal,
                           "objective_bound": model.ObjBound, "mip_gap": model.MIPGap,
                           "fill_rate": allocation/demand if demand else None,
                           "minimum_regional_fill_rate": min(rates) if rates else None,
                           "regional_fill_rate_std": statistics.pstdev(rates) if rates else None})
        (output_dir / "e07_result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None)
    parser.add_argument("--output-dir", default="results/S01/E07")
    parser.add_argument("--mode", choices=["absolute", "relative"], default="absolute")
    args = parser.parse_args()
    run(load_config(args.config), args.output_dir, args.mode)
