from datetime import datetime
from database.models import AccountSnapshot, TradeLog

class DBManager:
    def __init__(self, db_session):
        self.db = db_session

    def has_snapshot_for_day(self, date):
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())

        return self.db.query(AccountSnapshot).filter(
            AccountSnapshot.timestamp >= start,
            AccountSnapshot.timestamp <= end
        ).first() is not None

    def save_account_snapshot(self, data):
        snapshot = AccountSnapshot(
            timestamp=datetime.utcnow(),
            total_cash_value=data.get("TotalCashValue (USD)", 0),
            net_liquidation=data.get("NetLiquidation (USD)", 0),
            available_funds=data.get("AvailableFunds (USD)", 0),
            buying_power=data.get("BuyingPower (USD)", 0),
            unrealized_pnl=data.get("UnrealizedPnL (USD)", 0),
            realized_pnl=data.get("RealizedPnL (USD)", 0),
            equity_with_loan_value=data.get("EquityWithLoanValue (USD)", 0),
            excess_liquidity=data.get("ExcessLiquidity (USD)", 0),
            gross_position_value=data.get("GrossPositionValue (USD)", 0),
            cushion=float(data.get("Cushion", 0))
        )
        self.db.add(snapshot)
        self.db.commit()

    def save_trade_log(self, symbol: str, quantity: int, status: str, side: str = "BUY", order_id=None, strategy_name=None):
        try:
            trade = TradeLog(
                symbol=symbol,
                quantity=quantity,
                side=side,
                status=status,
                order_id=order_id,
                strategy_name=strategy_name
            )
            self.db.add(trade)
            self.db.commit()
            print("📝 Trade log saved to DB.")
        except Exception as e:
            self.db.rollback()
            print(f"❌ Failed to save trade log: {e}")