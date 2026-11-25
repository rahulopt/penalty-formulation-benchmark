"""Soft regional service floor with a separate linear SLA shortfall penalty."""
import argparse
import json
from fractions import Fraction
from pathlib import Path
import gurobipy as gp
from gurobipy import GRB
from src.base_model import build_model
from src.config_loader import load_config


def run(config, floor, mu):
    floor = Fraction(str(floor))
    if not 0 <= floor <= 1 or mu < 0:
        raise ValueError("Invalid SLA floor or penalty")
    regions = config["regions"]
    ids = [r["id"] for r in regions]
    required = {r["id"]: -(-(floor.numerator*r["demand"])//floor.denominator) for r in regions}
    capacity = config["inventory"]["available_units"]
    model, x, v, cost = build_model(config, soft=True)
    with model:
        model.addConstr(x.sum() == min(capacity, sum(r["demand"] for r in regions)))
        s = model.addVars(ids, lb=0, ub=required, vtype=GRB.INTEGER, name="sla_shortfall")
        for i in ids:
            model.addConstr(x[i]+s[i] >= required[i], name=f"soft_sla_{i}")
        penalty = config["penalties"]["linear"]["coefficient"] * gp.quicksum(r["priority"]*v[r["id"]] for r in regions)
        model.setObjective(cost + penalty + mu*s.sum(), GRB.MINIMIZE)
        model.setParam("MIPGap", 0)
        model.setParam("MIPGapAbs", 0)
        model.optimize()
        result = {"experiment":"E08", "scenario":config["experiment"]["scenario_id"], "floor":float(floor), "sla_coefficient":mu, "status_code":int(model.Status), "status":"OPTIMAL" if model.Status == GRB.OPTIMAL else "OTHER", "runtime_seconds":model.Runtime}
        if model.SolCount:
            rows = [{"region":i, "allocation":round(x[i].X), "shortage":round(v[i].X), "sla_shortfall":max(0, required[i]-round(x[i].X))} for i in ids]
            actual_sla = sum(r["sla_shortfall"] for r in rows)
            result.update({"regions":rows,"total_shortage":sum(r["shortage"] for r in rows),"total_sla_shortfall":actual_sla,"minimum_possible_sla_shortfall":max(0,sum(required.values())-capacity),"weighted_shortage":sum(r["priority"]*row["shortage"] for r,row in zip(regions,rows)),"allocation_cost":cost.getValue(),"demand_penalty":penalty.getValue(),"sla_penalty":mu*actual_sla,"objective":model.ObjVal,"mip_gap":model.MIPGap})
        out = Path(f"results/{config['experiment']['scenario_id']}/E08_floor_{floor.numerator}_{floor.denominator}_mu_{mu}")
        out.mkdir(parents=True,exist_ok=True)
        (out/"result.json").write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps(result,indent=2))
        return result


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",default="configs/s03_priorities.yaml")
    parser.add_argument("--floor",default="0.9")
    parser.add_argument("--mu",type=float,nargs="+",default=[0,25,75,125,500])
    args=parser.parse_args()
    for mu in args.mu:
        run(load_config(args.config),args.floor,mu)
