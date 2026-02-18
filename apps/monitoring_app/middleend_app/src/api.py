import os
import uuid

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

import procrastinate
from procrastinate.contrib.aiopg import AiopgConnector

import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_NAME = os.getenv("DATABASE_NAME")
POSTGRES_PASS = os.getenv("POSTGRES_PASS")
DATABASE_HOST = os.getenv("DATABASE_HOST")
DATABASE_PORT = os.getenv("DATABASE_PORT")
DATABASE_URI = f"postgresql://{DATABASE_USER}:{POSTGRES_PASS}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
logger.debug("Engine created successfully")

api = FastAPI(title="Monitoring API")
app = procrastinate.App(connector=AiopgConnector(dsn=DATABASE_URI)) 

class Evaluate(BaseModel):
    table_name          : str
    columns_to_check    : list[str] = ["temperature", "turbidity", "dissolved_oxygen", "ph", "ammonia", "nitrate", "population", "fish_length", "fish_weight"]
    report_range        : int       = 10000

async def queue_generation(task: Evaluate) -> dict:
    batch_id = str(uuid.uuid4())
    logger.info(f"Queuing Task {batch_id}: Create report for {task.table_name}")
    await app.configure_task(name="generate_report").defer_async(
        batch_id=batch_id,
        **task.model_dump()
    )
    logger.info(f"Batch {batch_id} successfully dispatched to Procrastinate.")
    return {"batch_id": batch_id, **task.model_dump()}

@api.post("/", status_code=status.HTTP_200_OK)
async def generate_report(config: Evaluate) -> dict:
    logger.info("Received POST request on /")
    result = await queue_generation(config)
    if not result:
        raise HTTPException(status_code=404, detail="No tables found in database.")
    return {"status": "queued", **result}

@api.get("/", status_code=status.HTTP_200_OK)
def get_root():
    return "Hello world"