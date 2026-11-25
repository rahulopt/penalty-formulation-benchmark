import gurobipy as gp
from gurobipy import GRB


def build_model(config, *, soft=False):
    """Build the common allocation model, with optional shortage variables."""
    regions = {r["id"]: r for r in config["regions"]}
    demand = {i: r["demand"] for i, r in regions.items()}
    model = gp.Model("regional_allocation")
    params = config["solver"]
    for key, value in {
        "TimeLimit": params["time_limit"],
        "MIPGap": params["mip_gap"],
        "Threads": params["threads"],
        "Seed": params["seed"],
        "OutputFlag": params["output_flag"],
    }.items():
        model.setParam(key, value)
    x = model.addVars(regions.keys(), lb=0, vtype=GRB.INTEGER, name="allocation")
    v = model.addVars(regions.keys(), lb=0, vtype=GRB.INTEGER, name="shortage") if soft else None
    model.addConstr(x.sum() <= config["inventory"]["available_units"], name="inventory_capacity")
    for i in regions:
        model.addConstr(x[i] + (v[i] if soft else 0) == demand[i], name=f"demand_{i}")
    cost = gp.quicksum(regions[i]["allocation_cost"] * x[i] for i in regions)
    model.setObjective(cost, GRB.MINIMIZE)
    return model, x, v, cost
