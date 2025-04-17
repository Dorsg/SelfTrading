import logging
from datetime import datetime, date
from sqlalchemy import func
from sqlalchemy.orm import Session
from database.db_core import SessionLocal
from database.models import AccountSnapshot, ExecutedTrade, OpenPosition, Order

logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self, db_session: Session = None):
        self._own_session = False
        if db_session is None:
            self.db = SessionLocal()
            self._own_session = True
        else:
            self.db = db_session

    def close(self):
        if self._own_session:
            self.db.close()

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
        finally:
            self.close()

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
        finally:
            self.close()

    def get_open_positions(self):
        try:
            positions = self.db.query(OpenPosition).all()
            return positions
        except Exception:
            logger.exception("Failed to fetch open positions from the database.")
            return []
        finally:
            self.close()


    def save_order(self, order_data: dict):
        try:
            order = Order(
                runner_id=order_data["runner_id"],
                ibkr_perm_id=order_data["ibkr_perm_id"],
                symbol=order_data["symbol"],
                action=order_data["action"],
                order_type=order_data["order_type"],
                quantity=order_data["quantity"],
                limit_price=order_data.get("limit_price"),
                stop_price=order_data.get("stop_price"),
                status=order_data.get("status"),
                filled_quantity=order_data.get("filled_quantity"),
                avg_fill_price=order_data.get("avg_fill_price"),
                account=order_data.get("account"),
            )
            self.db.add(order)
            self.db.commit()
            logger.info("Order saved successfully (IBKR ID: %s)", order.ibkr_perm_id)
            return order
        except Exception:
            logger.exception("Failed to save order to database.")
            self.db.rollback()
            return None
        finally:
            self.close()

    def sync_orders(self, orders: list[dict]):
        """
        Inserts or updates orders in the database based on permId.
        """
        try:
            for order_data in orders:
                perm_id = order_data["ibkr_perm_id"]
                existing = self.db.query(Order).filter(Order.ibkr_perm_id == perm_id).first()

                if existing:
                    for key, value in order_data.items():
                        setattr(existing, key, value)
                    logger.info("Updated order (permId: %s)", perm_id)
                else:
                    new_order = Order(**order_data)
                    self.db.add(new_order)
                    logger.info("Inserted new order (permId: %s)", perm_id)

            self.db.commit()
        except Exception:
            logger.exception("Failed to sync orders to database.")
            self.db.rollback()
        finally:
            self.close()
            
    def sync_executed_trades(self, trades: list[dict]):
        """
        Insert new fills; update the row if (perm_id, fill_time) already exists.
        """
        try:
            for t in trades:
                perm_id   = t["perm_id"]
                fill_time = t["fill_time"]

                existing = (
                    self.db.query(ExecutedTrade)
                    .filter(
                        ExecutedTrade.perm_id == perm_id,
                        ExecutedTrade.fill_time == fill_time,
                    )
                    .first()
                )

                if existing:
                    # update in‑place
                    for k, v in t.items():
                        setattr(existing, k, v)
                    logger.debug("Updated fill (perm=%s  time=%s)", perm_id, fill_time)
                else:
                    self.db.add(ExecutedTrade(**t))
                    logger.debug("Inserted new fill (perm=%s  time=%s)", perm_id, fill_time)

            self.db.commit()
            logger.info("Executed‑trades sync complete (rows processed: %d)", len(trades))

        except Exception:
            logger.exception("Failed to sync executed trades")
            self.db.rollback()
        finally:
            self.close()

    def get_all_orders(self):
        try:
            return self.db.query(Order).order_by(Order.created_at.desc()).all()
        except Exception:
            logger.exception("DB: Failed to fetch orders")
            return []


    def get_all_executed_trades(self):
        try:
            return self.db.query(ExecutedTrade).order_by(ExecutedTrade.fill_time.desc()).all()
        except Exception:
            logger.exception("DB: Failed to fetch executed trades")
            return []