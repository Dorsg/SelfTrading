import schedule
import time
import logging
import threading
from logger_config import setup_logging
from database.db_manager import DBManager
from ib_manager.ib_connector import IBManager
from strategy_engine.strategy_manager import StrategyManager

setup_logging()
logger = logging.getLogger(__name__)

ib = IBManager()
strategy_manager = StrategyManager()
scheduler_lock = threading.Lock()

# --- Wrapper ---
def safe_job(job_func):
    def wrapped():
        with scheduler_lock:
            job_func()
    return wrapped

def run_scheduler():
    logger.info("Scheduler started")
    schedule.every(1).minutes.at(":00").do(safe_job(handle_daily_snapshot))
    schedule.every(1).minutes.at(":10").do(safe_job(update_open_positions))
    schedule.every(5).minutes.at(":20").do(safe_job(place_test_order))
    schedule.every(1).minutes.at(":30").do(safe_job(sync_ibkr_orders))
    schedule.every(1).minutes.at(":40").do(safe_job(sync_ibkr_executed_trades))

    while True:
        schedule.run_pending()
        time.sleep(1)

def handle_daily_snapshot():
    logger.info("Checking for daily account snapshot...")
    db = DBManager()

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


def update_open_positions():
    logger.info("Updating open positions...")
    db = DBManager()

    try:
        positions = ib.get_open_positions()
        if positions:
            db.update_open_positions(positions)
        else:
            logger.warning("No open positions returned.")
    except Exception:
        logger.exception("Failed in update_open_positions()")



def place_test_order():
    logger.info("Placing test stop order...")
    try:
        ib.place_test_aggressive_limit(123)
    except Exception:
        logger.exception("Failed in place_test_order()")

def sync_ibkr_orders():
    logger.info("Syncing live orders from IBKR...")
    try:
        ib.sync_orders_from_ibkr()
    except Exception:
        logger.exception("Failed to sync IBKR orders")

def sync_ibkr_executed_trades():
    logger.info("Syncing executed trades from IBKR...")
    try:
        ib.sync_executed_trades()
    except Exception:
        logger.exception("Failed to sync executed trades")