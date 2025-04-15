import logging
from datetime import datetime, date
from sqlalchemy import func
from sqlalchemy.orm import Session
from database.models import AccountSnapshot, OpenPosition

logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_today_snapshot(self):
        today = date.today()
        return (
            self.db.query(AccountSnapshot)
            .filter(func.date(AccountSnapshot.timestamp) == today)
            .first()
        )

    def create_account_snapshot(self, snapshot_data: dict):
        try:
            snapshot = AccountSnapshot(
                timestamp=datetime.utcnow(),
                total_cash_value=snapshot_data.get("TotalCashValue (USD)"),
                net_liquidation=snapshot_data.get("NetLiquidation (USD)"),
                available_funds=snapshot_data.get("AvailableFunds (USD)"),
                buying_power=snapshot_data.get("BuyingPower (USD)"),
                unrealized_pnl=snapshot_data.get("UnrealizedPnL (USD)"),
                realized_pnl=snapshot_data.get("RealizedPnL (USD)"),
                excess_liquidity=snapshot_data.get("ExcessLiquidity (USD)"),
                gross_position_value=snapshot_data.get("GrossPositionValue (USD)"),
                account=snapshot_data.get("account"),
            )
            self.db.add(snapshot)
            self.db.commit()
            logger.info("Account snapshot created successfully.")
            return snapshot
        except Exception:
            logger.exception("Failed to insert account snapshot.")
            self.db.rollback()
            return None

    def update_open_positions(self, positions: list):
        try:
            self.db.query(OpenPosition).delete()
            for pos in positions:
                new_pos = OpenPosition(
                    symbol=pos["symbol"],
                    quantity=pos["quantity"],
                    avg_price=pos["avgCost"],
                    account=pos["account"],
                )
                self.db.add(new_pos)
            self.db.commit()
            logger.info("Open positions updated successfully.")
        except Exception:
            logger.exception("Failed to update open positions.")
            self.db.rollback()

    def get_open_positions(self):
        try:
            positions = self.db.query(OpenPosition).all()
            return positions
        except Exception:
            logger.exception("Failed to fetch open positions from the database.")
            return []
