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

# Database Credentials
SENSOR_DB_USER = os.environ.get('SENSOR_DB_USER')
SENSOR_DB_PASS = os.environ.get('SENSOR_DB_PASS')

# Database Connection Details
SENSOR_DB_HOST = os.environ.get('SENSOR_DB_HOST')

# Database port
SENSOR_DB_PORT = os.environ.get('SENSOR_DB_PORT')

# Database name
SENSOR_DB_NAME = os.environ.get('SENSOR_DB_NAME')

# Database URIs
SENSOR_DB_URI = f"postgresql://{SENSOR_DB_USER}:{SENSOR_DB_PASS}@{SENSOR_DB_HOST}:{SENSOR_DB_PORT}/{SENSOR_DB_NAME}"

def run_setup():
    connector = PsycopgConnector(conninfo=SENSOR_DB_URI)
    app = App(connector=connector)

    with app.open():
        with psycopg2.connect(SENSOR_DB_URI) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'procrastinate_jobs');")
                schema_exists = cur.fetchone()[0]
        
        if not schema_exists:
            app.schema_manager.apply_schema()
            logger.info("Applied Procrastinate schema")
        else:
            logger.info("Skipping application of Procastinate schema; Procrastinate schema already exists")
    
    logger.info("DB Setup complete! ^^")

if __name__ == "__main__":
    run_setup()