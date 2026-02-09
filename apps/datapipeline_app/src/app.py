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
from fastapi import FastApi, status
import psycopg2
import os

from .data_ingest import checkPayloadSchema

# Setup app
app = FastApi()

class Evaluate(BaseModel):
    table_name:     str
    data:           dict[str, Any]

@app.post("/", status_code=status.HTTP_202_ACCEPTED)
def post_root(payload: Evaluate):
    formattedPayload, additionalColumns, clearToSend = checkPayloadSchema(payload.data)
    if clearToSend: 
        #Darren code to send data to database, put it in data_ingest.py
    return