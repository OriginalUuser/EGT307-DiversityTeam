"""
Fast API for Model Inference
---------------------------

POST:
    - Read latest data from database
    - Load trained model
    - Make inference
    - Return inference
"""

from pydantic import BaseModel
from fastapi import FastAPI, status
import os
import psycopg2

from inference import makeInference

# Connect to database
DB_POSTGRES_PASS = os.getenv("DB_POSTGRES_PASS")
DB_DATABASE_DNS = os.getenv("DB_DATABASE_DNS")

ML_POSTGRES_PASS = os.getenv("ML_POSTGRES_PASS")
ML_DATABASE_DNS = os.getenv("ML_DATABASE_DNS")

DATABASE_PORT = os.getenv("DATABASE_PORT")

# Sensor Database
DB_NAME = "sensor-db"
DB_USER = "admin"

db_conn = psycopg2.connect(
    user=DB_USER,
    password=DB_POSTGRES_PASS,
    host=DB_DATABASE_DNS,
    port=DATABASE_PORT,
    database=DB_NAME
)
db_conn.autocommit = True

# Model Database
ML_NAME = "ml-artifacts"
ML_USER = "ml_admin"

ml_conn = psycopg2.connect(
    user=ML_USER,
    password=ML_POSTGRES_PASS,
    host=ML_DATABASE_DNS,
    port=DATABASE_PORT,
    database=ML_NAME
)
ml_conn.autocommit = True

# Setup app
app = FastAPI()

# Define payload
class Evaluate(BaseModel):
    table_name: str
    target_col: str
    batch_id: str
    window_size: int = 10
    horizon: int = 24

# Accept payload
@app.post("/", status_code=status.HTTP_200_OK)
def post_root(payload: Evaluate):
    result_df = makeInference(
        sensor_conn=db_conn,
        ml_conn=ml_conn,
        table_name=payload.table_name,
        target_col=payload.target_col,
        batch_id=payload.batch_id,
        window_size=payload.window_size,
        horizon=payload.horizon
    )

    final_results = result_df.to_dict(orient="records")
    return final_results
