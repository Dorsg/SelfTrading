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
    schedule.every(1).minutes.at(":00").do(handle_daily_snapshot)
    schedule.every(1).minutes.at(":00").do(execute_order)
    schedule.every(1).minutes.at(":30").do(update_orders_statuses)
    schedule.every(1).minutes.at(":00").do(update_positions)
    schedule.every(1).minutes.at(":30").do(sync_orders_from_ib)
    schedule.every(1).minutes.do(sync_historical_trades)

    while True:
        schedule.run_pending()
        time.sleep(1)


def execute_order():
    symbols = ['AAPL', 'AMZN', 'PLTR', 'NVDA', 'TSLA']
    symbol = random.choice(symbols)
    quantity = 1
    side = 'BUY'

    # 1. Get current price
    market_price = ib.get_market_price(symbol)
    if not market_price:
        logger.warning("Could not retrieve market price for %s", symbol)
        return

    stop_price = round(market_price * 1.01, 2)

    # 2. Place a STOP BUY order at +1% price
    status, ib_order_id, fill_price, perm_id = ib.place_order(
        symbol=symbol,
        quantity=quantity,
        side=side,
        order_type='STP',
        aux_price=stop_price
    )

    # 3. Save the order in DB
    new_order = db.save_order(
        runner_id=None,
        ib_order_id=ib_order_id,
        symbol=symbol,
        quantity=quantity,
        side=side,
        status=status,
        perm_id=perm_id
    )

    logger.info("Stop order placed: %s BUY %d @ %.2f | status=%s | perm_id=%s",
                symbol, quantity, stop_price, status, perm_id)

    # 4. If order filled immediately (rare), save the trade
    if status == 'Filled' and fill_price is not None and new_order:
        db.save_trade(
            runner_id=new_order.runner_id,
            order_id=new_order.id,
            ib_order_id=ib_order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            buy_price=fill_price,
            sell_price=None,
            profit_loss=0.0
        )
        logger.info("Trade executed immediately: %s BUY %d @ %.2f", symbol, quantity, fill_price)

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
    Periodically fetch open orders *from this session* in DB; see if status changed in IB.
    If changed to 'Filled'/'Cancelled', update accordingly.
    If filled, create a Trade entry if none exists yet.
    """
    logger.info("Checking open orders for status updates...")
    open_orders = db.get_open_orders()
    ib_orders_status = ib.get_all_orders_status()  # from this client session only

    for order in open_orders:
        matching = [o for o in ib_orders_status if o['orderId'] == order.ib_order_id]
        if not matching:
            continue

        new_status = matching[0]['status']
        fill_price = matching[0].get('fillPrice', None)

        if new_status != order.status:
            db.update_order_status(order.id, new_status)
            logger.info("Order %d (IB ID %d) updated to status=%s",
                        order.id, order.ib_order_id, new_status)

            # If the order just filled, create a Trade if not already created
            if new_status == 'Filled' and fill_price is not None:
                existing_trade = db.get_trade_by_order_id(order.id)
                if not existing_trade:
                    db.save_trade(
                        runner_id=order.runner_id,
                        order_id=order.id,
                        ib_order_id=order.ib_order_id,
                        symbol=order.symbol,
                        side=order.side,
                        quantity=order.quantity,
                        buy_price=fill_price if order.side == 'BUY' else None,
                        sell_price=fill_price if order.side == 'SELL' else None,
                        profit_loss=0.0
                    )
                    logger.info("Trade created for filled order %d at price %.2f",
                                order.id, fill_price)

def update_positions():
    """
    Fetch current positions from IB and save them to DB.
    """
    logger.info("Updating positions from IB...")
    positions_data = ib.get_positions()
    db.save_positions(positions_data)

def sync_historical_trades():
    """
    Periodically fetch all recent executions from IB and store them in our Trades table.
    Typically covers last ~24 hours. If trades are older than that, IB won't return them.
    """
    logger.info("Syncing all historical trades from IB to local DB...")
    executions = ib.fetch_all_executions()  # new method in IBManager
    db.upsert_executions_as_trades(executions)
    logger.info("Historical trades sync complete.")

def sync_orders_from_ib():
    """
    Periodically fetch all open orders + recently completed orders from IB.
    This ensures your orders table is updated with *all* open & final statuses.
    """
    logger.info("Syncing open/closed orders from IB to local DB...")

    # 1) All open trades (includes partial fills, pre-submitted, etc.)
    open_trades = ib.fetch_all_open_orders()
    db.upsert_open_orders(open_trades)

    # 2) Recently completed or cancelled orders
    completed_orders = ib.fetch_completed_orders()
    db.upsert_completed_orders(completed_orders)

    logger.info("Order sync complete.")
