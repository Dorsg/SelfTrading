import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Always use the Docker database URL
DATABASE_URL = os.getenv("DATABASE_URL_DOCKER")

if not DATABASE_URL:
    logger.error("DATABASE_URL_DOCKER is not set.")
    raise ValueError("DATABASE_URL_DOCKER is required.")

try:
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=engine
    )
    logger.info("Connected to database successfully.")
except Exception:
    logger.exception("Failed to connect to the database.")
    raise
