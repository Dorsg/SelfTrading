from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URL = "postgresql://postgres:password@localhost:5432/self_trading_db"

try:
    engine = create_engine(DATABASE_URL, echo=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("✅ Successfully connected to the database.")
except Exception as e:
    logger.exception("❌ Failed to connect to the database.")
    raise