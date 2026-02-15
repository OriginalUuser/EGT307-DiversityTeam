import os
from sqlalchemy import create_engine
import streamlit as st


@st.cache_resource
def get_engine():
    """
    Creates and returns a cached SQLAlchemy engine.
    This prevents multiple connections being opened on each Streamlit rerun.
    """

    # Accessing the database
    POSTGRES_PASS = os.getenv("POSTGRES_PASS")
    DATABASE_DNS = os.getenv("DATABASE_DNS")
    DATABASE_PORT = os.getenv("DATABASE_PORT")

    DB_NAME     = "sensor-db"
    USER        = "admin"
    PASSWORD    = POSTGRES_PASS
    HOST        = DATABASE_DNS
    PORT        = DATABASE_PORT

    engine = create_engine(
        f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}',
        pool_size=5,           # Max persistent connections
        max_overflow=10,       # Extra temporary connections
        pool_pre_ping=True     # Auto-reconnect if K8s restarts DB
    )

    return engine
