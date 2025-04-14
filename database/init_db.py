import logging
from database.models import Base
from database.db_core import engine

logger = logging.getLogger(__name__)

def create_tables():
    try:
        logger.info("Creating tables via Base.metadata.create_all...")
        Base.metadata.create_all(bind=engine)
        logger.info("Table creation completed.")
    except Exception:
        logger.exception("Error occurred during table creation.")

if __name__ == "__main__":
    create_tables()
