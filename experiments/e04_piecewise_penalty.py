import argparse
import json
import statistics
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

from src.base_model import build_model
from src.config_loader import load_config


def run(config, output_dir, coefficient=0.625, breakpoints=None):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    if coefficient <= 0:
        raise ValueError("Coefficient must be positive")
    max_demand = max(r["demand"] for r in config["regions"])
    points = sorted(set(breakpoints if breakpoints is not None else [0, 20, 40, 60, 100, 200]))
    if len(points) < 2 or points[0] != 0:
        raise ValueError("Breakpoints must start at zero and contain at least two distinct values")
    if points[-1] < max_demand:
        points.append(max_demand)
    slopes = [coefficient * (a + b) for a, b in zip(points, points[1:])]
    model, x, v, cost = build_model(config, soft=True)
    with model:
        ids = list(v.keys())
        p = model.addVars(ids, lb=0, name="penalty_cost")
        # Epigraph of a convex piecewise linear interpolation.
        # Positive objective coefficient ensures the epigraph is tight at optimum.
        for i in ids:
            for j, (a, slope) in enumerate(zip(points, slopes)):
                model.addConstr(p[i] >= coefficient * a**2 + slope * (v[i] - a),
                                name=f"pwl_{i}_{j}")
        model.setObjective(cost + gp.quicksum(p[i] for i in ids), GRB.MINIMIZE)
        model.optimize()
        result = {
            "experiment": "E04",
            "scenario": config["experiment"]["scenario_id"],
            "status_code": int(model.Status),
            "status": "OPTIMAL" if model.Status == GRB.OPTIMAL else "NOT_OPTIMAL",
            "runtime_seconds": model.Runtime,
            "node_count": model.NodeCount,
            "quadratic_reference_coefficient": coefficient,
            "breakpoints": points,
            "slopes": slopes,
            "num_variables": model.NumVars,
            "num_constraints": model.NumConstrs,
        }
        if model.SolCount:
            rows = [{"region": r["id"], "demand": r["demand"],
                     "allocation": round(x[r["id"]].X),
                     "shortage": round(v[r["id"]].X),
                     "piecewise_penalty": p[r["id"]].X}
                    for r in config["regions"]]
            demand = sum(r["demand"] for r in rows)
            allocation = sum(r["allocation"] for r in rows)
            rates = [r["allocation"] / r["demand"] for r in rows if r["demand"]]
            pwl_cost = sum(r["piecewise_penalty"] for r in rows)
            quadratic_cost = coefficient * sum(r["shortage"]**2 for r in rows)
            result.update({
                "regions": rows,
                "total_allocation": allocation,
                "total_shortage": sum(r["shortage"] for r in rows),
                "maximum_shortage": max(r["shortage"] for r in rows),
                "allocation_cost": cost.getValue(),
                "violation_penalty": pwl_cost,
                "quadratic_reference_penalty": quadratic_cost,
                "approximation_error_at_solution": pwl_cost - quadratic_cost,
                "objective": model.ObjVal,
                "objective_bound": model.ObjBound,
                "mip_gap": model.MIPGap,
                "fill_rate": allocation / demand if demand else None,
                "regional_fill_rate_std": statistics.pstdev(rates) if rates else None,
            })
        (output_dir / "e04_result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None)
    parser.add_argument("--output-dir", default="results/S01/E04")
    parser.add_argument("--coefficient", type=float, default=0.625)
    parser.add_argument("--breakpoints", type=float, nargs="+", default=None)
    args = parser.parse_args()
    run(load_config(args.config), args.output_dir, args.coefficient, args.breakpoints)
