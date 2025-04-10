import schedule
import time
from datetime import datetime
from database.database import SessionLocal
from database.db_manager import DBManager
from ib_manager.ib_connector import IBManager
from strategy_engine.strategy_manager import StrategyManager

ib = IBManager()
db = DBManager(SessionLocal())
strategy_manager = StrategyManager()


def run_scheduler():
    print("🎯 Scheduler started...")

    # Schedule the task to run every 5 minutes
    schedule.every(5).minutes.at(":00").do(handle_daily_snapshot)
    schedule.every(1).minutes.at(":00").do(execute_order)

    while True:
        schedule.run_pending()
        time.sleep(1)


def execute_order():
    symbol = 'AAPL'
    quantity = 1
    status = ib.place_market_order(symbol, quantity)

    if status:
        print(f"📈 Trade executed: {status}")
        db.save_trade_log(
            symbol=symbol,
            quantity=quantity,
            status=status,
            side="BUY" 
        )
    else:
        print("❌ Trade failed or status unknown")

    


def handle_daily_snapshot():
    today = datetime.utcnow().date()

    if not db.has_snapshot_for_day(today):
        print(f"📦 No snapshot for {today}, saving...")
        snapshot_data = ib.get_account_information()
        db.save_account_snapshot(snapshot_data)
    else:
        print(f"✅ Snapshot already exists for {today}")
