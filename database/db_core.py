import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Detect if running in Docker
DOCKER_MODE = os.getenv("DOCKER_MODE", "false").lower() == "true"

# Pick the correct DB URL
DATABASE_URL = (
    os.getenv("DATABASE_URL_DOCKER")
    if DOCKER_MODE
    else os.getenv("DATABASE_URL")
)

if not DATABASE_URL:
    logger.error("DATABASE_URL is not set.")
    raise ValueError("DATABASE_URL is required.")

try:
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Connected to database successfully.")
except Exception:
    logger.exception("Failed to connect to the database.")
    raise