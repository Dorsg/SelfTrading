import logging
import database.db_core as db
from database.models import Base

logger = logging.getLogger(__name__)

def create_tables():
    try:
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=db.engine)
        logger.info("Table creation completed.")
    except Exception:
        logger.exception("Error occurred during table creation.")

if __name__ == "__main__":
    create_tables()
