import json
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

STATE_FILE = Path(__file__).resolve().parents[1] / "data" / "fleet_state.json"

st.set_page_config(page_title="Fleet Map", layout="wide")
st.title("Autonomous Taxi Fleet – Live Map")

# 🔄 Auto-refresh every 2 seconds
st_autorefresh(interval=2000, key="fleet-refresh")

st.caption(f"Reading state from: {STATE_FILE}")

if not STATE_FILE.exists():
    st.error("fleet_state.json not found. Start the consumer first.")
    st.stop()

state = json.loads(STATE_FILE.read_text(encoding="utf-8"))

rows = []
for taxi_id, v in state.items():
    rows.append({
        "taxi_id": taxi_id,
        "lat": v.get("lat"),
        "lon": v.get("lon"),
        "speed": v.get("speed"),
        "battery": v.get("battery"),
        "status": v.get("status", "OK"),
        "last_update": v.get("last_update"),
    })

df = pd.DataFrame(rows).dropna(subset=["lat", "lon"])

st.subheader("Fleet state (debug)")
st.dataframe(df, use_container_width=True)

if df.empty:
    st.warning("No valid GPS points found.")
    st.stop()

# 🗺️ Map with BIG points
fig = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    hover_name="taxi_id",
    hover_data=["speed", "battery", "status", "last_update"],
    color="status",                # color by status
    size=[20] * len(df),            # constant big size
    size_max=25,
    zoom=12
)

fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

st.subheader("Live fleet map")
st.plotly_chart(fig, use_container_width=True)
