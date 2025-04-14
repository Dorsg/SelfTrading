import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env
load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    # You can raise an error or log a warning, but you definitely want to handle this
    logger.error("DATABASE_URL environment variable is not set. Make sure .env is loaded or Docker env is passed.")
    raise ValueError("DATABASE_URL is not set.")

try:
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Successfully connected to the database.")
except Exception:
    logger.exception("Failed to connect to the database.")
    raise