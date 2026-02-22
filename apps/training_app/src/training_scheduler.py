import os
import uuid
import asyncio
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from sqlalchemy import inspect
from model_trainer import app, sensor_engine
from api_schema import TrainingConfig
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%d-%m-%y %H:%M:%S",
)
logger = logging.getLogger(__name__)

COLS_TO_IGNORE = ["entry_id", "created_at"]

api = FastAPI(title="ML training API")


def get_db_config():
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
    db_tables, db_columns = get_db_config()

    if not db_tables:
        logger.error("Batch aborted: No tables found in database.")
        return None

    if config.tables:
        target_tables = [t for t in config.tables if t in db_tables]
    else:
        target_tables = db_tables

    if config.columns:
        target_columns = [c for c in config.columns if c in db_columns]
    else:
        target_columns = db_columns

    batch_id = str(uuid.uuid4())
    total_jobs = len(target_tables) * len(target_columns)

    logger.info(
        f"Queuing Batch {batch_id}: {total_jobs} total tasks ({len(target_tables)} tables x {len(target_columns)} columns)"
    )

    task_params = config.dict(exclude={"tables", "columns"})
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


@api.post("/train/batch")
async def trigger_via_api(config: TrainingConfig):
    logger.info("Received POST request on /train/batch")
    result = await run_training_batch(config)
    if not result:
        logger.warning("API responded with 404: Database is empty.")
        raise HTTPException(status_code=404, detail="No tables found in database.")
    return {"status": "queued", **result}


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "enable-api":
        uvicorn.run(api, host="0.0.0.0", port=8000)
        logger.info("Started FastAPI server on port 8000")
    else:
        logger.info("Executing CronJob")
        loop = asyncio.get_event_loop()
        res = loop.run_until_complete(run_training_batch(TrainingConfig()))
        if res:
            logger.info(f"Success! Batch {res['batch_id']} queued.")
        else:
            logger.error("Failed. No tables found.")
