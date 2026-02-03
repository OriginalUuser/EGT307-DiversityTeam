# import streamlit as st
# from pathlib import Path
# from retrieve import load_pond_data
# from streamlit_autorefresh import st_autorefresh
# import datetime
# import pandas as pd
# import altair as alt

# # -------------------------------
# # Page config
# # -------------------------------
# st.set_page_config(
#     page_title="Aquaponics Monitoring Dashboard",
#     layout="wide"
# )

# # -------------------------------
# # Pond configuration
# # -------------------------------
# POND_FILES = {
#     "Pond 1": r"archive\IoTpond1.csv",
#     "Pond 2": r"archive\IoTpond2.csv",
#     "Pond 3": r"archive\IoTpond3.csv",
#     "Pond 4": r"archive\IoTpond4.csv",
# }

# # -------------------------------
# # Sensor configuration
# # -------------------------------
# SENSORS = {
#     "Temperature (°C)": "temperaturec",
#     "pH": "ph",
#     "Dissolved Oxygen (g/ml)": "dissolvedoxygeng/ml",
#     "Turbidity (NTU)": "turbidityntu",
#     "Ammonia (g/ml)": "ammoniag/ml",
#     "Nitrate (g/ml)": "nitrateg/ml"
# }

# WINDOW_SIZE = 100
# FORECAST_HORIZON = 10
# TREND_EPSILON = 0.01

# # -------------------------------
# # Sidebar controls
# # -------------------------------
# st.sidebar.header("⚙️ Controls")

# pages = ["Main Page"] + list(POND_FILES.keys())
# selected_page = st.sidebar.selectbox("Select Page", pages)

# refresh_rate = st.sidebar.slider(
#     "Dashboard Refresh Rate (seconds)",
#     min_value=5,
#     max_value=60,
#     value=10,
#     step=5
# )

# refresh_ms = refresh_rate * 1000

# # -------------------------------
# # Cached data retrieval
# # -------------------------------
# @st.cache_data
# def get_data(csv_path):
#     return load_pond_data(csv_path)

# # -------------------------------
# # Sliding window helper
# # -------------------------------
# def get_sliding_window(df, state_key):
#     if state_key not in st.session_state:
#         st.session_state[state_key] = 0

#     max_start = len(df) - (WINDOW_SIZE + FORECAST_HORIZON)
#     start = min(st.session_state[state_key], max_start)

#     window_df = df.iloc[start : start + WINDOW_SIZE]
#     forecast_df = df.iloc[start + WINDOW_SIZE : start + WINDOW_SIZE + FORECAST_HORIZON]

#     st.session_state[state_key] += 1
#     if st.session_state[state_key] > max_start:
#         st.session_state[state_key] = 0

#     return window_df, forecast_df

# # =====================================================
# # MAIN PAGE — LATEST VALUES + TREND ARROWS
# # =====================================================
# if selected_page == "Main Page":
#     st.title("🌊 Aquaponics System Overview")

#     st_autorefresh(interval=refresh_ms, limit=None, key="main_page_refresh")

#     st.caption(
#         f"🕒 Last refreshed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
#     )

#     st.markdown("### 📊 Latest Sensor Values & Trends")

#     for pond_name, csv_path in POND_FILES.items():
#         st.markdown(f"## 🌱 {pond_name}")

#         if not Path(csv_path).exists():
#             st.error(f"CSV not found: {csv_path}")
#             continue

#         df = get_data(csv_path).sort_values("created_at").reset_index(drop=True)

#         if len(df) < WINDOW_SIZE + FORECAST_HORIZON:
#             st.warning("Not enough data.")
#             continue

#         window_df, forecast_df = get_sliding_window(
#             df,
#             state_key=f"main_{pond_name}_idx"
#         )

#         latest = window_df.iloc[-1]
#         forecast_last = forecast_df.iloc[-1]

#         cols = st.columns(len(SENSORS))

#         for i, (label, col) in enumerate(SENSORS.items()):
#             current_val = latest[col]
#             future_val = forecast_last[col]
#             delta = future_val - current_val

#             if delta > TREND_EPSILON:
#                 arrow = "🔺"
#                 color = "green"
#             elif delta < -TREND_EPSILON:
#                 arrow = "🔻"
#                 color = "red"
#             else:
#                 arrow = "➖"
#                 color = "gray"

#             with cols[i]:
#                 st.markdown(
#                     f"""
#                     <div style="text-align:center;">
#                         <div style="font-size:14px; font-weight:600;">{label}</div>
#                         <div style="font-size:22px;">
#                             {current_val:.2f}
#                             <span style="color:{color};">{arrow}</span>
#                         </div>
#                     </div>
#                     """,
#                     unsafe_allow_html=True
#                 )

#         st.markdown("---")

# # =====================================================
# # POND DASHBOARD PAGES
# # =====================================================
# else:
#     st.title(f"🌱 {selected_page} Monitoring Dashboard")

#     csv_path = POND_FILES[selected_page]
#     if not Path(csv_path).exists():
#         st.error(f"CSV not found: {csv_path}")
#         st.stop()

#     df = get_data(csv_path).sort_values("created_at").reset_index(drop=True)

#     st_autorefresh(interval=refresh_ms, limit=None, key=f"{selected_page}_refresh")

#     window_df, forecast_df = get_sliding_window(
#         df,
#         state_key=f"{selected_page}_idx"
#     )

#     latest = window_df.iloc[-1]

#     st.subheader("📊 Latest Readings")
#     st.caption(
#         f"🕒 Last refreshed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
#     )

#     cols = st.columns(3)
#     for i, (label, col) in enumerate(SENSORS.items()):
#         cols[i % 3].metric(label, f"{latest[col]:.2f}")

#     st.subheader("📈 Sensor Forecasts (Next 10 Values)")

#     for label, col in SENSORS.items():
#         st.markdown(f"### {label}")

#         hist_df = window_df[["created_at", col]]
#         future_df = forecast_df[["created_at", col]]

#         hist_line = alt.Chart(hist_df).mark_line(
#             strokeWidth=2
#         ).encode(
#             x="created_at:T",
#             y=f"{col}:Q"
#         )

#         hist_points = alt.Chart(hist_df).mark_point(
#             opacity=0,
#             size=80
#         ).encode(
#             x="created_at:T",
#             y=f"{col}:Q",
#             tooltip=[
#                 alt.Tooltip("created_at:T", title="Time"),
#                 alt.Tooltip(f"{col}:Q", title="Actual Value")
#             ]
#         )

#         forecast_line = alt.Chart(future_df).mark_line(
#             strokeDash=[6, 6],
#             strokeWidth=2,
#             color="#FF9800"
#         ).encode(
#             x="created_at:T",
#             y=f"{col}:Q"
#         )

#         forecast_points = alt.Chart(future_df).mark_point(
#             size=110,
#             filled=True,
#             color="#FF9800"
#         ).encode(
#             x="created_at:T",
#             y=f"{col}:Q",
#             tooltip=[
#                 alt.Tooltip("created_at:T", title="Predicted Time"),
#                 alt.Tooltip(f"{col}:Q", title="Predicted Value")
#             ]
#         )

#         chart = (
#             hist_line +
#             hist_points +
#             forecast_line +
#             forecast_points
#         ).properties(height=320)

#         st.altair_chart(chart, use_container_width=True)


import streamlit as st
from pathlib import Path
from retrieve import load_pond_data
from streamlit_autorefresh import st_autorefresh
import datetime
import pandas as pd
import altair as alt

# -------------------------------
# Page config
# -------------------------------
st.set_page_config(
    page_title="Aquaponics Monitoring Dashboard",
    layout="wide"
)

# -------------------------------
# Pond configuration
# -------------------------------
POND_FILES = {
    "Pond 1": r"archive\IoTpond1.csv",
    "Pond 2": r"archive\IoTpond2.csv",
    "Pond 3": r"archive\IoTpond3.csv",
    "Pond 4": r"archive\IoTpond4.csv",
}

# -------------------------------
# Sensor configuration
# -------------------------------
SENSORS = {
    "Temperature (°C)": "temperaturec",
    "pH": "ph",
    "Dissolved Oxygen (g/ml)": "dissolvedoxygeng/ml",
    "Turbidity (NTU)": "turbidityntu",
    "Ammonia (g/ml)": "ammoniag/ml",
    "Nitrate (g/ml)": "nitrateg/ml"
}

WINDOW_SIZE = 100
FORECAST_HORIZON = 10
TREND_EPSILON = 0.01

# -------------------------------
# Sidebar controls
# -------------------------------
st.sidebar.header("⚙️ Controls")

pages = ["Main Page", "Aggregate Overview"] + list(POND_FILES.keys())
selected_page = st.sidebar.selectbox("Select Page", pages)

refresh_rate = st.sidebar.slider(
    "Dashboard Refresh Rate (seconds)",
    min_value=5,
    max_value=60,
    value=10,
    step=5
)

refresh_ms = refresh_rate * 1000

# -------------------------------
# 🔁 GLOBAL AUTO REFRESH (FIX)
# -------------------------------
refresh_counter = st_autorefresh(
    interval=refresh_ms,
    limit=None,
    key="global_refresh"
)

st.caption(
    f"🕒 Last refreshed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# -------------------------------
# Cached data retrieval (FIXED)
# -------------------------------
@st.cache_data
def get_data(csv_path, refresh_counter):  # 🔁 refresh fix
    return load_pond_data(csv_path)

# -------------------------------
# Sliding window helper
# -------------------------------
def get_sliding_window(df, state_key):
    if state_key not in st.session_state:
        st.session_state[state_key] = 0

    max_start = len(df) - (WINDOW_SIZE + FORECAST_HORIZON)
    start = min(st.session_state[state_key], max_start)

    window_df = df.iloc[start : start + WINDOW_SIZE]
    forecast_df = df.iloc[start + WINDOW_SIZE : start + WINDOW_SIZE + FORECAST_HORIZON]

    st.session_state[state_key] += 1
    if st.session_state[state_key] > max_start:
        st.session_state[state_key] = 0

    return window_df, forecast_df

# =====================================================
# MAIN PAGE — LATEST VALUES + TRENDS
# =====================================================
if selected_page == "Main Page":
    st.title("🌊 Aquaponics System Overview")

    for pond_name, csv_path in POND_FILES.items():
        st.markdown(f"## 🌱 {pond_name}")

        df = get_data(csv_path, refresh_counter).sort_values("created_at").reset_index(drop=True)
        window_df, forecast_df = get_sliding_window(df, f"main_{pond_name}_idx")

        latest = window_df.iloc[-1]
        future = forecast_df.iloc[-1]

        cols = st.columns(len(SENSORS))

        for i, (label, col) in enumerate(SENSORS.items()):
            delta = future[col] - latest[col]

            if delta > TREND_EPSILON:
                arrow, color = "🔺", "green"
            elif delta < -TREND_EPSILON:
                arrow, color = "🔻", "red"
            else:
                arrow, color = "➖", "gray"

            with cols[i]:
                st.markdown(
                    f"""
                    <div style="text-align:center;">
                        <div style="font-size:14px; font-weight:600;">{label}</div>
                        <div style="font-size:22px;">
                            {latest[col]:.2f}
                            <span style="color:{color};">{arrow}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("---")

# =====================================================
# AGGREGATE OVERVIEW PAGE
# =====================================================
elif selected_page == "Aggregate Overview":
    st.title("📊 Aggregate Sensor Overview (All Ponds)")

    pond_dfs = []
    for name, path in POND_FILES.items():
        df = get_data(path, refresh_counter).sort_values("created_at").reset_index(drop=True)
        pond_dfs.append(df)

    base_df, _ = get_sliding_window(pond_dfs[0], "aggregate_idx")
    time_index = base_df["created_at"]

    for label, col in SENSORS.items():
        st.markdown(f"### {label}")

        aligned = []
        for df in pond_dfs:
            aligned.append(df.loc[base_df.index, col].values)

        agg_df = pd.DataFrame(aligned).T
        stats_df = pd.DataFrame({
            "created_at": time_index,
            "min": agg_df.min(axis=1),
            "median": agg_df.median(axis=1),
            "max": agg_df.max(axis=1),
        })

        area = alt.Chart(stats_df).mark_area(
            opacity=0.25,
            color="#90CAF9"
        ).encode(
            x="created_at:T",
            y="min:Q",
            y2="max:Q"
        )

        median_line = alt.Chart(stats_df).mark_line(
            strokeWidth=3,
            color="#1E88E5"
        ).encode(
            x="created_at:T",
            y="median:Q",
            tooltip=[
                alt.Tooltip("created_at:T", title="Time"),
                alt.Tooltip("median:Q", title="Median"),
                alt.Tooltip("min:Q", title="Min"),
                alt.Tooltip("max:Q", title="Max"),
            ]
        )

        st.altair_chart((area + median_line).properties(height=320), use_container_width=True)

# =====================================================
# INDIVIDUAL POND PAGES
# =====================================================
else:
    st.title(f"🌱 {selected_page} Monitoring Dashboard")

    df = get_data(POND_FILES[selected_page], refresh_counter)\
            .sort_values("created_at").reset_index(drop=True)

    window_df, forecast_df = get_sliding_window(df, f"{selected_page}_idx")
    latest = window_df.iloc[-1]

    st.subheader("📊 Latest Readings")
    cols = st.columns(3)
    for i, (label, col) in enumerate(SENSORS.items()):
        cols[i % 3].metric(label, f"{latest[col]:.2f}")

    st.subheader("📈 Sensor Forecasts")

    for label, col in SENSORS.items():
        hist_df = window_df[["created_at", col]]
        fut_df = forecast_df[["created_at", col]]

        chart = (
            alt.Chart(hist_df).mark_line().encode(
                x="created_at:T",
                y=f"{col}:Q"
            )
            + alt.Chart(hist_df).mark_point(opacity=0).encode(
                x="created_at:T",
                y=f"{col}:Q",
                tooltip=[alt.Tooltip("created_at:T"), alt.Tooltip(f"{col}:Q")]
            )
            + alt.Chart(fut_df).mark_line(strokeDash=[6, 6], color="#FF9800").encode(
                x="created_at:T",
                y=f"{col}:Q"
            )
            + alt.Chart(fut_df).mark_point(color="#FF9800").encode(
                x="created_at:T",
                y=f"{col}:Q",
                tooltip=[alt.Tooltip("created_at:T"), alt.Tooltip(f"{col}:Q")]
            )
        ).properties(height=320)

        st.altair_chart(chart, use_container_width=True)
