"""Streamlit dashboard for EV range and driving-efficiency analytics.

The dashboard reads curated local outputs and presents summary KPIs,
vehicle rankings, model/region comparisons, and a range trend.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="EV Analytics",
    # page_icon="🚗",
    layout="wide"
)

st.title("EV Range & Driving Efficiency Analytics")
st.caption("Telemetry → PySpark → Curated Analytics → Dashboard")

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT/"data/curated_local"

if not (DATA/"vehicle_efficiency.csv").exists():
    st.error("Run `python scripts/run_local_pipeline.py` first.")
    st.stop()

vehicle = pd.read_csv(DATA/"vehicle_efficiency.csv")
model = pd.read_csv(DATA/"model_efficiency.csv")
region = pd.read_csv(DATA/"region_efficiency.csv")
trend = pd.read_csv(DATA/"range_trend.csv")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Total Vehicles", vehicle.vehicle_id.nunique())
c2.metric("Avg Efficiency", f"{vehicle.overall_efficiency.mean():.2f} km/%")
c3.metric("Avg Estimated Range", f"{vehicle.avg_estimated_range_km.mean():.1f} km")
c4.metric("Total Distance", f"{vehicle.total_distance_km.sum():.1f} km")

st.divider()

left,right = st.columns(2)

with left:
    st.subheader("Top 5 Efficiency Vehicles")
    st.dataframe(
        vehicle.nlargest(5,"overall_efficiency")
        [["vehicle_id","model","region","overall_efficiency","total_distance_km"]],
        use_container_width=True,
        hide_index=True
    )

with right:
    st.subheader("Bottom 5 Efficiency Vehicles")
    st.dataframe(
        vehicle.nsmallest(5,"overall_efficiency")
        [["vehicle_id","model","region","overall_efficiency","total_distance_km"]],
        use_container_width=True,
        hide_index=True
    )

st.subheader("Efficiency by Vehicle")
st.bar_chart(
    vehicle.sort_values("overall_efficiency")
    .set_index("vehicle_id")["overall_efficiency"]
)

left,right = st.columns(2)

with left:
    st.subheader("Efficiency by Model")
    st.bar_chart(model.set_index("model")["overall_efficiency"])

with right:
    st.subheader("Efficiency by Region")
    st.bar_chart(region.set_index("region")["overall_efficiency"])

st.subheader("Range Trend")
trend["date"] = pd.to_datetime(trend["date"])
st.line_chart(
    trend.set_index("date")["avg_estimated_range_km"]
)
