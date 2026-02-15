import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from procrastinate import App, PsycopgConnector
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%d-%m-%y %H:%M:%S"
)
logger = logging.getLogger(__name__)

SENSOR_DB_URI = os.getenv("SENSOR_DATABASE_URL")

def run_setup():
    new_db_name = "ml_artifacts"

    conn = psycopg2.connect(SENSOR_DB_URI)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (new_db_name,))
        if not cur.fetchone():
            cur.execute(f"CREATE DATABASE {new_db_name}")
            logger.info(f"Created database: {new_db_name}")
    conn.close()

    artifact_db_url = SENSOR_DB_URI.rsplit('/', 1)[0] + f"/{new_db_name}"
    connector = PsycopgConnector(conninfo=artifact_db_url)
    app = App(connector=connector)

    with app.open():
        with psycopg2.connect(artifact_db_url) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'procrastinate_jobs');")
                schema_exists = cur.fetchone()[0]
        
        if not schema_exists:
            app.schema_manager.apply_schema()
            logger.info("Applied Procrastinate schema")
        else:
            logger.info("Skipping application of Procastinate schema; Procrastinate schema already exists")

    with psycopg2.connect(artifact_db_url) as conn:
        with conn.cursor() as cur:
            with open('db_schema.sql', 'r') as f:
                cur.execute(f.read())
        conn.commit()
        logger.info("Applied model training database schema")
    
    logger.info("DB Setup complete! ^^")

if __name__ == "__main__":
    run_setup()