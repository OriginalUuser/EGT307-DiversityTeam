import pandas as pd
from pathlib import Path


def load_pond_data(csv_path: str) -> pd.DataFrame:
    """
    Loads and cleans pond CSV data.
    """
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)

    df.columns = df.columns.str.lower().str.replace(" ", "").str.replace("(", "").str.replace(")", "")

    # Parse datetime
    df["created_at"] = pd.to_datetime(
        df["created_at"],
        errors="coerce",  # invalid formats become NaT instead of crashing
        dayfirst=True      # if your dates are in DD/MM/YYYY format
    )

    df = df.dropna(subset=["created_at"])


# Convert sensor columns to numeric
    sensor_cols = [
        "temperaturec",
        "ph",
        "dissolvedoxygeng/ml",
        "turbidityntu",
        "ammoniag/ml",
        "nitrateg/ml"
]

    for col in sensor_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows where all sensors are NaN
    df = df.dropna(subset=sensor_cols, how="all")

    # Sort chronologically
    df = df.sort_values("created_at")

    return df
