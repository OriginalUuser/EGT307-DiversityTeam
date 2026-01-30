import os
import re
import pandas as pd
import numpy as np

raw_data_path = os.path.join(os.getcwd(), "data", "kaggle_dataset_raw")
clean_data_path = os.path.join(os.getcwd(), "data", "kaggle_dataset_clean")

# Collect all csvs and standardize
# This only works for the Kaggle dataset
for file in os.listdir(raw_data_path):
    df = pd.read_csv(os.path.join(raw_data_path, file), low_memory=False)
    # Add the population column for IoTPond7.csv and IoTPond8.csv
    if file == "IoTPond7.csv":
        loc_index = df.columns.get_loc("nitrate(g/ml)") + 1
        df.insert(loc=loc_index, column="population", value=None)
    elif file == "IoTPond8.csv":
        loc_index = df.columns.get_loc("Total_length (cm)") - 1
        df.insert(loc=loc_index, column="population", value=None)
    elif file == "IoTPond9.csv":
        loc_index = df.columns.get_loc("Nitrate(g/ml)") + 1
        df.insert(loc=loc_index, column="population", value=None)

    # Remove extra columns
    df.columns = [col.lower() for col in df.columns]
    if "date" in df.columns:
        df.drop(inplace=True, columns="date")
    if df.shape[1] > 11:
        df.drop(inplace=True, columns=df.columns[11:])

    # Standardize columns
    new_col_names = ["created_at", "entry_id", "temperature", "turbidity", "dissolved_oxygen", "ph", "ammonia", "nitrate", "population", "fish_length", "fish_weight"]
    df.columns = new_col_names

    # Drop duplicates
    df = df.drop_duplicates()

    # Remove rows where entry_id is null
    df = df.dropna(subset=['entry_id'])

    # Standardize datatypes
    convert_dict = {
        "entry_id": "Int64",
        "temperature": np.float64,
        "turbidity": np.float64,
        "dissolved_oxygen": np.float64,
        "ph": np.float64,
        "ammonia": np.float64,
        "nitrate": np.float64,
        "population": "Int64",
        "fish_length": np.float64,
        "fish_weight": np.float64,
    }
    df = df.astype(convert_dict)

    if match := re.search(r'\d+', file): no = match.group(0)
    df.to_csv(os.path.join(clean_data_path, f"iot_pond_{no}.csv"), index=False)
    print(f"Standardized and saved to {os.path.join(clean_data_path, f"iot_pond_{no}.csv")}")