import time
import logging
from sqlalchemy.exc import OperationalError
from database.models import Base
from database.db_core import engine

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def create_tables():
    max_retries = 10
    delay_seconds = 3

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempt {attempt} of {max_retries}: Creating tables via Base.metadata.create_all...")
            Base.metadata.create_all(bind=engine)
            logger.info("Table creation completed.")
            return
        except OperationalError as e:
            logger.warning(f"DB not ready yet: {e}")
            if attempt < max_retries:
                logger.info(f"Retrying in {delay_seconds} seconds...")
                time.sleep(delay_seconds)
            else:
                logger.error("Failed to connect to DB after all retries.")
        except Exception:
            logger.exception("Unexpected error during table creation.")
            return

if __name__ == "__main__":
    create_tables()
