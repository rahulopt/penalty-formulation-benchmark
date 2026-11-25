"""Hierarchical linear objectives with controlled allocation."""
import argparse
import json
from fractions import Fraction
from pathlib import Path
import gurobipy as gp
from gurobipy import GRB
from src.base_model import build_model
from src.config_loader import load_config


def run(config, floor, order):
    floor = Fraction(str(floor))
    if not 0 <= floor <= 1:
        raise ValueError("SLA floor must be between zero and one")
    regions = config["regions"]
    ids = [r["id"] for r in regions]
    required = {r["id"]: -(-(floor.numerator*r["demand"])//floor.denominator) for r in regions}
    capacity = config["inventory"]["available_units"]
    model, x, v, cost = build_model(config, soft=True)
    with model:
        model.addConstr(x.sum() == min(capacity, sum(r["demand"] for r in regions)), name="controlled_allocation")
        s = model.addVars(ids, lb=0, ub=required, vtype=GRB.INTEGER, name="sla_shortfall")
        for i in ids:
            model.addConstr(x[i]+s[i] >= required[i], name=f"soft_sla_{i}")
        sla = s.sum()
        weighted = gp.quicksum(r["priority"]*v[r["id"]] for r in regions)
        objectives = [(sla, "sla_shortfall"), (weighted, "weighted_shortage")] if order == "sla-first" else [(weighted, "weighted_shortage"), (sla, "sla_shortfall")]
        objectives.append((cost, "allocation_cost"))
        model.ModelSense = GRB.MINIMIZE
        for index, (expr, name) in enumerate(objectives):
            model.setObjectiveN(expr, index, priority=3-index, weight=1, abstol=0, reltol=0, name=name)
        model.setParam("MIPGap", 0)
        model.setParam("MIPGapAbs", 0)
        model.optimize()
        result = {"experiment":"E09", "scenario":config["experiment"]["scenario_id"], "floor":float(floor), "order":order, "status_code":int(model.Status), "status":"OPTIMAL" if model.Status == GRB.OPTIMAL else "NOT_OPTIMAL", "runtime_seconds":model.Runtime}
        if model.SolCount:
            rows = [{"region":i,"allocation":round(x[i].X),"shortage":round(v[i].X),"sla_shortfall":max(0,required[i]-round(x[i].X))} for i in ids]
            result.update({"regions":rows,"total_allocation":sum(r["allocation"] for r in rows),"total_shortage":sum(r["shortage"] for r in rows),"total_sla_shortfall":sum(r["sla_shortfall"] for r in rows),"weighted_shortage":sum(r["priority"]*row["shortage"] for r,row in zip(regions,rows)),"allocation_cost":cost.getValue(),"objective_values":{name:expr.getValue() for expr,name in objectives}})
        out = Path(f"results/{config['experiment']['scenario_id']}/E09_{order}_floor_{floor.numerator}_{floor.denominator}")
        out.mkdir(parents=True,exist_ok=True)
        (out/"result.json").write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps(result,indent=2))
        return result


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",default="configs/s03_priorities.yaml")
    parser.add_argument("--floor",default="0.9")
    parser.add_argument("--order",choices=["sla-first","priority-first","both"],default="both")
    args=parser.parse_args()
    for order in (["sla-first","priority-first"] if args.order=="both" else [args.order]):
        run(load_config(args.config),args.floor,order)
