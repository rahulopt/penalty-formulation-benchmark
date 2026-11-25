"""Interactive benchmark dashboard. Run from repository root: streamlit run app.py."""
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
st.set_page_config(page_title="Penalty Formulation Benchmark", layout="wide")
st.title("How should we allocate scarce inventory?")
st.caption("A comparative optimization study | Penalty formulation, fairness, business priorities and solver performance")
st.markdown("""
When inventory is insufficient, an optimizer must decide **who receives stock and who bears the shortage**.
A mathematically optimal allocation can still leave a customer region completely unserved.
This study investigates how changing the penalty for unmet demand changes that decision — and how much computation is required.
""")
a,b,c=st.columns(3)
a.metric("Illustrative demand", "1,000 units")
b.metric("Available inventory", "800 units")
c.metric("Unavoidable shortage", "200 units")
st.caption("Controlled five-region scenarios; the network scalability study uses separate synthetic instances.")
with st.expander("Start here: study design and terminology", expanded=True):
    st.markdown("""
**Research question:** Can we balance shortage severity, business priority and operational service guarantees without exceeding the solver time budget?

| Method | Meaning |
|---|---|
| Linear penalty | Each additional unit of shortage has a constant cost. |
| Quadratic penalty | The marginal penalty rises with shortage severity. |
| Piecewise Linear (PWL) penalty | Connected straight-line segments approximate the quadratic curve while retaining a linear objective and constraints. |
| Fixed + quadratic penalty | A fixed charge for any affected region plus a growing severity charge. |
| Minimax | Minimize the worst absolute or percentage shortage. |
| Weighted penalty | Higher-priority regions incur higher shortage penalties. |
| Hard / soft Service-Level Agreement (SLA) | Enforce a minimum service target, or allow and penalize shortfalls. |
| Lexicographic optimization | Optimize objectives in strict priority order. |
| Epsilon-constraint | Minimize one objective while imposing an explicit budget on another. |

**Fill rate** = allocated units / demand. **Weighted shortage** = shortage multiplied by business priority, summed across regions. **MIP gap** = relative optimality gap for a mixed-integer optimization model. **Solver SLA** = optimal termination within the configured time and gap tolerances; distinct from the regional service SLA.
""")
    st.latex(r"x_i+v_i=d_i,\qquad \sum_i x_i\leq C")
    st.caption("Allocation x, unmet demand v, demand d and available inventory C.")
    st.markdown("**How to explore:** start with the controlled scenarios, then investigate penalty calibration, business trade-offs and computational scalability. All result charts read saved solver outputs.")
SCENARIOS={"S01":"S01 — Equal demand and priorities","S02":"S02 — Unequal regional demand","S03":"S03 — Different business priorities"}
MODES={"linear":"Linear penalty","quadratic":"Quadratic penalty","pwl":"Piecewise Linear (PWL) penalty"}
def run_label(path):
    key=path.split("/")[1] if "/" in path else path
    names={"E00":"Hard demand constraint","E01":"Linear penalty","E03":"Quadratic penalty","E04":"Piecewise Linear (PWL) penalty","E04A":"Piecewise Linear (PWL) — fine breakpoints","E04B":"Piecewise Linear (PWL) — coarse breakpoints","E04C":"Piecewise Linear (PWL) — targeted breakpoints","E04D":"Piecewise Linear (PWL) — single segment","E05":"Fixed penalty","E06A":"Fixed + linear penalty","E06B":"Fixed + quadratic penalty","E07":"Absolute minimax","E07A":"Absolute minimax","E07B":"Relative minimax","E03_normalized_p0":"Absolute quadratic","E03_normalized_p1":"Demand-normalized quadratic","E03_normalized_p2":"Squared relative shortage","E02_linear":"Priority-weighted linear","E02_quadratic":"Priority-weighted quadratic"}
    if key.startswith("E02_floor_"):
        parts=key.split("_")
        return f"Weighted {parts[2]} — {float(parts[3]):.0%} hard service floor"
    return names.get(key,key)+f" ({path})"


def load_json(pattern):
    rows = []
    for path in sorted(RESULTS.glob(pattern)):
        try:
            d = json.loads(path.read_text())
            if isinstance(d, dict):
                rows.append(d)
        except (OSError, ValueError) as exc:
            st.warning(f"Could not read {path.name}: {exc}")
    return rows

def read_csv(path):
    return pd.read_csv(path) if path.exists() else pd.DataFrame()

def missing():
    st.info("No local results found for this view. Run the corresponding experiment from the repository root.")

def scatter(df, x, y, color=None, **kwargs):
    st.plotly_chart(px.scatter(df, x=x, y=y, color=color, **kwargs), use_container_width=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["1. Allocation & fairness", "2. Hybrid penalty", "3. Service guarantees", "4. Business trade-offs", "5. Solver scalability"])

with tab1:
    st.header("Who bears the shortage?")
    st.markdown("Compare how different penalty functions distribute limited inventory. Equal shortage units need not mean equal service percentages when regional demands differ. Higher business priorities can justify differentiated service.")
    rows = []
    for path in sorted(RESULTS.glob("S*/**/*.json")):
        try:
            d = json.loads(path.read_text())
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict) or d.get("status") != "OPTIMAL" or not d.get("regions"):
            continue
        if d.get("experiment") in ("E08", "E09", "E10"):
            continue
        if not all("demand" in r for r in d["regions"]):
            continue
        for r in d["regions"]:
            if r["demand"]:
                rows.append({"scenario":d.get("scenario"),"run":str(path.parent.relative_to(RESULTS)),"region":r["region"],"allocation":r["allocation"],"shortage":r["shortage"],"fill_rate":100*r["allocation"]/r["demand"]})
    if rows:
        df=pd.DataFrame(rows)
        scenario=st.selectbox("Choose a controlled scenario",sorted(df.scenario.dropna().unique()),format_func=lambda s:SCENARIOS.get(s,s))
        st.caption(SCENARIOS.get(scenario,scenario))
        df=df[df.scenario==scenario]
        options=sorted(df.run.unique())
        selected=st.multiselect("Runs to compare",options,default=options[:min(4,len(options))],format_func=run_label)
        df=df[df.run.isin(selected)]
        if not df.empty:
            df=df.copy()
            df["Formulation"]=df.run.map(run_label)
            st.plotly_chart(px.bar(df,x="region",y="fill_rate",color="Formulation",barmode="group",range_y=[0,100],labels={"region":"Region","fill_rate":"Demand fulfilled (%)"},title="Regional service levels"),use_container_width=True)
            kpis=df.groupby("Formulation",as_index=False).agg(total_allocation=("allocation","sum"),total_shortage=("shortage","sum"),worst_fill_rate=("fill_rate","min"),maximum_shortage=("shortage","max"))
            st.dataframe(kpis,hide_index=True,use_container_width=True)
            st.caption("Higher worst fill rate means better protection of the least-served region; lower maximum shortage means less severe individual shortages.")
            st.dataframe(df,use_container_width=True,hide_index=True)
    else:
        missing()

with tab2:
    st.header("How many regions should bear the shortage?")
    st.markdown("A fixed charge discourages opening new shortage locations; a quadratic charge discourages severe shortages. In S01 we keep the total shortage at 200 units and vary only the fixed charge.")
    df=read_csv(RESULTS/"S01/E06C/summary.csv")
    if not df.empty:
        df=df.sort_values("fixed_coefficient")
        st.plotly_chart(px.scatter(df,x="fixed_coefficient",y="actual_count",hover_data=["expected_counts","actual_objective","passed"],labels={"fixed_coefficient":"Fixed charge per affected region","actual_count":"Number of affected regions"},title="Observed shortage concentration"),use_container_width=True)
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:
        missing()

with tab3:
    st.header("What if a service guarantee is impossible?")
    st.markdown("In S03, a 90% regional service target requires 900 units, but only 800 exist. A hard guarantee is infeasible. A soft guarantee allows an explicit shortfall with an additional penalty. The minimum aggregate shortfall is 100 units.")
    st.latex(r"s_i\geq 0.9d_i-x_i,\qquad s_i\geq0")
    rows=load_json("S03/E08_floor_9_10_mu_*/result.json")
    if rows:
        df=pd.DataFrame(rows).drop_duplicates("sla_coefficient",keep="last").sort_values("sla_coefficient")
        st.plotly_chart(px.scatter(df,x="sla_coefficient",y="total_sla_shortfall",hover_data=["weighted_shortage","objective"],labels={"sla_coefficient":"Penalty per unit of SLA shortfall","total_sla_shortfall":"Aggregate SLA shortfall (units)"},title="Service shortfall versus penalty coefficient"),use_container_width=True)
        scatter(df,"total_sla_shortfall","weighted_shortage",hover_data=["sla_coefficient"])
        st.dataframe(df[["sla_coefficient","status","total_sla_shortfall","weighted_shortage","objective"]],hide_index=True,use_container_width=True)
    else:
        missing()

with tab4:
    st.header("Choose an acceptable business compromise")
    st.markdown("The epsilon-constraint method finds the smallest priority-weighted shortage allowed by a chosen SLA shortfall budget. Each nondominated point represents a different efficient compromise; reducing one metric requires worsening the other. Strict lexicographic optimization selects the extreme points.")
    df=read_csv(RESULTS/"S03/E10_floor_9_10/summary.csv")
    if not df.empty:
        df=df[df.status=="OPTIMAL"].drop_duplicates(["sla_shortfall","weighted_shortage"]).sort_values("sla_shortfall")
        if not df.empty:
            st.plotly_chart(px.line(df,x="sla_shortfall",y="weighted_shortage",markers=True,labels={"sla_shortfall":"Aggregate SLA shortfall (units)","weighted_shortage":"Priority-weighted shortage"},title="Efficient trade-off frontier"),use_container_width=True)
            choice=st.select_slider("SLA shortfall budget",options=sorted(df.epsilon.unique()))
            row=df[df.epsilon==choice].iloc[0]
            a,b,c=st.columns(3)
            a.metric("SLA shortfall",int(row.sla_shortfall))
            b.metric("Weighted shortage",int(row.weighted_shortage))
            c.metric("Allocation cost",f"{row.allocation_cost:,.0f}")
            path=RESULTS/f"S03/E10_floor_9_10/epsilon_{int(choice)}.json"
            if path.exists():
                regions=pd.DataFrame(json.loads(path.read_text())["regions"])
                st.plotly_chart(px.bar(regions,x="region",y=["allocation","shortage"],barmode="stack"),use_container_width=True)
    else:
        missing()

with tab5:
    st.header("Can the formulation meet the solver deadline?")
    st.markdown("The coupled network includes multiple warehouses, three stock keeping units (SKUs), eligible routes and binary warehouse assignments. Each formulation sees the same generated instances. We compare computational effort and service quality, not raw objective values across different penalties.")
    df=read_csv(RESULTS/"E11/summary.csv")
    if not df.empty:
        st.caption("Solver-only runtime; time-limit observations are censored. OPTIMAL means within configured tolerance.")
        df["sla_success"]=df["met_solver_sla"].astype(str).str.lower().eq("true")
        groups=df.groupby(["regions","mode"],as_index=False).agg(runs=("mode","size"),median_runtime=("runtime_seconds","median"),sla_rate=("sla_success","mean"),median_gap=("gap","median"),mean_min_fill=("min_fill_rate","mean"),mean_max_shortage=("max_shortage","mean"),mean_cost=("transport_activation_cost","mean"))
        groups["sla_rate"]*=100
        groups["median_gap"]*=100
        groups["mean_min_fill"]*=100
        groups["mode"]=groups["mode"].map(MODES)
        a,b,c=st.columns(3)
        a.metric("Recorded solver runs",len(df))
        b.metric("Solver SLA met",f"{int(df.sla_success.sum())}/{len(df)}")
        c.metric("Feasible incumbents",int((df.solutions>0).sum()))
        st.plotly_chart(px.line(groups,x="regions",y="median_runtime",color="mode",markers=True,log_y=True,labels={"regions":"Number of regions","median_runtime":"Median solver runtime (seconds)","mode":"Formulation"},title="Runtime by network size (log scale)"),use_container_width=True)
        st.plotly_chart(px.bar(groups,x="regions",y="sla_rate",color="mode",barmode="group",range_y=[0,100],labels={"regions":"Number of regions","sla_rate":"Solver SLA success (%)","mode":"Formulation"},title="Deadline compliance"),use_container_width=True)
        st.plotly_chart(px.bar(groups,x="regions",y="mean_min_fill",color="mode",barmode="group",labels={"regions":"Number of regions","mean_min_fill":"Mean worst region-SKU fill rate (%)","mode":"Formulation"},title="Protection of least-served demand"),use_container_width=True)
        st.plotly_chart(px.bar(groups,x="regions",y="mean_max_shortage",color="mode",barmode="group",labels={"regions":"Number of regions","mean_max_shortage":"Mean maximum shortage (units)","mode":"Formulation"},title="Shortage severity"),use_container_width=True)
        st.dataframe(groups,hide_index=True,use_container_width=True)
        st.markdown("**Interpretation:** A faster solver is not automatically a better business decision. Check deadline success alongside worst service, shortage severity and transportation cost. Time-limited feasible incumbents remain useful, but are not certified optimal.")
        st.download_button("Download benchmark results",df.to_csv(index=False),"scalability.csv","text/csv")
    else:
        missing()

st.divider()
st.caption("Synthetic benchmark; three independent instances per size. Raw objectives across penalty families are not directly comparable. No memory or end-to-end latency profiling.")
