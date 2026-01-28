import os
import sqlite3
import pandas as pd

db_path = os.path.join(os.getcwd(), "database_vol")
csv_path = os.path.join(os.getcwd(), "database_vol", "kaggle_dataset")

with sqlite3.connect(os.path.join(db_path, "sensor_readings.db")) as conn:
    csv_files = [file for file in os.listdir(csv_path) if file[-4:] == ".csv"]
    
    for csv in csv_files:
        pd.read_csv(os.path.join(csv_path, csv)).to_sql(csv.split(".")[0], conn)