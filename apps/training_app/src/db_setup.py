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
ML_DB_USER = os.environ.get('ML_DB_USER')
ML_DB_PASSWORD = os.environ.get('ML_DB_PASSWORD')

# Database Connection Details
ML_DB_HOST = os.environ.get('ML_DB_HOST')

# Database port
DB_PORT = os.environ.get('DB_PORT')

# Database name
ML_DB_NAME = os.environ.get('ML_DB_NAME')

# Database URIs
ML_DB_URI = f"postgresql://{ML_DB_USER}:{ML_DB_PASSWORD}@{ML_DB_HOST}:{DB_PORT}/{ML_DB_NAME}"

def run_setup():
    connector = PsycopgConnector(conninfo=ML_DB_URI)
    app = App(connector=connector)

    with app.open():
        with psycopg2.connect(ML_DB_URI) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'procrastinate_jobs');")
                schema_exists = cur.fetchone()[0]
        
        if not schema_exists:
            app.schema_manager.apply_schema()
            logger.info("Applied Procrastinate schema")
        else:
            logger.info("Skipping application of Procastinate schema; Procrastinate schema already exists")

    with psycopg2.connect(ML_DB_URI) as conn:
        with conn.cursor() as cur:
            with open('db_schema.sql', 'r') as f:
                cur.execute(f.read())
        conn.commit()
        logger.info("Applied model training database schema")
    
    logger.info("DB Setup complete! ^^")

if __name__ == "__main__":
    run_setup()