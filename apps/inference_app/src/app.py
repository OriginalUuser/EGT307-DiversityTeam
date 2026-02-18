"""
Fast API for Model Inference
---------------------------

GET:
    - Read latest data from database
    - Load trained model
    - Make inference
    - Return inference
"""

from pydantic import BaseModel
from fastapi import FastAPI, status
import psycopg2
import os

from .inference import makeInference

# Connect to database
DB_POSTGRES_PASS = os.getenv("DB_POSTGRES_PASS")
DB_DATABASE_DNS = os.getenv("DB_DATABASE_DNS")
ML_POSTGRES_PASS = os.getenv("ML_POSTGRES_PASS")
ML_DATABASE_DNS = os.getenv("ML_DATABASE_DNS")
DATABASE_PORT = os.getenv("DATABASE_PORT")

# Sensor Database
DB_NAME     = "sensor-db"
DB_USER        = "admin"

conn_db = psycopg2.connect(
    user=DB_USER,
    password=DB_POSTGRES_PASS,
    host=DB_DATABASE_DNS,
    port=DATABASE_PORT,
    database=DB_NAME
)
conn_db.autocommit = True
cursor_db = conn_db.cursor()

# Model Database
ML_NAME     = "ml-artifacts"
ML_USER        = "ml_admin"

conn_ml = psycopg2.connect(
    user=ML_USER,
    password=ML_POSTGRES_PASS,
    host=ML_DATABASE_DNS,
    port=DATABASE_PORT,
    database=ML_NAME
)
conn_ml.autocommit = True
cursor_ml = conn_ml.cursor()

# Setup app
app = FastAPI()

# Define payload
class Evaluate(BaseModel):
    table_name:     str

# Accept payload
@app.post("/", status_code=status.HTTP_201_CREATED)
def post_root(payload: Evaluate):
    # Read latest database data
    cursor_db.execute(f"SELECT * FROM {payload.table_name} ORDER BY created_at DESC LIMIT 10;")
    raw_data = cursor_db.fetchall()

    # Load trained model
    # Name of table containing model
    table_name = "training_history"
    query = f"SELECT model_object, model_weights FROM {table_name} LIMIT 1;"
    cursor_ml.execute(query)
    row = cursor_ml.fetchone()
    print(row)
    model_binary = row[0]
    weights = row[1] 

    # Make inference
    inferences = makeInference(raw_data, weights, model_binary)

    # Return inference
    return inferences
