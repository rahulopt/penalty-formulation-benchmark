import argparse
import json
import statistics
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

from src.base_model import build_model
from src.config_loader import load_config


def run(config, output_dir, coefficient=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model, x, v, cost = build_model(config, soft=True)
    with model:
        coefficient = config["penalties"]["quadratic"]["coefficient"] if coefficient is None else coefficient
        if coefficient <= 0:
            raise ValueError("Quadratic penalty coefficient must be positive")
        penalty = coefficient * gp.quicksum(v[i] * v[i] for i in v.keys())
        model.setObjective(cost + penalty, GRB.MINIMIZE)
        model.optimize()
        result = {
            "experiment": "E03",
            "scenario": config["experiment"]["scenario_id"],
            "status_code": int(model.Status),
            "status": "OPTIMAL" if model.Status == GRB.OPTIMAL else "NOT_OPTIMAL",
            "runtime_seconds": model.Runtime,
            "node_count": model.NodeCount,
            "penalty_coefficient": coefficient,
        }
        if model.SolCount:
            rows = [
                {"region": r["id"], "demand": r["demand"],
                 "allocation": round(x[r["id"]].X),
                 "shortage": round(v[r["id"]].X)}
                for r in config["regions"]
            ]
            total_demand = sum(r["demand"] for r in rows)
            total_allocation = sum(r["allocation"] for r in rows)
            total_shortage = sum(r["shortage"] for r in rows)
            fill_rates = [r["allocation"] / r["demand"] for r in rows if r["demand"]]
            result.update({
                "regions": rows,
                "total_allocation": total_allocation,
                "total_shortage": total_shortage,
                "maximum_shortage": max(r["shortage"] for r in rows),
                "allocation_cost": cost.getValue(),
                "violation_penalty": coefficient * sum(r["shortage"] ** 2 for r in rows),
                "objective": model.ObjVal,
                "objective_bound": model.ObjBound,
                "mip_gap": model.MIPGap,
                "fill_rate": total_allocation / total_demand if total_demand else None,
                "regional_fill_rate_std": statistics.pstdev(fill_rates) if fill_rates else None,
            })
        (output_dir / "e03_result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None)
    parser.add_argument("--output-dir", default="results/S01/E03")
    parser.add_argument("--coefficient", type=float, default=None)
    args = parser.parse_args()
    run(load_config(args.config), args.output_dir, args.coefficient)
