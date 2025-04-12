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

    # 1) Save a daily account snapshot
    schedule.every(1).minutes.at(":00").do(handle_daily_snapshot)

    # 2) Simple example: place an order
    schedule.every(1).minutes.at(":00").do(execute_order)

    # 3) Periodic check of open trades, update statuses
    schedule.every(1).minutes.at(":30").do(update_orders_statuses)

    # 4) Periodic fetch of positions (e.g. every 5 minutes)
    schedule.every(5).minutes.at(":00").do(update_positions)

    while True:
        schedule.run_pending()
        time.sleep(1)

def execute_order():
    """
    Example: place a 1-share BUY market order for AAPL.
    """
    symbol = 'AAPL'
    quantity = 1
    status = ib.place_market_order(symbol, quantity)

    if status:
        logger.info("Trade executed: symbol=%s, quantity=%d, status=%s", symbol, quantity, status)
        db.save_trade_log(
            symbol=symbol,
            quantity=quantity,
            status=status,
            side="BUY"
        )
    else:
        logger.error("Trade failed or returned unknown status")

def handle_daily_snapshot():
    """
    If no snapshot exists for today, fetch account summary & save.
    """
    today = datetime.utcnow().date()
    if not db.has_snapshot_for_day(today):
        logger.info("No snapshot for %s, saving...", today)
        snapshot_data = ib.get_account_information()
        db.save_account_snapshot(snapshot_data)
    else:
        logger.info("Snapshot already exists for %s", today)

def update_orders_statuses():
    """
    Periodically fetch open trades from DB; see if their status changed in IB.
    If changed to 'Filled'/'Cancelled', mark them closed in DB.
    """
    logger.info("Checking open trades for status updates...")
    open_trades = db.get_open_trades()
    ib_trades = ib.get_all_trades()  # We'll implement get_all_trades() in IBManager

    for trade_log in open_trades:
        # Only works if trade_log.order_id is set
        if not trade_log.order_id:
            continue
        # Find the matching ib_insync trade by orderId
        matched = [t for t in ib_trades if t.order.orderId == trade_log.order_id]
        if matched:
            current_status = matched[0].orderStatus.status
            if current_status != trade_log.status:
                db.update_trade_status(trade_log.id, current_status)

def update_positions():
    """
    Fetch current positions from IB and save them to DB.
    """
    logger.info("Updating positions from IB...")
    positions_data = ib.get_positions()  # We'll implement get_positions() in IBManager
    db.save_positions(positions_data)
