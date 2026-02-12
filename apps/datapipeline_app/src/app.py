"""
Fast API for Data Ingestion
---------------------------

POST:
    - Accept payload from pond sensors (mock device)
    - Check payload content
    - Send payload to database
"""

from typing import Any
from pydantic import BaseModel
from fastapi import FastAPI, status
import psycopg2
import os

from .data_ingest import checkPayloadSchema

# Connect to database
POSTGRES_PASS = os.getenv('POSTGRES_PASS')
conn = psycopg2.connect(
    user="admin",
    password=POSTGRES_PASS,
    host="127.0.0.1",
    port="5432",
    database="sensor-db"
)
conn.autocommit = True
cursor = conn.cursor()

# Setup app
app = FastAPI()

# Define payload
class Evaluate(BaseModel):
    table_name:     str
    data:           dict[str, Any]

# cursor.execute("DROP TABLE IF EXISTS temp CASCADE;")
# cursor.execute(
#     '''
#         CREATE TABLE temp (
#             col1 SERIAL PRIMARY KEY,
#             col2 INT,
#             col3 VARCHAR(3)
#         ); 
#     '''
# )
# cursor.execute("INSERT INTO temp (col2, col3) VALUES (0, 'hi');")
# cursor.execute("INSERT INTO temp (col3, col2) VALUES ('bye', 100);")
# cursor.execute("SELECT * FROM temp;")

# cursor.execute(
#     """
#         SELECT 
#             column_name, 
#             data_type
#         FROM 
#             information_schema.columns
#         WHERE 
#             table_schema = 'public' AND table_name = 'temp'
#         ORDER BY 
#             ordinal_position;
#     """
# )


# print(cursor.fetchall())

# Accept payload
@app.post("/", status_code=status.HTTP_202_ACCEPTED)
def post_root(payload: Evaluate):
    # Ideally read schema + imputation values and pass into function

    # Check payload content
    formattedPayload, additionalColumns, expectedSchema, clearToSend = checkPayloadSchema(payload.data)
    if clearToSend: 
        # Send data to corresponding table in database
        cursor.execute(f"INSERT INTO {payload.table_name} {set(formattedPayload.keys())} VALUES {set(formattedPayload.values())};")
        
        # Update schema + imputation values

