"""Interactive benchmark dashboard. Run from repository root: streamlit run app.py."""
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
st.set_page_config(page_title="Penalty Formulation Benchmark", layout="wide")
st.title("Penalty Formulation Benchmark")
st.caption("Operations research • inventory allocation • computational trade-offs")

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

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Formulations", "Hybrid sensitivity", "Soft SLA", "Pareto frontier", "Scalability"])

with tab1:
    st.header("Regional allocation comparison")
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
        scenario=st.selectbox("Scenario",sorted(df.scenario.dropna().unique()))
        df=df[df.scenario==scenario]
        options=sorted(df.run.unique())
        selected=st.multiselect("Runs to compare",options,default=options[:min(4,len(options))])
        df=df[df.run.isin(selected)]
        if not df.empty:
            st.plotly_chart(px.bar(df,x="region",y="fill_rate",color="run",barmode="group",range_y=[0,100]),use_container_width=True)
            st.dataframe(df,use_container_width=True,hide_index=True)
    else:
        missing()

with tab2:
    st.header("Fixed + quadratic penalty sensitivity")
    df=read_csv(RESULTS/"S01/E06C/summary.csv")
    if not df.empty:
        df=df.sort_values("fixed_coefficient")
        st.plotly_chart(px.scatter(df,x="fixed_coefficient",y="actual_count",hover_data=["expected_counts","actual_objective","passed"]),use_container_width=True)
        st.dataframe(df,use_container_width=True,hide_index=True)
    else:
        missing()

with tab3:
    st.header("Soft SLA penalty calibration")
    rows=load_json("S03/E08_floor_9_10_mu_*/result.json")
    if rows:
        df=pd.DataFrame(rows).drop_duplicates("sla_coefficient",keep="last").sort_values("sla_coefficient")
        st.plotly_chart(px.scatter(df,x="sla_coefficient",y="total_sla_shortfall",hover_data=["weighted_shortage","objective"]),use_container_width=True)
        scatter(df,"total_sla_shortfall","weighted_shortage",hover_data=["sla_coefficient"])
        st.dataframe(df[["sla_coefficient","status","total_sla_shortfall","weighted_shortage","objective"]],hide_index=True,use_container_width=True)
    else:
        missing()

with tab4:
    st.header("Efficient SLA and priority trade-offs")
    df=read_csv(RESULTS/"S03/E10_floor_9_10/summary.csv")
    if not df.empty:
        df=df[df.status=="OPTIMAL"].drop_duplicates(["sla_shortfall","weighted_shortage"]).sort_values("sla_shortfall")
        if not df.empty:
            st.plotly_chart(px.line(df,x="sla_shortfall",y="weighted_shortage",markers=True),use_container_width=True)
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
    st.header("Computational scalability")
    df=read_csv(RESULTS/"E11/summary.csv")
    if not df.empty:
        st.caption("Solver-only runtime; time-limit observations are censored. OPTIMAL means within configured tolerance.")
        df["sla_success"]=df["met_solver_sla"].astype(str).str.lower().eq("true")
        groups=df.groupby(["regions","mode"],as_index=False).agg(runs=("mode","size"),median_runtime=("runtime_seconds","median"),sla_rate=("sla_success","mean"),median_gap=("gap","median"),mean_min_fill=("min_fill_rate","mean"),mean_max_shortage=("max_shortage","mean"),mean_cost=("transport_activation_cost","mean"))
        groups["sla_rate"]*=100
        groups["median_gap"]*=100
        groups["mean_min_fill"]*=100
        st.plotly_chart(px.line(groups,x="regions",y="median_runtime",color="mode",markers=True,log_y=True),use_container_width=True)
        st.plotly_chart(px.bar(groups,x="regions",y="sla_rate",color="mode",barmode="group",range_y=[0,100]),use_container_width=True)
        st.plotly_chart(px.bar(groups,x="regions",y="mean_min_fill",color="mode",barmode="group"),use_container_width=True)
        st.dataframe(groups,hide_index=True,use_container_width=True)
        st.download_button("Download benchmark results",df.to_csv(index=False),"scalability.csv","text/csv")
    else:
        missing()

st.divider()
st.caption("Synthetic benchmark; three independent instances per size. Raw objectives across penalty families are not directly comparable. No memory or end-to-end latency profiling.")
