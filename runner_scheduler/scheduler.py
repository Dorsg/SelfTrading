import random
import schedule
import time
import logging
from datetime import datetime
from logger_config import setup_logging
from database.db_core import SessionLocal
from database.db_manager import DBManager
from ib_manager.ib_connector import IBManager
from strategy_engine.strategy_manager import StrategyManager

setup_logging()
logger = logging.getLogger(__name__)

ib = IBManager()
db = DBManager(SessionLocal())
strategy_manager = StrategyManager()

def run_scheduler():
    logger.info("Scheduler started")
    #schedule.every(1).minutes.at(":00").do(handle_daily_snapshot)


    while True:
        schedule.run_pending()
        time.sleep(1)

