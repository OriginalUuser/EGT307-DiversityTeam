import pandas as pd
from db import get_engine


def load_pond_data(
    table_name: str,
    window_size: int,
    forecast_horizon: int
) -> pd.DataFrame:
    """
    Load the most recent pond data from Postgres.

    Parameters
    ----------
    table_name : str
        Name of the Postgres table (e.g. "iot_pond_1")

    window_size : int
        Number of rows used for sliding window display

    forecast_horizon : int
        Number of fabricated future rows needed

    Returns
    -------
    pd.DataFrame
        Data sorted ascending by time
    """

    rows_needed = window_size + forecast_horizon

    engine = get_engine()

    query = f"""
        SELECT *
        FROM {table_name}
        ORDER BY created_at DESC
        LIMIT 110
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return df

    # Ensure timestamp column is datetime
    df["created_at"] = pd.to_datetime(df["created_at"])

    # Sort ascending for time-series plotting
    df = df.sort_values("created_at").reset_index(drop=True)

    return df







# import pandas as pd
# from pathlib import Path




# def load_pond_data(csv_path: str) -> pd.DataFrame:
#     """
#     Loads and cleans pond CSV data.
#     """
#     if not Path(csv_path).exists():
#         raise FileNotFoundError(f"CSV not found: {csv_path}")

#     df = pd.read_csv(csv_path)

#     df.columns = df.columns.str.lower().str.replace(" ", "").str.replace("(", "").str.replace(")", "")

#     # Parse datetime
#     df["created_at"] = pd.to_datetime(
#         df["created_at"],
#         errors="coerce",  # invalid formats become NaT instead of crashing
#         dayfirst=True      # if your dates are in DD/MM/YYYY format
#     )

#     df = df.dropna(subset=["created_at"])


# # Convert sensor columns to numeric
#     sensor_cols = [
#         "temperaturec",
#         "ph",
#         "dissolvedoxygeng/ml",
#         "turbidityntu",
#         "ammoniag/ml",
#         "nitrateg/ml"
# ]

#     for col in sensor_cols:
#         if col in df.columns:
#             df[col] = pd.to_numeric(df[col], errors="coerce")

#     # Drop rows where all sensors are NaN
#     df = df.dropna(subset=sensor_cols, how="all")

#     # Sort chronologically
#     df = df.sort_values("created_at")

#     return df
