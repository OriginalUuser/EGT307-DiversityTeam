import streamlit as st
from retrieve import load_pond_data
from streamlit_autorefresh import st_autorefresh
import datetime
import pandas as pd
import altair as alt
import os
import json
import requests

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
pond_raw = os.getenv("POND","{}")
POND_FILES = json.loads(pond_raw)

sensors_raw = os.getenv("SENSORS","{}")
SENSORS = json.loads(sensors_raw)

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

data_amount_raw = os.getenv('DATA_AMOUNT')
DATA_AMOUNT = int(data_amount_raw)

@st.cache_data
def get_data(table_name, refresh_counter):
    return load_pond_data(
        table_name=table_name,
        data_amount= DATA_AMOUNT
    )

# -------------------------------
# Cached forecasted data retrieval
# -------------------------------

@st.cache_data(ttl=300)
def get_real_forecast(selected_page):
    path = "/app/data/all_ponds_forecast.json"
    if not os.path.exists(path):
        return pd.DataFrame()
    
    try:
        with open(path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df['created_at'] = pd.to_datetime(df['created_at'])
        # Filter by the pond name (the page name in your app)
        return df[df['pond_name'] == selected_page]
    except Exception as e:
        st.error(f"Error reading forecast file: {e}")
        return pd.DataFrame()
        

# =====================================================
# MAIN PAGE — LATEST VALUES + TRENDS
# =====================================================
if selected_page == "Main Page":
    st.title("🌊 Aquaponics System Overview")

    for pond_name, table_name in POND_FILES.items():
        st.markdown(f"## 🌱 {pond_name}")

        df = get_data(table_name, refresh_counter).sort_values("created_at").reset_index(drop=True)
        forecast_df = get_real_forecast(pond_name)

        if not df.empty:
            latest = df.iloc[-1]
            latest_time = latest["created_at"]
            
            # Logic to find the next valid forecast point
            next_prediction = None
            if not forecast_df.empty:
                future_points = forecast_df[forecast_df["created_at"] > latest_time]
                if not future_points.empty:
                    next_prediction = future_points.iloc[0]

            cols = st.columns(len(SENSORS))

            for i, (label, col) in enumerate(SENSORS.items()):
                # Default state
                arrow, color = "➖", "gray"

                if next_prediction is not None and col in next_prediction:
                    delta = next_prediction[col] - latest[col]

                    if delta > TREND_EPSILON:
                        arrow, color = "▲", "green"
                    elif delta < -TREND_EPSILON:
                        arrow, color = "▼", "red"
                    else:
                        arrow, color = "➖", "gray"

                with cols[i]:
                    # Using the original HTML/Markdown approach to prevent delta conflicts
                    st.markdown(
                        f"""
                        <div style="text-align:center;">
                            <div style="font-size:14px; font-weight:600; color:#555;">{label}</div>
                            <div style="font-size:22px;">
                                {latest[col]:.2f}
                                <span style="color:{color};">{arrow}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
        else:
            st.info(f"Waiting for data from {pond_name}...")

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

    time_index = pond_dfs[0]["created_at"]

    for label, col in SENSORS.items():
        aligned = []
        for df in pond_dfs:
            aligned.append(df.loc[df.index, col].values)

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

    current_table = POND_FILES[selected_page]

    # -------------------------------
    # 📡 Sidebar Report Trigger (Pond-Specific)
    # -------------------------------
    with st.sidebar.expander(f"🛠️ Run Analysis for {selected_page}", expanded=True):
        
        # User configures columns and range
        selected_sensor_labels = st.multiselect(
            "Select Columns",
            options=list(SENSORS.keys()),
            default=list(SENSORS.keys())[:1] # Defaults to first 
        )
        
        report_range = st.number_input(
            "Report Range (Rows)", 
            min_value=2000, max_value=100000, value=2000
        )

        if st.button("🚀 Trigger Monitoring Job"):
            if not selected_sensor_labels:
                st.warning("Please select at least one column.")
            else:
                db_column_names = [SENSORS[label] for label in selected_sensor_labels]
                # Prepare the payload
                payload = {
                    "table_name": current_table,
                    "columns": db_column_names,
                    "report_range": report_range
                }

                # API Details from Environment
                mon_dns = os.getenv("MONITORING_DNS")
                mon_port = os.getenv("MONITORING_PORT")
                url = f"http://{mon_dns}:{mon_port}"

                try:
                    with st.spinner("Dispatching Job..."):
                        response = requests.post(url, json=payload, timeout=5)
                    
                    if response.status_code == 200:
                        st.success(f"Job triggered for {current_table}!")
                    else:
                        st.error(f"Failed to trigger: {response.status_code}")
                except Exception as e:
                    st.error(f"Could not connect to Monitoring Service: {e}")



    df = get_data(POND_FILES[selected_page], refresh_counter)\
            .sort_values("created_at").reset_index(drop=True)

    forecast_df = get_real_forecast(selected_page)

    latest = df.iloc[-1]

    st.subheader("📊 Latest Readings")
    cols = st.columns(3)
    for i, (label, col) in enumerate(SENSORS.items()):
        cols[i % 3].metric(label, f"{latest[col]:.2f}")


    st.subheader("📈 Sensor Forecasts")
    for label, col in SENSORS.items():
        hist_df = df[["created_at", col]].rename(columns={"created_at": "date"})
        
        # Base historical chart
        chart = alt.Chart(hist_df).mark_line().encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y(f"{col}:Q", title=label)
        ) + alt.Chart(hist_df).mark_point(opacity=0).encode(
            x="date:T", y=f"{col}:Q", 
            tooltip=["date:T", f"{col}:Q"]
        )

        # Only add the forecast layers if data actually exists
        if not forecast_df.empty and col in forecast_df.columns:
            fut_df = forecast_df[["created_at", col]].rename(columns={"created_at": "date"})
            
            forecast_layers = alt.Chart(fut_df).mark_line(strokeDash=[6, 6], color="#FF9800").encode(
                x="date:T",
                y=f"{col}:Q"
            ) + alt.Chart(fut_df).mark_point(color="#FF9800").encode(
                x="date:T",
                y=f"{col}:Q",
                tooltip=["date:T", f"{col}:Q"]
            )
            chart += forecast_layers

        st.altair_chart(chart.properties(height=320, title=f"{label} Graph"), use_container_width=True)
