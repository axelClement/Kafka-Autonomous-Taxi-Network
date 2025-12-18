import json
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

STATE_FILE = Path(__file__).resolve().parents[1] / "data" / "fleet_state.json"

st.set_page_config(page_title="Fleet Map", layout="wide")
st.title("Autonomous Taxi Fleet – Live Map")

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

if df.empty:
    st.warning("No valid GPS points found.")
    st.stop()



def base_color(row):
    if row["status"] == "OVERSPEED":
        return "OVERSPEED"
    return "OK"

df["base_status"] = df.apply(base_color, axis=1)

COLOR_MAP = {
    "OK": "green",
    "OVERSPEED": "red",
}



fig = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    hover_name="taxi_id",
    hover_data=["speed", "battery", "status", "last_update"],
    color="base_status",
    color_discrete_map=COLOR_MAP,
    zoom=12,
    center={"lat": 48.8566, "lon": 2.3522},
)

fig.update_traces(marker=dict(size=20, opacity=0.9))



low_battery_df = df[df["status"] == "LOW_BATTERY"]

if not low_battery_df.empty:
    fig.add_trace(
        go.Scattermapbox(
            lat=low_battery_df["lat"],
            lon=low_battery_df["lon"],
            mode="markers",
            marker=dict(
                size=26,
                color="yellow",
                symbol="battery",   # Mapbox symbol
                opacity=0.95,
            ),
            name="Low Battery",
            hoverinfo="skip",
        )
    )

fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    legend_title_text="Status",
)

st.subheader("Live fleet map")
st.plotly_chart(fig, use_container_width=True)

# Optional debug table
with st.expander("Fleet state (debug)"):
    st.dataframe(df, use_container_width=True)
