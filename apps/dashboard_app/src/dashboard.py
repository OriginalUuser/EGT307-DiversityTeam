import streamlit as st
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
    "Pond 1": "iot_pond_1",
    "Pond 2": "iot_pond_2",
    "Pond 3": "iot_pond_3",
    "Pond 4": "iot_pond_4",    
}

# -------------------------------
# Sensor configuration
# -------------------------------
SENSORS = {
    "Temperature (°C)": "temperature",
    "pH": "ph",
    "Dissolved Oxygen (g/ml)": "dissolved_oxygen",
    "Turbidity (NTU)": "turbidity",
    "Ammonia (g/ml)": "ammonia",
    "Nitrate (g/ml)": "nitrate",
    "Fish Popluation": "population",
    "Length of Fish": "fish_length",
    "Weight of Fish": "fish_weight"
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
# 🔁 GLOBAL AUTO REFRESH
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
# Cached data retrieval
# -------------------------------
@st.cache_data
def get_data(table_name, refresh_counter):
    return load_pond_data(
        table_name=table_name,
        window_size=WINDOW_SIZE,
        forecast_horizon=FORECAST_HORIZON
    )

# -------------------------------
# Production window logic
# -------------------------------
def get_window_data(df, state_key=None):
    """
    Returns (window_df, forecast_df)
    Production mode:
    - First 100 rows = actual data
    - Next 10 rows = forecast
    """
    if len(df) < WINDOW_SIZE + FORECAST_HORIZON:
        return df.iloc[:WINDOW_SIZE], df.iloc[WINDOW_SIZE:]

    window_df = df.iloc[:WINDOW_SIZE]
    forecast_df = df.iloc[WINDOW_SIZE:WINDOW_SIZE + FORECAST_HORIZON]

    return window_df, forecast_df

# =====================================================
# MAIN PAGE — LATEST VALUES + TRENDS
# =====================================================
if selected_page == "Main Page":
    st.title("🌊 Aquaponics System Overview")

    for pond_name, table_name in POND_FILES.items():
        st.markdown(f"## 🌱 {pond_name}")

        df = get_data(table_name, refresh_counter).sort_values("created_at").reset_index(drop=True)
        window_df, forecast_df = get_window_data(df)

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
    for name, table_name in POND_FILES.items():
        df = get_data(table_name, refresh_counter).sort_values("created_at").reset_index(drop=True)
        pond_dfs.append(df)

    base_df, _ = get_window_data(pond_dfs[0])
    time_index = base_df["created_at"]

    for label, col in SENSORS.items():
        aligned = []
        for df in pond_dfs:
            aligned.append(df.loc[base_df.index, col].values)

        agg_df = pd.DataFrame(aligned).T
        stats_df = pd.DataFrame({
            "date": time_index,
            "min": agg_df.min(axis=1),
            "median": agg_df.median(axis=1),
            "max": agg_df.max(axis=1),
        })

        area = alt.Chart(stats_df).mark_area(
            opacity=0.25,
            color="#90CAF9"
        ).encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("min:Q", title=label),
            y2="max:Q"
        )

        median_line = alt.Chart(stats_df).mark_line(
            strokeWidth=3,
            color="#1E88E5"
        ).encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("median:Q", title=label),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip("median:Q", title=f"Median {label}"),
                alt.Tooltip("min:Q", title=f"Min {label}"),
                alt.Tooltip("max:Q", title=f"Max {label}"),
            ]
        )

        st.altair_chart(
            (area + median_line).properties(
                height=320,
                title=f"{label} Graph"
            ),
            use_container_width=True
        )


# =====================================================
# INDIVIDUAL POND PAGES
# =====================================================
else:
    st.title(f"🌱 {selected_page} Monitoring Dashboard")

    df = get_data(POND_FILES[selected_page], refresh_counter)\
            .sort_values("created_at").reset_index(drop=True)

    window_df, forecast_df = get_window_data(df)
    latest = window_df.iloc[-1]

    st.subheader("📊 Latest Readings")
    cols = st.columns(3)
    for i, (label, col) in enumerate(SENSORS.items()):
        cols[i % 3].metric(label, f"{latest[col]:.2f}")


    st.subheader("📈 Sensor Forecasts")
    for label, col in SENSORS.items():
        hist_df = window_df[["created_at", col]].rename(columns={"created_at": "date"})
        fut_df = forecast_df[["created_at", col]].rename(columns={"created_at": "date"})

        chart = (
            alt.Chart(hist_df).mark_line().encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y(f"{col}:Q", title=label)
            )
            + alt.Chart(hist_df).mark_point(opacity=0).encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y(f"{col}:Q", title=label),
                tooltip=[alt.Tooltip("date:T", title="Date"),
                        alt.Tooltip(f"{col}:Q", title=label)]
            )
            + alt.Chart(fut_df).mark_line(strokeDash=[6, 6], color="#FF9800").encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y(f"{col}:Q", title=label)
            )
            + alt.Chart(fut_df).mark_point(color="#FF9800").encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y(f"{col}:Q", title=label),
                tooltip=[alt.Tooltip("date:T", title="Date"),
                        alt.Tooltip(f"{col}:Q", title=label)]
            )
        ).properties(
            height=320,
            title=f"{label} Graph"
        )

        st.altair_chart(chart, use_container_width=True)
