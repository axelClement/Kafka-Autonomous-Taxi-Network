import json
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
STATE_FILE = Path(__file__).resolve().parents[1] / "data" / "fleet_state.json"

st.set_page_config(page_title="Fleet Map", layout="wide")
st.title("Autonomous Taxi Fleet – Live Map")

# Auto-refresh every 2 seconds
st_autorefresh(interval=2000, key="fleet-refresh")

st.caption(f"Reading state from: {STATE_FILE}")

if not STATE_FILE.exists():
    st.error("fleet_state.json not found. Start the consumer first.")
    st.stop()

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
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

df_all = pd.DataFrame(rows)

# --------------------------------------------------
# DEBUG (TOP)
# --------------------------------------------------
st.subheader("Fleet state (debug)")
st.dataframe(df_all, use_container_width=True)

# --------------------------------------------------
# REAL FLEET STATUS (DYNAMIC)
# --------------------------------------------------
st.subheader("Fleet status (real-time)")

col1, col2, col3 = st.columns(3)

nb_ok = (df_all["status"] == "OK").sum()
nb_overspeed = (df_all["status"] == "OVERSPEED").sum()
nb_low_battery = (df_all["status"] == "LOW_BATTERY").sum()

col1.metric("🟢 OK", nb_ok)
col2.metric("🔴 Overspeed", nb_overspeed)
col3.metric("⚠ Low battery", nb_low_battery)

# --------------------------------------------------
# LEGEND (STATIC, ALWAYS VISIBLE)
# --------------------------------------------------
st.subheader("Legend")

legend_col1, legend_col2, legend_col3 = st.columns(3)

legend_col1.markdown("🟢 **OK**  \nNormal operation")
legend_col2.markdown("🔴 **OVERSPEED**  \nSpeed above threshold")
legend_col3.markdown("⚠ **LOW BATTERY**  \nBattery below 20% (symbol on map)")

# --------------------------------------------------
# MAP DATA (ONLY VALID GPS)
# --------------------------------------------------
df = df_all.dropna(subset=["lat", "lon"])
if df.empty:
    st.warning("No valid GPS points found yet.")
    st.stop()

# Base color: OK green, OVERSPEED red
def base_status(row):
    return "OVERSPEED" if row["status"] == "OVERSPEED" else "OK"

df["base_status"] = df.apply(base_status, axis=1)

COLOR_MAP = {
    "OK": "green",
    "OVERSPEED": "red",
}

# --------------------------------------------------
# MAP
# --------------------------------------------------
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

# LOW BATTERY overlay (text symbol, reliable)
low_battery_df = df[df["status"] == "LOW_BATTERY"]
if not low_battery_df.empty:
    fig.add_trace(
        go.Scattermapbox(
            lat=low_battery_df["lat"],
            lon=low_battery_df["lon"],
            mode="text",
            text=["!"] * len(low_battery_df),
            textposition="middle center",
            textfont=dict(size=18, color="black"),
            hoverinfo="skip",
            showlegend=False,
        )
    )

# Remove Plotly legend completely
fig.update_layout(
    mapbox_style="open-street-map",
    showlegend=False,
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)

# --------------------------------------------------
# DISPLAY MAP
# --------------------------------------------------
st.subheader("Live fleet map")
st.plotly_chart(fig, use_container_width=True)
