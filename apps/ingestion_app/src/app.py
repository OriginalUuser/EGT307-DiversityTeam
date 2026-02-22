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

from .data_ingest import tableExists, checkPayloadSchema

# Connect to database
POSTGRES_PASS   = os.getenv("POSTGRES_PASS")
DATABASE_DNS    = os.getenv("DATABASE_DNS")
DATABASE_PORT   = os.getenv("DATABASE_PORT")

DB_NAME         = os.getenv("DATABASE_NAME")
USER            = os.getenv("DATABASE_USER")

# Setup app
app = FastAPI()

# Define payload
class Evaluate(BaseModel):
    table_name:     str
    data:           dict[str, Any]

# Accept payload
@app.post("/", status_code=status.HTTP_201_CREATED)
def post_root(payload: Evaluate):
    # Ideally read schema + imputation values and pass into function

    with psycopg2.connect(user=USER, password=POSTGRES_PASS, host=DATABASE_DNS, port=DATABASE_PORT, database=DB_NAME) as conn:
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check table name
        if not tableExists(payload.table_name):
            print("table does not exist")
            return
        
        # Check payload content
        formattedPayload, additionalColumns, expectedSchema, clearToSend = checkPayloadSchema(payload.data)
        if clearToSend: 
            # Send data to corresponding table in database
            print("sending data to database")
            cursor.execute(f"INSERT INTO {payload.table_name} {str(tuple(formattedPayload.keys())).replace("'", "")} VALUES {str(tuple(formattedPayload.values()))};")
            
            # Update schema + imputation values
            return formattedPayload
    
    print("discarding bad data")