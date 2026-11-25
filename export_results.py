"""Export allowlisted research metrics, never raw solver logs or credentials."""
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "results"
TARGET = ROOT / "data" / "benchmark_results"

JSON_FIELDS = set("""experiment scenario status status_code initial_status_code runtime_seconds node_count num_variables num_constraints coefficient penalty_coefficient normalization_power controlled_allocation severity fixed_coefficient severity_coefficient mode order floor service_floor required_inventory available_inventory sla_coefficient epsilon oracle_passed total_allocation total_shortage maximum_shortage violated_regions allocation_cost fixed_penalty variable_penalty violation_penalty demand_penalty sla_penalty objective objective_bound mip_gap fill_rate minimum_regional_fill_rate regional_fill_rate_std weighted_shortage total_sla_shortfall minimum_possible_sla_shortfall sla_shortfall maximum_violation_metric quadratic_reference_penalty approximation_error_at_solution""".split())
REGION_FIELDS = set("region demand priority allocation shortage violated sla_shortfall".split())
CSV_FIELDS = set("""fixed_coefficient expected_counts actual_count expected_objective actual_objective runtime_seconds maximum_shortage passed epsilon status sla_shortfall weighted_shortage allocation_cost oracle_passed mode status_code work_units nodes variables constraints solutions bound objective gap transport_activation_cost total_shortage max_shortage fill_rate min_fill_rate fill_rate_std reference_quadratic_cost regions instance_seed repeat time_limit met_solver_sla""".split())
CSV_PATHS = ["S01/E06C/summary.csv", "S03/E10_floor_9_10/summary.csv", "E11/summary.csv"]

def scalar(v):
    return v is None or isinstance(v,(str,bool,int)) or isinstance(v,float) and math.isfinite(v)

def main():
    if not SOURCE.is_dir():
        raise SystemExit("No local results directory. Run the experiments first.")
    count=0
    regional=[]
    summary=[]
    for path in sorted(SOURCE.glob("S*/**/*.json")):
        if path.name not in ("result.json","e07_result.json") and not path.name.startswith(("e00","e01","e02","e03","e04","e05","e06","epsilon_")):
            continue
        raw=json.loads(path.read_text())
        if not isinstance(raw,dict) or "experiment" not in raw:
            continue
        clean={k:v for k,v in raw.items() if k in JSON_FIELDS and scalar(v)}
        if isinstance(raw.get("regions"),list):
            clean["regions"]=[{k:v for k,v in r.items() if k in REGION_FIELDS and scalar(v)} for r in raw["regions"]]
        rel=path.relative_to(SOURCE)
        dest=TARGET/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(clean,indent=2,allow_nan=False)+"\n")
        count+=1
        run=str(rel.parent)
        summary.append({"run":run,**{k:v for k,v in clean.items() if k!="regions"}})
        for r in clean.get("regions",[]):
            regional.append({"scenario":clean.get("scenario"),"experiment":clean["experiment"],"run":run,**r})
    def write_table(path,rows):
        if rows:
            path.parent.mkdir(parents=True,exist_ok=True)
            fields=sorted(set().union(*(r.keys() for r in rows)))
            with path.open("w",newline="") as f:
                writer=csv.DictWriter(f,fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
    write_table(TARGET/"formulation_comparison.csv",regional)
    write_table(TARGET/"experiment_summary.csv",summary)
    for rel in CSV_PATHS:
        path=SOURCE/rel
        if not path.exists():
            print("Missing:",rel)
            continue
        with path.open(newline="") as f:
            rows=[{k:v for k,v in row.items() if k in CSV_FIELDS} for row in csv.DictReader(f)]
        write_table(TARGET/rel,rows)
        print(f"{rel}: {len(rows)} rows")
    print(f"Exported {count} JSON records and {len(regional)} regional rows to {TARGET}")
    print("Review the exported dataset before committing. Raw logs are not exported.")

if __name__=="__main__":
    main()
