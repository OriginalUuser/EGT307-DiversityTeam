import json
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
import tempfile
import os

def _scale(x, scaler_min, scaler_scale):
    return x * scaler_scale + scaler_min

def _inverse_scale(x_scaled, scaler_min, scaler_scale):
    return (x_scaled - scaler_min) / scaler_scale

def makeInference(
    sensor_conn,
    ml_conn,
    table_name: str,
    target_col: str,
    batch_id: str,
    window_size: int = 10,
    horizon: int = 24
):
    # Load latest model + scaler params
    with ml_conn.cursor() as cursor:
        cursor.execute("""
            SELECT model_object, model_weights, time_end
            FROM training_history
            WHERE batch_id = %s AND source_table = %s AND target_column = %s
            ORDER BY time_end DESC
            LIMIT 1
        """, (batch_id, table_name, target_col))
        row = cursor.fetchone()

    if not row:
        raise RuntimeError("No trained model found.")

    model_bytes, weights_json, time_end = row
    weights = json.loads(weights_json)
    scaler_min = float(weights["scaler_min"])
    scaler_scale = float(weights["scaler_scale"])

    # Load model from bytes
    with tempfile.NamedTemporaryFile(suffix=".keras", delete=False) as tmp:
        tmp.write(model_bytes)
        tmp_path = tmp.name
    try:
        model = load_model(tmp_path)
    finally:
        os.remove(tmp_path)

    # Get query past data within context window
    query = f"""
        WITH hourly AS (
            SELECT
                date_trunc('hour', created_at) AS hour_ts,
                avg({target_col}) AS avg_val
            FROM {table_name}
            GROUP BY 1
        ),
        bounds AS (
            SELECT min(hour_ts) AS min_ts, max(hour_ts) AS max_ts
            FROM hourly
        ),
        series AS (
            SELECT generate_series(min_ts, max_ts, interval '1 hour') AS hour_ts
            FROM bounds
        ),
        joined AS (
            SELECT s.hour_ts, h.avg_val
            FROM series s
            LEFT JOIN hourly h ON h.hour_ts = s.hour_ts
        ),
        filled AS (
            SELECT
                hour_ts,
                avg_val,
                sum(CASE WHEN avg_val IS NOT NULL THEN 1 ELSE 0 END)
                    OVER (ORDER BY hour_ts) AS grp
            FROM joined
        ),
        ffilled AS (
            SELECT
                hour_ts AS created_at,
                first_value(avg_val) OVER (PARTITION BY grp ORDER BY hour_ts) AS {target_col}
            FROM filled
            WHERE grp > 0
        )
        SELECT * FROM (
            SELECT created_at, {target_col}
            FROM ffilled
            ORDER BY created_at DESC
            LIMIT {window_size}
        ) AS sub
        ORDER BY created_at ASC;
    """

    df = pd.read_sql(query, sensor_conn)

    if df.empty:
        raise RuntimeError("No sensor data found.")

    df["created_at"] = pd.to_datetime(df["created_at"])
    df.set_index("created_at", inplace=True)

    last_ts = df.index.max()
    context = df[target_col].values[-window_size:]

    # Scale context
    context_scaled = _scale(context, scaler_min, scaler_scale)

    # Autoregressive forecast
    preds_scaled = []
    window = context_scaled.copy()

    for _ in range(horizon):
        x = window.reshape(1, window_size, 1)
        yhat_scaled = model.predict(x, verbose=0)[0, 0]
        preds_scaled.append(yhat_scaled)
        window = np.append(window[1:], yhat_scaled)

    preds = _inverse_scale(np.array(preds_scaled), scaler_min, scaler_scale)

    # Outut
    timestamps = pd.date_range(last_ts + pd.Timedelta(hours=1), periods=horizon, freq="1h")
    return pd.DataFrame({"created_at": timestamps, "prediction": preds})
