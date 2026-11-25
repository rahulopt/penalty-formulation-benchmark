import json
from pathlib import Path
import argparse

from gurobipy import GRB
from src.base_model import build_model
from src.config_loader import load_config


def run(config, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with build_model(config, soft=False)[0] as model:
        model.optimize()
        result = {
            "experiment": "E00",
            "scenario": config["experiment"]["scenario_id"],
            "status_code": int(model.Status),
            "runtime_seconds": model.Runtime,
            "total_demand": sum(r["demand"] for r in config["regions"]),
            "available_inventory": config["inventory"]["available_units"],
        }
        if model.Status == GRB.INFEASIBLE:
            result["status"] = "INFEASIBLE"
            model.computeIIS()
            result["iis_constraints"] = [c.ConstrName for c in model.getConstrs() if c.IISConstr]
            result["iis_minimal"] = bool(model.IISMinimal)
            model.write(str(output_dir / "e00_iis.ilp"))
        elif model.SolCount:
            result["status"] = "OPTIMAL" if model.Status == GRB.OPTIMAL else "INCUMBENT"
            result["objective"] = model.ObjVal
        else:
            result["status"] = "NO_INCUMBENT"
        (output_dir / "e00_result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=None)
    parser.add_argument("--output-dir", default="results/S01/E00")
    args = parser.parse_args()
    run(load_config(args.config), args.output_dir)
