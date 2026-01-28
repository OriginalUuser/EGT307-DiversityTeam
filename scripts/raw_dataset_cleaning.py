import sqlite3
import pandas as pd

# Collect all sqlite db tables as pandas df for transformation
dfs = []
with sqlite3.connect("./database_vol/sensor_readings.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    # Get all sqlite db table names
    for table_name in cursor.fetchall():
        dfs.append(pd.read_sql_query(f"SELECT * FROM {table_name[0]}", conn))

    # Rename all columns and remove extra columns
    new_col_names = [name.lower().replace(" ", "_") for name in dfs[0].columns]
    for i, df in enumerate(dfs):
        if df.shape[1] > 11:
            dfs[i].drop(inplace=True, columns=df.columns[11:])
        dfs[i].columns = new_col_names

# Update sqlite db with changes made to pandas df
with sqlite3.connect("./database_vol/sensor_readings.db") as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    
    for df, table_name in zip(dfs, cursor.fetchall()):
        try:
            df.to_sql(table_name[0], conn, if_exists='replace', index=False)
            print(f"Table {table_name} cleaned successfully.")
        except ValueError as e:
            print(f"Error: {e}")