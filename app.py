"""
Stage 5: VISUALIZATION DASHBOARD (Streamlit + Plotly)
Run:  streamlit run app.py
Matches slide 9: Summary KPIs | Trend charts | Cause & severity | State/City comparison
(+ hotspot map and hour/day heatmap from the methodology slide)
"""
import os
import subprocess
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

from clean_data import clean

# Auto-create the data on first run (needed on Streamlit Cloud / Codespaces)
if not os.path.exists("data/accidents_clean.csv"):
    subprocess.run([sys.executable, "generate_data.py"], check=True)
    subprocess.run([sys.executable, "clean_data.py"], check=True)

st.set_page_config(page_title="Traffic Accident Dashboard", page_icon="🚦", layout="wide")
SEV_COLORS = {"Minor": "#f5a623", "Serious": "#2b7a9b", "Fatal": "#ef8354"}


def show(fig, container=st):
    """Render a plotly figure on both old and new Streamlit versions."""
    try:
        container.plotly_chart(fig, width="stretch")
    except TypeError:
        container.plotly_chart(fig)


@st.cache_data
def load(path="data/accidents_clean.csv"):
    return pd.read_csv(path, parse_dates=["date"])


# ---------- data source ----------
st.sidebar.title("🚦 Filters")
upload = st.sidebar.file_uploader("Optional: upload your own accident CSV", type="csv")
if upload:
    df = clean(pd.read_csv(upload))
elif os.path.exists("data/accidents_clean.csv"):
    df = load()
else:
    st.error("No data found. Run:  python generate_data.py  then  python clean_data.py")
    st.stop()

years = sorted(df.year.unique())
sel_years = st.sidebar.multiselect("Year", years, default=years)
sel_sev = st.sidebar.multiselect("Severity", list(SEV_COLORS), default=list(SEV_COLORS))
sel_state = st.sidebar.multiselect("State", sorted(df.state.unique()), default=sorted(df.state.unique()))

f = df[df.year.isin(sel_years) & df.severity.isin(sel_sev) & df.state.isin(sel_state)]
if f.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# ---------- KPIs ----------
st.title("Traffic Accident Data Analysis & Visualization System")
by_year = f.groupby("year").size()
yoy = ((by_year.iloc[-1] - by_year.iloc[-2]) / by_year.iloc[-2] * 100) if len(by_year) > 1 else None

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total accidents", f"{len(f):,}")
k2.metric("Fatal accidents", f"{(f.severity == 'Fatal').sum():,}")
k3.metric("Total casualties", f"{int(f.casualties.sum()):,}")
k4.metric("YoY change (latest year)", f"{yoy:+.1f}%" if yoy is not None else "n/a")

# ---------- trend ----------
st.subheader("Accidents over time")
trend = f.groupby(["year", "severity"]).size().reset_index(name="accidents")
show(px.line(trend, x="year", y="accidents", color="severity", markers=True,
                        color_discrete_map=SEV_COLORS))

# ---------- cause + severity ----------
c1, c2 = st.columns(2)
cause = (f.cause.value_counts(normalize=True) * 100).round(1).reset_index()
cause.columns = ["cause", "percent"]
with c1:
    st.subheader("Accidents by cause (%)")
    show(px.bar(cause.sort_values("percent"), x="percent", y="cause", orientation="h",
                text="percent", color_discrete_sequence=["#f5a623"]))
with c2:
    st.subheader("Accidents by severity")
    show(px.pie(f, names="severity", hole=.5, color="severity",
                color_discrete_map=SEV_COLORS))

# ---------- state / city comparison ----------
st.subheader("State / City comparison")
level = st.radio("Rank by", ["city", "state"], horizontal=True)
rank = f.groupby(level).size().sort_values(ascending=False).head(15).reset_index(name="accidents")
show(px.bar(rank, x=level, y="accidents", color="accidents",
                       color_continuous_scale="Blues"))

# ---------- time patterns ----------
st.subheader("When do accidents happen?")
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
heat = f.groupby(["day_of_week", "hour"]).size().reset_index(name="n")
heat["day_of_week"] = pd.Categorical(heat.day_of_week, days, ordered=True)
heat = heat.pivot(index="day_of_week", columns="hour", values="n")
show(px.imshow(heat, aspect="auto", color_continuous_scale="YlOrRd",
                          labels=dict(x="Hour of day", y="", color="Accidents")))

# ---------- hotspot map ----------
st.subheader("Accident hotspot map")
sample = f.sample(min(len(f), 8000), random_state=1)
show(
    px.density_map(sample, lat="latitude", lon="longitude", radius=8, zoom=3.8,
                   center=dict(lat=22, lon=79), map_style="carto-positron")
    if hasattr(px, "density_map") else
    px.density_mapbox(sample, lat="latitude", lon="longitude", radius=8, zoom=3.8,
                      center=dict(lat=22, lon=79), mapbox_style="carto-positron")
)

with st.expander("View filtered data"):
    st.dataframe(f.head(1000))
    st.download_button("Download filtered CSV", f.to_csv(index=False), "filtered_accidents.csv")
