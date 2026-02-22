# Description: Script to write jobs to the job queue via either API or Cronjob.
# Formatted and linted with Ruff

import uuid
import asyncio
import sys
from typing import Dict

import uvicorn
from fastapi import FastAPI, HTTPException
from sqlalchemy import inspect
from model_trainer import app, sensor_engine
from api_schema import TrainingConfig
import logging

# Define logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%d-%m-%y %H:%M:%S",
)
logger = logging.getLogger(__name__)

COLS_TO_IGNORE = ["entry_id", "created_at"]

###########
# FastAPI #
###########

# API is defined in the same file because it is part of the same system used to create the job queue.

# Init FastAPI
api = FastAPI(title="ML training API")


@api.post("/train/batch")  # Send to service "ml-artifacts-db-rw" in the cluster
async def trigger_via_api(
    config: TrainingConfig,
) -> Dict:  # Use schema defined in api_schema.py
    """
    API endpoint to initiate a batch training process.

    Receives training parameters, validates database tables, and sequentially
    queues training tasks into the PostgreSQL-backed task queue.

    Args:
        config (TrainingConfig): Configuration for tables, columns, and hyperparameters.

    Returns:
        dict: A success status with the unique batch_id and total job count.

    Raises:
        HTTPException: 404 error if no matching tables are found in the DB.
    """
    logger.info("Received POST request!")
    result = await run_training_batch(config)
    if not result:
        logger.warning("Database is empty.")
        raise HTTPException(status_code=404, detail="No tables found in database.")
    return {"status": "queued", **result}


####################
# Helper Functions #
####################


def _get_db_config():
    """
    Identifes IoT tables and available sensor columns from database schema.

    Filters the 'public' schema for tables with an 'iot_' prefix and retrieves
    valid feature columns from the first matching table, excluding those
    defined in COLS_TO_IGNORE.

    Returns:
        tuple: A pair containing:
            - list[str]: Identified IoT table names.
            - list[str]: Valid sensor column names for training.
    """
    inspector = inspect(sensor_engine)
    tables = [
        name
        for name in inspector.get_table_names(schema="public")
        if name.split("_")[0] == "iot"
    ]

    if not tables:
        logger.warning("No tables found in sensor-db.")
        return [], []

    cols_info = inspector.get_columns(tables[0])
    columns = [c["name"] for c in cols_info if c["name"] not in COLS_TO_IGNORE]
    return tables, columns


async def run_training_batch(config: TrainingConfig):
    """
    Creates the job tasks to the Procrastinate job queue. (Similar to how you define a couroutine list in normal python)

    Args:
        config (TrainingConfig): Configuration object containing table/column
            filters and model hyperparameters.

    Returns:
        dict: Metadata about the queued batch including 'batch_id' and
            'total_jobs'. Returns None if no valid tables are found.
    """
    db_tables, db_columns = _get_db_config()

    # Abort if no tables in the sensor database
    if not db_tables:
        logger.error("Batch aborted: No tables found in database.")
        return None

    # Create a list of all the tables with sensor data
    if config.tables:
        target_tables = [t for t in config.tables if t in db_tables]
    else:
        target_tables = db_tables

    # Create a list of all the columns in the tables
    if config.columns:
        target_columns = [c for c in config.columns if c in db_columns]
    else:
        target_columns = db_columns

    # Create a batch id for unqiue training identification
    batch_id = str(uuid.uuid4())

    # Get total number of jobs queued for logging
    total_jobs = len(target_tables) * len(target_columns)

    logger.info(
        f"Queuing Batch {batch_id}: {total_jobs} total tasks ({len(target_tables)} tables x {len(target_columns)} columns)"
    )

    task_params = config.dict(exclude={"tables", "columns"})

    # Queue the jobs to the queue sequeuentially
    async with app.open_async():
        for table in target_tables:
            for col in target_columns:
                await app.configure_task(name="train_model_sql").defer_async(
                    batch_id=batch_id, table_name=table, target_col=col, **task_params
                )

    logger.info(f"Batch {batch_id} successfully dispatched to Procrastinate.")

    return {
        "batch_id": batch_id,
        "total_jobs": len(target_tables) * len(target_columns),
    }


if __name__ == "__main__":
    # If script is run as `python -m training_scheduler.py enable-api`, the api will be used with the POSTed training configurations
    if len(sys.argv) > 1 and sys.argv[1] == "enable-api":
        logger.info("Started FastAPI server on port 8000")
        uvicorn.run(
            api, host="0.0.0.0", port=8000
        )  # Set host to 0.0.0.0 to accept requests from anywhere. This allows me to accept requests from other namespaces

    # Else, if the script is is run as `"python", "training_scheduler.py"`, it will use the default training configurations.
    # Used by the cronjob
    else:
        logger.info("Executing CronJob")
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(
            run_training_batch(TrainingConfig())
        )  # Use default training parameter configuration
        if res:
            logger.info(f"Success! Batch {res['batch_id']} queued.")
        else:
            logger.error("Failed. No tables found.")
