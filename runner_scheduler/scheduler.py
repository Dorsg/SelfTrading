import schedule
import time
import logging
from logger_config import setup_logging
from database.db_core import SessionLocal
from database.db_manager import DBManager
from ib_manager.ib_connector import IBManager
from strategy_engine.strategy_manager import StrategyManager

setup_logging()
logger = logging.getLogger(__name__)

ib = IBManager()
strategy_manager = StrategyManager()

def run_scheduler():
    logger.info("Scheduler started")
    schedule.every(1).minutes.do(handle_daily_snapshot)

    while True:
        schedule.run_pending()
        time.sleep(1)


def handle_daily_snapshot():
    logger.info("Checking for daily account snapshot...")
    db_session = SessionLocal()
    db = DBManager(db_session)

    try:
        existing = db.get_today_snapshot()
        if existing:
            logger.info("Snapshot for today already exists. Skipping...")
            return

        snapshot_data = ib.get_account_information()
        if not snapshot_data:
            logger.warning("Empty account data returned.")
            return

        db.create_account_snapshot(snapshot_data)
    except Exception:
        logger.exception("Failed in handle_daily_snapshot()")
    finally:
        db_session.close()

