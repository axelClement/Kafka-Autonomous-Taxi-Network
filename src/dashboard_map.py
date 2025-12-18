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

SPEED_LIMIT = 110
LOW_BATTERY_LIMIT = 20

st.set_page_config(page_title="Fleet Map", layout="wide")
st.title("Autonomous Taxi Fleet – Live Map")

# 🔄 Auto-refresh every 2 seconds
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
        "raw_status": v.get("status", "OK"),  # kept for reference
        "last_update": v.get("last_update"),
    })

df_all = pd.DataFrame(rows)

# Ensure numeric
df_all["speed"] = pd.to_numeric(df_all["speed"], errors="coerce")
df_all["battery"] = pd.to_numeric(df_all["battery"], errors="coerce")

# --------------------------------------------------
# DERIVED FLAGS (SOURCE OF TRUTH)
# --------------------------------------------------
df_all["is_overspeed"] = df_all["speed"] > SPEED_LIMIT
df_all["is_low_battery"] = df_all["battery"] < LOW_BATTERY_LIMIT

def compute_display_status(row):
    if row["is_overspeed"] and row["is_low_battery"]:
        return "OVERSPEED + LOW_BATTERY"
    if row["is_overspeed"]:
        return "OVERSPEED"
    if row["is_low_battery"]:
        return "LOW_BATTERY"
    return "OK"

df_all["display_status"] = df_all.apply(compute_display_status, axis=1)

# --------------------------------------------------
# DEBUG (TOP) — NOW CORRECT
# --------------------------------------------------
st.subheader("Fleet state (debug)")

st.dataframe(
    df_all[
        [
            "taxi_id",
            "speed",
            "battery",
            "is_overspeed",
            "is_low_battery",
            "display_status",
            "lat",
            "lon",
            "last_update",
        ]
    ],
    use_container_width=True,
)

# --------------------------------------------------
# REAL FLEET STATUS (DYNAMIC)
# --------------------------------------------------
st.subheader("Fleet status (real-time)")

col1, col2, col3 = st.columns(3)

nb_ok = (df_all["display_status"] == "OK").sum()
nb_overspeed = df_all["is_overspeed"].sum()
nb_low_battery = df_all["is_low_battery"].sum()

col1.metric("🟢 OK", int(nb_ok))
col2.metric("🔴 Overspeed", int(nb_overspeed))
col3.metric("!  Low battery", int(nb_low_battery))

# --------------------------------------------------
# LEGEND (STATIC)
# --------------------------------------------------
st.subheader("Legend")

legend_col1, legend_col2, legend_col3 = st.columns(3)
legend_col1.markdown("🟢 **OK**  \nNormal operation")
legend_col2.markdown("🔴 **OVERSPEED**  \nSpeed above threshold")
legend_col3.markdown(
    f"!  **LOW BATTERY**  \nBattery below {LOW_BATTERY_LIMIT}% (symbol on map)"
)

# --------------------------------------------------
# MAP DATA (ONLY VALID GPS)
# --------------------------------------------------
df = df_all.dropna(subset=["lat", "lon"]).copy()
if df.empty:
    st.warning("No valid GPS points found yet.")
    st.stop()

# Base color depends ONLY on overspeed
df["base_status"] = df["is_overspeed"].map(lambda x: "OVERSPEED" if x else "OK")

COLOR_MAP = {"OK": "green", "OVERSPEED": "red"}

# --------------------------------------------------
# MAP (NO PLOTLY LEGEND)
# --------------------------------------------------
fig = px.scatter_mapbox(
    df,
    lat="lat",
    lon="lon",
    hover_name="taxi_id",
    hover_data=["speed", "battery", "display_status", "last_update"],
    color="base_status",
    color_discrete_map=COLOR_MAP,
    zoom=12,
    center={"lat": 48.8566, "lon": 2.3522},
)

fig.update_traces(marker=dict(size=20, opacity=0.9))

# LOW BATTERY overlay "!" (independent from overspeed)
low_battery_df = df[df["is_low_battery"]]
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
