"""Enumerate and validate the integer Pareto frontier for S03."""
import argparse
import csv
import json
from fractions import Fraction
from pathlib import Path

import gurobipy as gp
from gurobipy import GRB

from src.base_model import build_model
from src.config_loader import load_config


def run(config, floor, epsilon):
    floor = Fraction(str(floor))
    if not 0 <= floor <= 1 or epsilon < 0:
        raise ValueError("Invalid floor or epsilon")
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
        model.addConstr(sla <= epsilon, name="epsilon_budget")
        model.ModelSense = GRB.MINIMIZE
        model.setObjectiveN(weighted, 0, priority=3, abstol=0, reltol=0, name="weighted_shortage")
        model.setObjectiveN(sla, 1, priority=2, abstol=0, reltol=0, name="sla_shortfall")
        model.setObjectiveN(cost, 2, priority=1, abstol=0, reltol=0, name="allocation_cost")
        model.setParam("MIPGap", 0)
        model.setParam("MIPGapAbs", 0)
        model.setParam("DualReductions", 0)
        model.optimize()
        status = {GRB.OPTIMAL:"OPTIMAL",GRB.INFEASIBLE:"INFEASIBLE"}.get(model.Status, "OTHER")
        result = {"experiment":"E10","scenario":config["experiment"]["scenario_id"],"floor":float(floor),"epsilon":epsilon,"status":status,"status_code":int(model.Status),"runtime_seconds":model.Runtime}
        if model.SolCount:
            rows = [{"region":i,"allocation":round(x[i].X),"shortage":round(v[i].X),"sla_shortfall":max(0,required[i]-round(x[i].X))} for i in ids]
            result.update({"regions":rows,"total_allocation":sum(r["allocation"] for r in rows),"total_shortage":sum(r["shortage"] for r in rows),"sla_shortfall":sum(r["sla_shortfall"] for r in rows),"weighted_shortage":sum(r["priority"]*row["shortage"] for r,row in zip(regions,rows)),"allocation_cost":cost.getValue()})
        return result


def oracle(epsilon):
    if epsilon < 100:
        return None
    sla = min(epsilon, 180)
    remaining = 180-sla
    weighted = 200
    for marginal in (1,2,3,4):
        units = min(20, remaining)
        weighted += marginal*units
        remaining -= units
    return sla, weighted


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--config",default="configs/s03_priorities.yaml")
    parser.add_argument("--floor",default="0.9")
    parser.add_argument("--epsilon",type=int,nargs="+",default=[99,*range(100,181),181])
    args=parser.parse_args()
    config=load_config(args.config)
    regions=config["regions"]
    use_oracle=(Fraction(args.floor)==Fraction(9,10) and config["inventory"]["available_units"]==800 and [r["demand"] for r in regions]==[200]*5 and [r["priority"] for r in regions]==[5,4,3,2,1] and [r["allocation_cost"] for r in regions]==[10]*5)
    root=Path(f"results/{config['experiment']['scenario_id']}/E10_floor_{Fraction(args.floor).numerator}_{Fraction(args.floor).denominator}")
    root.mkdir(parents=True,exist_ok=True)
    summary=[]
    for epsilon in sorted(set(args.epsilon)):
        result=run(config,args.floor,epsilon)
        expected=oracle(epsilon) if use_oracle else None
        passed=None
        if use_oracle:
            passed=(result["status"]=="INFEASIBLE" if expected is None else result["status"]=="OPTIMAL" and (result.get("sla_shortfall"),result.get("weighted_shortage"))==expected)
        result["oracle_passed"]=passed
        (root/f"epsilon_{epsilon}.json").write_text(json.dumps(result,indent=2)+"\n")
        summary.append({k:result.get(k) for k in ("epsilon","status","sla_shortfall","weighted_shortage","allocation_cost","runtime_seconds","oracle_passed")})
    with (root/"summary.csv").open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    for row in summary:
        print(row)
    if use_oracle:
        print(f"Validated {sum(r['oracle_passed'] for r in summary)}/{len(summary)} cases")
        if not all(r["oracle_passed"] for r in summary):
            raise SystemExit(1)


if __name__=="__main__":
    main()
