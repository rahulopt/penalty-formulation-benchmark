"""Compare absolute and demand-normalized quadratic shortage penalties."""
import argparse
import json
import statistics
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

from src.base_model import build_model
from src.config_loader import load_config


def run(config, output_dir, power):
    if power not in (0, 1, 2):
        raise ValueError("Power must be 0, 1 or 2")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    model, x, v, cost = build_model(config, soft=True)
    with model:
        regions = config["regions"]
        demand = sum(r["demand"] for r in regions)
        capacity = config["inventory"]["available_units"]
        coefficient = 0.625
        model.addConstr(x.sum() == min(capacity, demand), name="controlled_allocation")
        penalty = coefficient * gp.quicksum(
            v[r["id"]] * v[r["id"]] / (r["demand"] ** power)
            for r in regions if r["demand"] > 0
        )
        model.setObjective(cost + penalty, GRB.MINIMIZE)
        model.setParam("MIPGap", 0)
        model.setParam("MIPGapAbs", 0)
        model.optimize()
        result = {
            "experiment": "E03_normalized",
            "scenario": config["experiment"]["scenario_id"],
            "normalization_power": power,
            "coefficient": coefficient,
            "controlled_allocation": True,
            "status_code": int(model.Status),
            "status": "OPTIMAL" if model.Status == GRB.OPTIMAL else "NOT_OPTIMAL",
            "runtime_seconds": model.Runtime,
            "node_count": model.NodeCount,
        }
        if model.SolCount:
            rows = [{"region": r["id"], "demand": r["demand"],
                     "allocation": round(x[r["id"]].X),
                     "shortage": round(v[r["id"]].X)}
                    for r in regions]
            allocation = sum(r["allocation"] for r in rows)
            rates = [r["allocation"] / r["demand"] for r in rows if r["demand"]]
            result.update({
                "regions": rows,
                "total_allocation": allocation,
                "total_shortage": sum(r["shortage"] for r in rows),
                "maximum_shortage": max(r["shortage"] for r in rows),
                "allocation_cost": cost.getValue(),
                "violation_penalty": penalty.getValue(),
                "objective": model.ObjVal,
                "objective_bound": model.ObjBound,
                "mip_gap": model.MIPGap,
                "fill_rate": allocation / demand if demand else None,
                "minimum_regional_fill_rate": min(rates) if rates else None,
                "regional_fill_rate_std": statistics.pstdev(rates) if rates else None,
            })
        (output_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/s02_heterogeneous.yaml")
    parser.add_argument("--power", type=int, choices=[0, 1, 2], required=True)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    config = load_config(args.config)
    output = args.output_dir or f"results/{config['experiment']['scenario_id']}/E03_normalized_p{args.power}"
    run(config, output, args.power)
