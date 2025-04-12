from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:password@db:5432/self_trading_db"

try:
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Successfully connected to the database.")
except Exception:
    logger.exception("Failed to connect to the database.")
    raise
