import os
import time
import logging
import requests

import pandas as pd
from sqlalchemy import create_engine
from reporting import generate_report, is_data_drift
from evidently.ui.workspace import RemoteWorkspace

import procrastinate
from procrastinate.contrib.aiopg import AiopgConnector

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Accessing the database
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_NAME = os.getenv("DATABASE_NAME")
POSTGRES_PASS = os.getenv("POSTGRES_PASS")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_URI = f"postgresql://{DATABASE_USER}:{POSTGRES_PASS}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

engine = create_engine(DATABASE_URI)
logger.debug("Engine created successfully")

# Get training url
TRAINING_PORT = os.getenv("TRAINING_PORT")
TRAINING_DNS = os.getenv("TRAINING_DNS")
TRAINING_URL = f"http://{TRAINING_DNS}:{TRAINING_PORT}/train/batch"

# Setup procrastinate
app = procrastinate.App(connector=AiopgConnector(dsn=DATABASE_URI)) 

# Connect to the remote workspace for updating the monitoring dashboards
WORKSPACE_DNS = os.getenv("WORKSPACE_DNS")
WORKSPACE_PORT = os.getenv("WORKSPACE_PORT")
WORKSPACE_URL = f"http://{WORKSPACE_DNS}:{WORKSPACE_PORT}"
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
if isinstance(project, list): project = project[0]

@app.task(name="generate_report")
async def generation_task(
    batch_id: str,
    table_name: str,
    columns_to_check: list[str],
    report_range: int
):
    # Get the most recent {report_range} rows
    sql_query = f"SELECT * FROM {table_name} ORDER BY created_at DESC FETCH FIRST {report_range} ROWS ONLY;"
    df = pd.read_sql(sql_query, engine)
    df = df.loc[:, columns_to_check]
    logger.debug("Data has been loaded")

    # If the report range is larger than the dataset, use the dataset's max length instead
    if report_range > df.shape[0]:
        report_range = df.shape[0]

    # Split extracted data into half for reference data and current data splits
    if report_range % 2 != 0:
        # Report range must be even
        report_range = report_range + 1
    else:
        report_range = report_range

    halfway_point = int(report_range / 2)
    current = df.iloc[:halfway_point, :]
    reference = df.iloc[halfway_point:, :]

    # Generate a data drift report
    drift_snapshot, drift_snapshot_dict = generate_report(
        reference_df=reference, 
        current_df=current, 
        columns=columns_to_check,
        metadata={"table": table_name}
    )

    # Send the report to the dashboard
    ws.add_run(project.id, drift_snapshot)
    logger.info(f"Report Generated for batch: {batch_id}") 

    # If model retraining is required, call the retraining pipeline
    if is_data_drift(drift_snapshot_dict):
        logger.debug("Data drift detected, sending retraining request")
        data_payload = {
            "tables": [table_name],
            "rows_limit": halfway_point
        }
        response = requests.post(url=TRAINING_URL, json=data_payload)

        logger.info(f"Response: {response.status_code}") 
        logger.info(f"Response: {response.text}") 
    else:
        logger.info(f"No data drift detected")

if __name__ == "__main__":
    app.run_worker_async()