import psycopg2
import os
from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import Any

# Connect to database
POSTGRES_PASS = os.getenv('POSTGRES_PASS')
conn = psycopg2.connect(
    user="admin",
    password=POSTGRES_PASS,
    host="sensor-db-ha-rw.database-ns",
    port="5432",
    database="sensor-db"
)
conn.autocommit = True
cursor = conn.cursor()
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast');")
print(cursor.fetchall())

app = FastAPI()

class Evaluate(BaseModel):
    table_name:     str
    data:           int

@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Evaluate):
    sqlQuery = f"INSERT INTO temp (col2, col3) VALUES ('{item.table_name}', {(item.data)});"
    cursor.execute("DROP TABLE IF EXISTS temp CASCADE;")
    cursor.execute(
        '''
            CREATE TABLE temp (
                col1 SERIAL PRIMARY KEY,
                col2 VARCHAR(255),
                col3 INT
            ); 
        '''
    )
    cursor.execute(sqlQuery)
    cursor.execute("SELECT * FROM temp;")
    return cursor.fetchall()

# @app.post("/", status_code=status.HTTP_202_ACCEPTED)
# def post():
#     return "success!"
   