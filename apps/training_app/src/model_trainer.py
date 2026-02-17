import os
import json
import pandas as pd
import numpy as np
import tempfile

from sqlalchemy import create_engine, text
import procrastinate
from procrastinate.contrib.aiopg import AiopgConnector
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from sklearn.preprocessing import MinMaxScaler
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%d-%m-%y %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Database Credentials
SENSOR_DB_USER = os.environ.get('SENSOR_DB_USER')
SENSOR_DB_PASSWORD = os.environ.get('SENSOR_DB_PASSWORD')

ML_DB_USER = os.environ.get('ML_DB_USER')
ML_DB_PASSWORD = os.environ.get('ML_DB_PASSWORD')

# Database Connection Details
SENSOR_DB_HOST = os.environ.get('SENSOR_DB_HOST')
ML_DB_HOST = os.environ.get('ML_DB_HOST')

# Database port
DB_PORT = os.environ.get('DB_PORT')

# Database names
SENSOR_DB_NAME = os.environ.get('SENSOR_DB_NAME')
ML_DB_NAME = os.environ.get('ML_DB_NAME')

# Database URIs
SENSOR_DB_URI = f"postgresql://{SENSOR_DB_USER}:{SENSOR_DB_PASSWORD}@{SENSOR_DB_HOST}:{DB_PORT}/{SENSOR_DB_NAME}"
ML_DB_URI = f"postgresql://{ML_DB_USER}:{ML_DB_PASSWORD}@{ML_DB_HOST}:{DB_PORT}/{ML_DB_NAME}"

sensor_engine = create_engine(SENSOR_DB_URI)
ml_artifact_engine = create_engine(ML_DB_URI)
app = procrastinate.App(connector=AiopgConnector(dsn=ML_DB_URI)) 

@app.task(name="train_model_sql")
async def train_model_sql(
    batch_id: str, 
    table_name: str, 
    target_col: str, 
    rows_limit: int = 5000,
    window_size: int = 10,
    lstm_units: int = 50,
    num_layers: int = 2,
    epochs: int = 10,
    optimizer: str = 'adam',
    loss_function: str = 'mean_squared_error',
    batch_size: int = 32
):
    logger.info(f"Starting training job <Batch: {batch_id} | Table: {table_name} | Target: {target_col}>")
    try:
        query = f"""
            SELECT * FROM (
                SELECT created_at, {target_col}
                FROM {table_name}
                ORDER BY created_at DESC
                LIMIT {rows_limit}
            ) AS sub
            ORDER BY created_at ASC
        """

        logger.debug(f"Executing query on sensor database for table {table_name}")
        df = pd.read_sql(query, sensor_engine)

        if df.empty:
            logger.warning(f"No data found for {table_name}. Skipping training.")
            return

        df['created_at'] = pd.to_datetime(df['created_at'])
        df.set_index('created_at', inplace=True)

        df = df[[target_col]].resample('1h').mean().ffill()
        df.dropna(inplace=True)
        
        t_start = df.index.min().isoformat()
        t_end = df.index.max().isoformat()
        logger.info(f"Data loaded: {len(df)} rows found spanning {t_start} to {t_end}")

        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(df.values.reshape(-1, 1))

        if len(scaled_data) <= window_size:
            logger.warning(f"Not enough data points ({len(scaled_data)}) for window size {window_size}.")
            return

        X, y = [], []
        for i in range(window_size, len(scaled_data)):
            X.append(scaled_data[i-window_size:i, 0])
            y.append(scaled_data[i, 0])
        
        X, y = np.array(X), np.array(y)
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))

        model = Sequential()
        model.add(Input(shape=(X.shape[1], 1)))

        for i in range(num_layers):
            return_seq = (i < num_layers - 1)
            model.add(LSTM(units=lstm_units, return_sequences=return_seq))
        model.add(Dense(1))
        
        model.compile(optimizer=optimizer, loss=loss_function)
        
        logger.info(f"Training LSTM: {num_layers} layers x {lstm_units} units | Epochs: {epochs}")
        history = model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)
        
        final_loss = history.history['loss'][-1]
        metrics = {
            "mse": float(final_loss),
            "rmse": float(np.sqrt(final_loss))
        }
        
        weights = {
            "scaler_min": float(scaler.min_[0]),
            "scaler_scale": float(scaler.scale_[0])
        }

        with tempfile.NamedTemporaryFile(suffix='.keras', delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            model.save(tmp_path)
            with open(tmp_path, 'rb') as f:
                model_bytes = f.read()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        logger.info(f"Task completed successfully | Batch: {batch_id}")

        # Save Results
        logger.debug(f"Saving artifact to ml_artifacts database for batch {batch_id}")
        with ml_artifact_engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO training_history 
                    (batch_id, source_table, target_column, rows_limit, time_start, time_end, model_weights, metrics, model_object)
                    VALUES (:bid, :src, :tgt, :lim, :ts, :te, :w, :m, :obj)
                """),
                {
                    "bid": batch_id,
                    "src": table_name,
                    "tgt": target_col,
                    "lim": rows_limit,
                    "ts": t_start,
                    "te": t_end,
                    "w": json.dumps(weights),
                    "m": json.dumps(metrics),
                    "obj": model_bytes
                }
            )
            conn.commit()

        logger.info(f"Task completed and history saved | Batch: {batch_id}")
    except Exception as e:
        logger.exception(f"Task failed | Batch: {batch_id} | Error: {str(e)}")
        raise