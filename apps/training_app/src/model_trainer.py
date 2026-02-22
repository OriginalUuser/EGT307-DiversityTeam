# Description: Script for individual model training worker
# Formatted and linted with Ruff

import os
import json
import pandas as pd
import numpy as np
import tempfile
from typing import Optional

from sqlalchemy import create_engine, text
import procrastinate
from procrastinate.contrib.aiopg import AiopgConnector
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Input
from tensorflow.keras.callbacks import History
from sklearn.preprocessing import MinMaxScaler
import logging

# Define logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%d-%m-%y %H:%M:%S",
)
logger = logging.getLogger(__name__)

################
# Database URI #
################

# Database Credentials
SENSOR_DB_USER = os.environ.get("SENSOR_DB_USER")
SENSOR_DB_PASSWORD = os.environ.get("SENSOR_DB_PASSWORD")

ML_DB_USER = os.environ.get("ML_DB_USER")
ML_DB_PASSWORD = os.environ.get("ML_DB_PASSWORD")

# Database Connection Details
SENSOR_DB_HOST = os.environ.get("SENSOR_DB_HOST")
ML_DB_HOST = os.environ.get("ML_DB_HOST")

# Database port
DB_PORT = os.environ.get("DB_PORT")

# Database names
SENSOR_DB_NAME = os.environ.get("SENSOR_DB_NAME")
ML_DB_NAME = os.environ.get("ML_DB_NAME")

# Database URIs
SENSOR_DB_URI = f"postgresql://{SENSOR_DB_USER}:{SENSOR_DB_PASSWORD}@{SENSOR_DB_HOST}:{DB_PORT}/{SENSOR_DB_NAME}"
ML_DB_URI = (
    f"postgresql://{ML_DB_USER}:{ML_DB_PASSWORD}@{ML_DB_HOST}:{DB_PORT}/{ML_DB_NAME}"
)

sensor_engine = create_engine(SENSOR_DB_URI)
ml_artifact_engine = create_engine(ML_DB_URI)
app = procrastinate.App(connector=AiopgConnector(dsn=ML_DB_URI))  # Init procrastinate

####################
# Helper Functions #
####################


def _fetch_training_data(
    table_name: str, target_col: str, rows_limit: int
) -> pd.DataFrame:
    """
    Retrieves the most recent sensor data from the database.

    Args:
        table_name (str): Name of the SQL table to query.
        target_col (str): The specific column to use as the model target.
        rows_limit (int): Maximum number of recent rows to fetch.

    Returns:
        pd.DataFrame: A DataFrame sorted by 'created_at' in ascending order.
    """
    # Selects latest added rows based on time created and target column
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
    return pd.read_sql(query, sensor_engine)


def _preprocess_timeseries(
    df: pd.DataFrame, target_col: str, window_size: int
) -> Optional[tuple]:
    """
    Cleans, resamples, and transforms raw data into LSTM-ready windows.

    Args:
        df (pd.DataFrame): Raw input data containing 'created_at' and target columns.
        target_col (str): The column name to be scaled and trained.
        window_size (int): Number of previous time steps to use for each prediction.

    Returns:
        Optional[tuple]: (X, y, scaler, t_start, t_end) if data meets window_size
            requirements, otherwise None.
    """
    # Converts data in created_at column to datetime objects in case it isn't already
    df["created_at"] = pd.to_datetime(df["created_at"])
    df.set_index("created_at", inplace=True)

    # Resample data into hours through finding the mean and impute missing rows with data from row before it
    df = df[[target_col]].resample("1h").mean().ffill()

    # Dropna just in case it still exists, as LSTMs cannot accept Null values
    df.dropna(inplace=True)

    # Check of df is empty, or doesn't have enough rows to meet the window size used for model training
    if df.empty or len(df) <= window_size:
        return None

    # Time period of data (in hours) which is used to train the model
    t_start, t_end = df.index.min().isoformat(), df.index.max().isoformat()
    logger.info(f"Data loaded: {len(df)} rows found spanning {t_start} to {t_end}")

    # We need to scale data into a range between 0 and 1 as LSTMS are sensitve to scale of input data
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(df.values.reshape(-1, 1))

    X, y = [], []

    # Perform sliding window logic
    for i in range(window_size, len(scaled_data)):
        X.append(scaled_data[i - window_size : i, 0])
        y.append(scaled_data[i, 0])

    X, y = np.array(X), np.array(y)
    X = np.reshape(
        X, (X.shape[0], X.shape[1], 1)
    )  # Reshape to (Samples, Time Steps, Features)

    return X, y, scaler, t_start, t_end


def _build_and_train_lstm(
    X: np.ndarray,
    y: np.ndarray,
    num_layers: int,
    lstm_units: int,
    optimizer: str,
    loss_function: str,
    epochs: int,
    batch_size: int,
) -> tuple:
    """
    Constructs and trains a Sequential LSTM model.

    Args:
        X (np.ndarray): 3D input features of shape (samples, time_steps, 1).
        y (np.ndarray): Target values.
        num_layers (int): Number of LSTM layers to stack.
        lstm_units (int): Number of neurons in each LSTM layer.
        optimizer (str): Keras optimizer name (e.g., 'adam').
        loss_function (str): Keras loss function (e.g., 'mean_squared_error').
        epochs (int): Number of training iterations.
        batch_size (int): Size of training batches.

    Returns:
        tuple: (model, history) where history contains training loss metrics.
    """
    # Define model object
    model = Sequential()

    # Define the input layer
    model.add(Input(shape=(X.shape[1], 1)))

    # Build the dense layers iteratively
    for i in range(num_layers):
        return_seq = i < num_layers - 1
        model.add(LSTM(units=lstm_units, return_sequences=return_seq))

    # Output layer; Has one neuron for numerical prediction
    model.add(Dense(1))

    # Complile model with optimizer and loss function
    model.compile(optimizer=optimizer, loss=loss_function)
    logger.info(
        f"Training LSTM: {num_layers} layers x {lstm_units} units | Epochs: {epochs}"
    )
    history = model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=0)
    return model, history


def _save_ml_artifacts(
    batch_id: str,
    table_name: str,
    target_col: str,
    rows_limit: int,
    t_start: str,
    t_end: str,
    scaler: MinMaxScaler,
    model: Sequential,
    history: History,
) -> None:
    """
    Persists training metadata, metrics, and the model binary to the database.

    Calculates final metrics, extracts scaler parameters, and saves the
    model as a binary object (BLOB) using a temporary file.

    Args:
        batch_id (str): Unique identifier for the training batch.
        table_name (str): The source SQL table name.
        target_col (str): The target column name.
        rows_limit (int): The row limit used for the query.
        t_start (str): ISO format start timestamp of the training data.
        t_end (str): ISO format end timestamp of the training data.
        scaler (MinMaxScaler): The fitted scaler used for data normalization.
        model (Sequential): The trained Keras model.
        history (History): The Keras history object containing loss logs.
    """

    # Gets the loss from the last epoch of training the model
    final_loss = history.history["loss"][-1]

    # Store the MSE and RMSE of the model
    metrics = {"mse": float(final_loss), "rmse": float(np.sqrt(final_loss))}

    # Stored to be used later in the inference pipeline to convert LSTM predictions back to real values (Unscale prediction)
    weights = {
        "scaler_min": float(scaler.min_[0]),
        "scaler_scale": float(scaler.scale_[0]),
    }

    # Store model weights as temporary .keras files,
    # before uploading to the PostgreSQL database as BLOB and deleted
    with tempfile.NamedTemporaryFile(suffix=".keras", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        model.save(tmp_path)
        with open(tmp_path, "rb") as f:
            model_bytes = f.read()
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    # Store all the relevant data into PostgreSQL
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
                "obj": model_bytes,
            },
        )
        conn.commit()


#######################
# Procastinate worker #
#######################


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
    optimizer: str = "adam",
    loss_function: str = "mean_squared_error",
    batch_size: int = 32,
):
    """
    LSTM model training pipeline. It is a Procrastinate worker that takes jobs from the task queue and starts model training.

    Args:
        batch_id (str): UUID representing the current execution batch.
        table_name (str): The SQL table containing the sensor data.
        target_col (str): The specific column to forecast.
        rows_limit (int, optional): Max recent rows to fetch. Defaults to 5000.
        window_size (int, optional): Number of past lags for input. Defaults to 10.
        lstm_units (int, optional): Neurons per LSTM layer. Defaults to 50.
        num_layers (int, optional): Count of stacked LSTM layers. Defaults to 2.
        epochs (int, optional): Training iterations. Defaults to 10.
        optimizer (str, optional): Keras optimizer name. Defaults to "adam".
        loss_function (str, optional): Keras loss function. Defaults to "mean_squared_error".
        batch_size (int, optional): Samples per gradient update. Defaults to 32.

    Returns:
        None: Artifacts are saved directly to the database.

    Raises:
        Exception: Re-raises any exceptions encountered during training to allow the task queue to handle retries.
    """
    logger.info(
        f"Starting training job <Batch: {batch_id} | Table: {table_name} | Target: {target_col}>"
    )
    try:
        df = _fetch_training_data(table_name, target_col, rows_limit)

        if df.empty:
            logger.warning(f"No data found for {table_name}. Skipping training.")
            return

        # Cleans, resamples, and transforms raw data into LSTM-ready windows.
        result = _preprocess_timeseries(df, target_col, window_size)

        # Have to do this to log if function returns a None data type
        if result is None:
            logger.warning(
                f"Insufficient data to proceed with training for {table_name}."
            )
            return

        # If data returned is not None, can upack the tuple into individual variables
        X, y, scaler, t_start, t_end = result

        # Build and train a Sequential LSTM
        model, history = _build_and_train_lstm(
            X, y, num_layers, lstm_units, optimizer, loss_function, epochs, batch_size
        )

        # Save all model artifacts into PostgreSQL
        _save_ml_artifacts(
            batch_id,
            table_name,
            target_col,
            rows_limit,
            t_start,
            t_end,
            scaler,
            model,
            history,
        )

        logger.info(f"Task completed and history saved | Batch: {batch_id}")
    except Exception as e:
        logger.exception(f"Task failed | Batch: {batch_id} | Error: {str(e)}")
        raise
