import psycopg2
import os
from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import Any
import pandas as pd

# Connect to database
POSTGRES_PASS = os.getenv('POSTGRES_PASS')
conn = psycopg2.connect(
    user="admin",
    password=POSTGRES_PASS,
    # host="sensor-db-ha-rw.database-ns",
    host="127.0.0.1",
    port="5432",
    database="sensor-db"
)
conn.autocommit = True
cursor = conn.cursor()
# create_table = f'''
#         CREATE TABLE iot_pond_1 (
#             created_at TIMESTAMPTZ,
#             entry_id SERIAL PRIMARY KEY,
#             temperature FLOAT,
#             turbidity FLOAT,
#             dissolved_oxygen FLOAT,
#             ph FLOAT,
#             ammonia FLOAT,
#             nitrate FLOAT,
#             population INT,
#             fish_length FLOAT,
#             fish_weight FLOAT
#         ); 
#         '''
# cursor.execute(create_table)
cursor.execute("SELECT * FROM iot_pond_1 ORDER BY created_at DESC LIMIT 5;")
# cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast');")
print(cursor.fetchall())
# hi = {"a":'0', "b":1}
# print(str(tuple(hi.keys())).replace("'", ""))
# print(str(tuple(hi.values())))
# data = pd.Timestamp("2026-1-1")
# time = pd.to_datetime(data, format='%Y-%m-%d %H:%M:%S %Z', errors='coerce')
# print(time.tz_localize('CET'))

# correctedData = pd.Timestamp("2026-1-1")
# correctedData = pd.to_datetime(correctedData, format='%Y-%m-%d %H:%M:%S %Z', errors='coerce')

# # If error, treat as bad data
# if pd.isnull(correctedData):
#     correctedData = None
# else:
#     correctedData = str(correctedData.tz_localize('CET'))

# print(correctedData)

# app = FastAPI()

# class Evaluate(BaseModel):
#     table_name:     str
#     data:           int

# @app.post("/", status_code=status.HTTP_201_CREATED)
# async def create_item(item: Evaluate):
#     sqlQuery = f"INSERT INTO temp (col2, col3) VALUES ('{item.table_name}', {(item.data)});"
#     cursor.execute("DROP TABLE IF EXISTS temp CASCADE;")
#     cursor.execute(
#         '''
#             CREATE TABLE temp (
#                 col1 SERIAL PRIMARY KEY,
#                 col2 VARCHAR(255),
#                 col3 INT
#             ); 
#         '''
#     )
#     cursor.execute(sqlQuery)
#     cursor.execute("SELECT * FROM temp;")
#     return cursor.fetchall()

# @app.post("/", status_code=status.HTTP_202_ACCEPTED)
# def post():
#     return "success!"
   