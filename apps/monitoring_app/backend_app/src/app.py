import os
import time
import logging

import pandas as pd
from sqlalchemy import create_engine
from .reporting import generate_report, is_data_drift
from evidently.ui.workspace import RemoteWorkspace

from fastapi import FastAPI, status
from pydantic import BaseModel
from requests.exceptions import ConnectionError

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Accessing the database
POSTGRES_PASS = os.getenv('POSTGRES_PASS')
DATABASE_DNS = os.getenv('POSTGRES_PASS')
DATABASE_PORT = os.getenv('POSTGRES_PASS')

DB_NAME     = "sensor-db"
USER        = "admin"
PASSWORD    = POSTGRES_PASS
HOST        = DATABASE_DNS
PORT        = DATABASE_PORT
engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}')
logger.debug("Engine created successfully")

# Connect to the remote workspace for updating the monitoring dashboards
WORKSPACE_URL = os.getenv("WORKSPACE_URL")
ws = None
for retry in range(10):
    try:
        ws = RemoteWorkspace(WORKSPACE_URL)
        break
    except ConnectionError:
        logger.warning("Workspace project problem: ConnectionError")
        time.sleep(10)
assert ws is not None, "Workspace failed to connect"
logger.debug("Workspace project connected successfully")

# Connect to dashboard
project = ws.search_project("Aquaponics Monitoring")
# if isinstance(project, list): project = project[0]

class Evaluate(BaseModel):
    table_name          : str
    columns_to_check    : list[str] = ["temperature", "turbidity", "dissolved_oxygen", "ph", "ammonia", "nitrate", "population", "fish_length", "fish_weight"]
    report_range        : int       = 10000

@app.post("/", status_code=status.HTTP_202_ACCEPTED)
async def post_root(payload: Evaluate):
    # Get the most recent {report_range} rows
    sql_query = f"SELECT * FROM {payload.table_name} ORDER BY created_at DESC FETCH FIRST {payload.report_range} ROWS ONLY;"
    df = pd.read_sql(sql_query, engine)
    logger.debug("Data has been loaded")

    # Split extracted data into half for reference data and current data splits
    halfway_point = payload.report_range / 2
    current = df.iloc[:halfway_point, :]
    reference = df.iloc[halfway_point:, :]

    # Generate a data drift report
    drift_snapshot, drift_snapshot_dict = generate_report(
        reference_df=reference, 
        current_df=current, 
        columns=payload.columns_to_check, 
        num_metrics="wasserstein",
        cat_metrics="jensenshannon"
    )

    # Send the report to the dashboard
    ws.add_run(project.id, drift_snapshot)
    logger.debug("Report generated and added to workspace")

    # If model retraining is required, call the retraining pipeline
    if is_data_drift(drift_snapshot_dict):
        # TODO: Send retraining request to the training pipeline service
        logger.debug("Data drift detected, sending retraining request")
        pass

    return 

@app.get("/", status_code=status.HTTP_200_OK)
def get_root():
    return