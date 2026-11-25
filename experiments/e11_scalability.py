"""Compare penalty formulations on identical capacitated shipment networks."""
import argparse
import csv
import json
import random
import statistics
from pathlib import Path
import gurobipy as gp
from gurobipy import GRB


def instance(n, seed):
    rng = random.Random(seed)
    W = range(max(2, n//5))
    R = range(n)
    K = range(3)
    d = {(r,k):rng.randint(40,200) for r in R for k in K}
    # Every region has two eligible warehouses. Shared supply and activation
    # budgets couple shipments across regions and products.
    edges = [(w,r) for r in R for w in rng.sample(list(W),2)]
    A = [(w,r,k) for w,r in edges for k in K]
    supply = {(w,k):max(1,int(.8*sum(d[r,k] for r in R)/len(W))) for w in W for k in K}
    c = {a:rng.randint(2,10) for a in A}
    return W,R,K,d,edges,A,supply,c


def solve(data, mode, limit, seed):
    W,R,K,d,edges,A,supply,c = data
    with gp.Model() as m:
        m.Params.OutputFlag = 0
        m.Params.Threads = 1
        m.Params.Seed = seed
        m.Params.TimeLimit = limit
        m.Params.MIPGap = .001
        x = m.addVars(A,vtype=GRB.INTEGER,lb=0,name="ship")
        z = m.addVars(edges,vtype=GRB.BINARY,name="active")
        v = m.addVars(list(d),lb=0,vtype=GRB.INTEGER,name="shortage")
        m.addConstrs((gp.quicksum(x[w,r,k] for w,rr in edges if rr==r)+v[r,k]==d[r,k] for r,k in d))
        m.addConstrs((gp.quicksum(x[w,r,k] for ww,r in edges if ww==w)<=supply[w,k] for w in W for k in K))
        m.addConstrs((x[w,r,k]<=d[r,k]*z[w,r] for w,r,k in A))
        m.addConstrs((gp.quicksum(z[w,r] for w,rr in edges if rr==r)<=1 for r in R))
        transport = gp.quicksum(c[a]*x[a] for a in A)+20*z.sum()
        # Calibrate linear and quadratic marginal penalties at 40 units.
        if mode=="linear":
            penalty=50*v.sum()
        elif mode=="quadratic":
            penalty=.625*gp.quicksum(v[i]*v[i] for i in d)
        else:
            p=m.addVars(list(d),lb=0,name="pwl")
            for i in d:
                points=sorted({0,d[i],*(b for b in (20,40,60,100,150) if b<d[i])})
                for a,b in zip(points,points[1:]):
                    m.addConstr(p[i]>=.625*a*a+.625*(a+b)*(v[i]-a))
            penalty=p.sum()
        m.setObjective(transport+penalty,GRB.MINIMIZE)
        m.optimize()
        row={"mode":mode,"status_code":int(m.Status),"runtime_seconds":m.Runtime,
             "work_units":m.Work,"nodes":m.NodeCount,"variables":m.NumVars,
             "constraints":m.NumConstrs,"solutions":m.SolCount,"bound":m.ObjBound}
        if m.SolCount:
            shortages={i:round(v[i].X) for i in d}
            rates=[1-shortages[i]/d[i] for i in d]
            row.update(objective=m.ObjVal,gap=m.MIPGap,transport_activation_cost=transport.getValue(),
                       total_shortage=sum(shortages.values()),max_shortage=max(shortages.values()),
                       fill_rate=1-sum(shortages.values())/sum(d.values()),
                       min_fill_rate=min(rates),fill_rate_std=statistics.pstdev(rates),
                       reference_quadratic_cost=transport.getValue()+.625*sum(a*a for a in shortages.values()))
        return row


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--sizes",nargs="+",type=int,default=[10,25,50])
    p.add_argument("--seeds",nargs="+",type=int,default=[42,43,44])
    p.add_argument("--repeats",type=int,default=2)
    p.add_argument("--limit",type=float,default=15)
    args=p.parse_args()
    if min(args.sizes)<2 or args.repeats<1 or args.limit<=0:
        p.error("Invalid size, repeats or time limit")
    root=Path("results/E11")
    root.mkdir(parents=True,exist_ok=True)
    rows=[]
    for n in args.sizes:
        for seed in args.seeds:
            data=instance(n,seed)
            for repeat in range(args.repeats):
                modes=["linear","quadratic","pwl"]
                random.Random(seed+repeat).shuffle(modes)
                for mode in modes:
                    row=solve(data,mode,args.limit,seed)
                    row.update(regions=n,instance_seed=seed,repeat=repeat,time_limit=args.limit,
                               met_solver_sla=row["status_code"]==GRB.OPTIMAL and row["runtime_seconds"]<=args.limit)
                    rows.append(row)
                    print(json.dumps(row),flush=True)
                    fields=sorted(set().union(*(r.keys() for r in rows)))
                    with (root/"summary.csv").open("w",newline="") as f:
                        writer=csv.DictWriter(f,fieldnames=fields)
                        writer.writeheader()
                        writer.writerows(rows)
    print(f"Completed {len(rows)} runs; results/E11/summary.csv")


if __name__=="__main__":
    main()
