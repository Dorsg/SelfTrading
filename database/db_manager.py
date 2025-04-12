import logging
from datetime import datetime
from database.models import AccountSnapshot, TradeLog, Positions, Runner

logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self, db_session):
        self.db = db_session

    # ----- Snapshots -----
    def has_snapshot_for_day(self, date):
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        exists = (
            self.db.query(AccountSnapshot)
                   .filter(AccountSnapshot.timestamp >= start,
                           AccountSnapshot.timestamp <= end)
                   .first() is not None
        )
        logger.debug("Checked snapshot for %s: exists=%s", date, exists)
        return exists

    def save_account_snapshot(self, data):
        try:
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
            logger.info("Account snapshot saved to DB")
        except Exception:
            self.db.rollback()
            logger.exception("Failed to save account snapshot")

    # ----- Trades -----
    def save_trade_log(self, symbol: str, quantity: int, status: str,
                       side: str = "BUY", order_id=None, strategy_name=None):
        try:
            is_open = status not in ("Filled", "Cancelled")
            trade = TradeLog(
                symbol=symbol,
                quantity=quantity,
                side=side,
                status=status,
                order_id=order_id,
                strategy_name=strategy_name,
                is_open=is_open
            )
            self.db.add(trade)
            self.db.commit()
            logger.info("Trade log saved: %s x%d (%s), status=%s", symbol, quantity, side, status)
        except Exception:
            self.db.rollback()
            logger.exception("Failed to save trade log for %s", symbol)

    def get_open_trades(self):
        return self.db.query(TradeLog).filter(TradeLog.is_open == True).all()

    def update_trade_status(self, trade_id: int, new_status: str):
        try:
            trade = self.db.query(TradeLog).get(trade_id)
            if not trade:
                return
            trade.status = new_status
            if new_status in ("Filled", "Cancelled"):
                trade.is_open = False
            self.db.commit()
            logger.info("Trade %d updated to %s (is_open=%s)", trade_id, new_status, trade.is_open)
        except Exception:
            self.db.rollback()
            logger.exception("Failed to update trade status (ID=%d)", trade_id)

    # ----- Positions -----
    def save_positions(self, positions_data: list):
        try:
            self.db.query(Positions).delete()
            for pos in positions_data:
                self.db.add(Positions(
                    symbol=pos['symbol'],
                    quantity=pos['quantity'],
                    avg_cost=pos['avgCost'],
                    account=pos['account']
                ))
            self.db.commit()
            logger.info("Positions saved (%d entries)", len(positions_data))
        except Exception:
            self.db.rollback()
            logger.exception("Failed to save positions")

    # ----- Runners -----
    def get_all_runners(self):
        try:
            runners = self.db.query(Runner).all()
            logger.info("Fetched %d runners", len(runners))
            return runners
        except Exception:
            logger.exception("Failed to fetch runners")
            return []

    def create_runner(self, data):
        try:
            runner = Runner(**data)
            self.db.add(runner)
            self.db.commit()
            logger.info("Runner created: %s", runner)
            return runner
        except Exception:
            self.db.rollback()
            logger.exception("Failed to create runner")
            raise

    def delete_runner(self, runner_id):
        try:
            runner = self.db.query(Runner).get(runner_id)
            if not runner:
                logger.warning("Runner not found: id=%s", runner_id)
                return False
            self.db.delete(runner)
            self.db.commit()
            logger.info("Runner deleted: id=%s", runner_id)
            return True
        except Exception:
            self.db.rollback()
            logger.exception("Failed to delete runner (id=%s)", runner_id)
            raise