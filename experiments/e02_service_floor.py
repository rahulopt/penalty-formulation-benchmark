"""Weighted penalties with hard minimum regional service levels."""
import argparse
import json
import statistics
from fractions import Fraction
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB
from src.base_model import build_model
from src.config_loader import load_config


def run(config, output_dir, mode, floor):
    floor = Fraction(str(floor))
    if not 0 <= floor <= 1 or mode not in ("linear", "quadratic"):
        raise ValueError("Invalid service floor or penalty mode")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    regions = config["regions"]
    demand = sum(r["demand"] for r in regions)
    capacity = config["inventory"]["available_units"]
    coefficient = config["penalties"][mode]["coefficient"]
    required = {r["id"]: -(-(floor.numerator*r["demand"])//floor.denominator) for r in regions}
    model, x, v, cost = build_model(config, soft=True)
    with model:
        model.addConstr(x.sum() == min(demand, capacity), name="controlled_allocation")
        for r in regions:
            i = r["id"]
            model.addConstr(x[i] >= required[i], name=f"service_floor_{i}")
        penalty = coefficient * gp.quicksum(
            r["priority"] * (v[r["id"]] if mode == "linear" else v[r["id"]]*v[r["id"]])
            for r in regions
        )
        model.setObjective(cost + penalty, GRB.MINIMIZE)
        model.setParam("MIPGap", 0)
        model.setParam("MIPGapAbs", 0)
        model.optimize()
        initial_status = int(model.Status)
        runtime = model.Runtime
        if model.Status == GRB.INF_OR_UNBD:
            model.setParam("DualReductions", 0)
            model.reset()
            model.optimize()
            runtime += model.Runtime
        status = {GRB.OPTIMAL: "OPTIMAL", GRB.INFEASIBLE: "INFEASIBLE",
                  GRB.INF_OR_UNBD: "INF_OR_UNBD", GRB.UNBOUNDED: "UNBOUNDED",
                  GRB.TIME_LIMIT: "TIME_LIMIT"}.get(model.Status, "OTHER")
        result = {"experiment":"E02_service_floor", "scenario":config["experiment"]["scenario_id"],
                  "mode":mode, "service_floor":float(floor), "required_inventory":sum(required.values()),
                  "available_inventory":capacity, "status":status, "status_code":int(model.Status),
                  "runtime_seconds":runtime, "initial_status_code":initial_status, "node_count":model.NodeCount}
        if model.SolCount:
            rows = [{"region":r["id"], "priority":r["priority"], "demand":r["demand"],
                     "allocation":round(x[r["id"]].X), "shortage":round(v[r["id"]].X)} for r in regions]
            rates = [r["allocation"]/r["demand"] for r in rows if r["demand"]]
            result.update({"regions":rows, "total_allocation":sum(r["allocation"] for r in rows),
                           "total_shortage":sum(r["shortage"] for r in rows),
                           "weighted_shortage":sum(r["priority"]*r["shortage"] for r in rows),
                           "maximum_shortage":max(r["shortage"] for r in rows),
                           "minimum_regional_fill_rate":min(rates) if rates else None,
                           "regional_fill_rate_std":statistics.pstdev(rates) if rates else None,
                           "allocation_cost":cost.getValue(), "violation_penalty":penalty.getValue(),
                           "objective":model.ObjVal, "mip_gap":model.MIPGap})
        (output_dir / "result.json").write_text(json.dumps(result, indent=2)+"\n")
        print(json.dumps(result, indent=2))
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/s03_priorities.yaml")
    parser.add_argument("--mode", choices=["linear", "quadratic"], required=True)
    parser.add_argument("--floor", required=True)
    args = parser.parse_args()
    config = load_config(args.config)
    run(config, f"results/{config['experiment']['scenario_id']}/E02_floor_{args.mode}_{args.floor}", args.mode, args.floor)
