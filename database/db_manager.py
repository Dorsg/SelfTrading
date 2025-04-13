import logging
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import (
    AccountSnapshot, Trade, Positions,
    Runner, Order
)

logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self, db_session: Session):
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

    # ----- Orders -----
    def save_order(self, runner_id, ib_order_id, symbol, quantity, side, status, perm_id=None):
        """
        Creates and saves a new Order record in the DB.
        """
        try:
            new_order = Order(
                runner_id=runner_id,
                ib_order_id=ib_order_id,
                perm_id=perm_id,           # <-- store perm_id if we have it
                symbol=symbol,
                quantity=quantity,
                side=side,
                status=status,
                filled=(status == 'Filled')
            )
            self.db.add(new_order)
            self.db.commit()
            logger.info("Order saved: ib_order_id=%s, perm_id=%s, symbol=%s x%d (%s), status=%s",
                        ib_order_id, perm_id, symbol, quantity, side, status)
            return new_order
        except Exception:
            self.db.rollback()
            logger.exception("Failed to save order for %s", symbol)
            return None

    def get_open_orders(self):
        """
        Return all orders that are not filled or canceled.
        """
        try:
            return self.db.query(Order).filter(
                Order.status.notin_(["Filled", "Cancelled"])
            ).all()
        except Exception:
            logger.exception("Failed to fetch open orders")
            return []

    def update_order_status(self, order_id: int, new_status: str):
        """
        Update the status of an order. If filled/cancelled,
        mark accordingly.
        """
        try:
            order = self.db.query(Order).get(order_id)
            if not order:
                return
            order.status = new_status
            if new_status in ("Filled", "Cancelled"):
                order.filled = (new_status == "Filled")
            order.updated_at = datetime.utcnow()
            self.db.commit()
            logger.info("Order %d updated to %s (filled=%s)", 
                        order_id, new_status, order.filled)
        except Exception:
            self.db.rollback()
            logger.exception("Failed to update order status (ID=%d)", order_id)

    # ----- Trades -----
    def save_trade(self,
                   runner_id=None,
                   order_id=None,
                   ib_order_id=None,
                   symbol=None,
                   side=None,
                   quantity=0,
                   buy_price=None,
                   sell_price=None,
                   profit_loss=None):
        """
        Create a new Trade record.
        """
        try:
            trade = Trade(
                runner_id=runner_id,
                order_id=order_id,
                ib_order_id=ib_order_id,
                symbol=symbol,
                side=side,
                quantity=quantity,
                buy_price=buy_price,
                sell_price=sell_price,
                profit_loss=profit_loss if profit_loss is not None else 0.0,
            )
            self.db.add(trade)
            self.db.commit()
            logger.info("Trade saved: %s x%d (%s). buy_price=%.2f, sell_price=%.2f",
                        symbol, quantity, side,
                        buy_price if buy_price else 0.0,
                        sell_price if sell_price else 0.0)
        except Exception:
            self.db.rollback()
            logger.exception("Failed to save trade for %s", symbol)

    def get_trade_by_order_id(self, order_id: int):
        try:
            return self.db.query(Trade).filter(Trade.order_id == order_id).first()
        except Exception:
            logger.exception("Failed to fetch trade by order_id=%d", order_id)
            return None

    def upsert_executions_as_trades(self, executions: list):
        """
        Goes through the list of execution dictionaries (from IBManager.fetch_all_executions())
        and ensures each is in the trades table. 
        If you have partial fills, you might get multiple entries for the same orderId at different times.
        This example simply creates a new trade if one with matching ib_order_id + side + quantity doesn't exist.
        """
        try:
            inserted_count = 0
            for ex in executions:
                ib_order_id = ex['ib_order_id']
                symbol = ex['symbol']
                side = ex['side']
                qty = ex['quantity']
                price = ex['price']

                # Check if there's already a trade for this ib_order_id + side + symbol + quantity
                existing_trade = (self.db.query(Trade)
                    .filter(Trade.ib_order_id == ib_order_id)
                    .filter(Trade.side == side)
                    .filter(Trade.symbol == symbol)
                    .filter(Trade.quantity == qty)
                ).first()

                if existing_trade:
                    continue  # If partial fill logic needed, you'd update here
                else:
                    new_trade = Trade(
                        ib_order_id=ib_order_id,
                        symbol=symbol,
                        side=side,
                        quantity=qty,
                        buy_price=price if side == 'BUY' else None,
                        sell_price=price if side == 'SELL' else None,
                        profit_loss=0.0
                    )
                    self.db.add(new_trade)
                    inserted_count += 1

            if inserted_count > 0:
                self.db.commit()
            logger.info("Upserted %d new executions into Trades table", inserted_count)
        except Exception:
            self.db.rollback()
            logger.exception("Failed to upsert executions into Trades table")

    # Additional upsert methods for open & completed orders:
    def upsert_open_orders(self, ib_open_trades: list):
        """
        For each open Trade (ib_insync.Trade), upsert into 'orders' table.
        Now also capturing perm_id = trade.order.permId.
        """
        try:
            for t in ib_open_trades:
                ib_order_id = t.order.orderId
                perm_id = t.order.permId  # permanent ID from IB
                status = t.orderStatus.status
                symbol = t.contract.symbol
                quantity = int(t.order.totalQuantity)
                side = t.order.action.upper()
                filled_flag = (status == 'Filled')

                existing = self.db.query(Order).filter(Order.ib_order_id == ib_order_id).first()
                if existing:
                    # update
                    existing.perm_id = perm_id
                    existing.symbol = symbol
                    existing.quantity = quantity
                    existing.side = side
                    existing.status = status
                    existing.filled = filled_flag
                    existing.updated_at = datetime.utcnow()
                else:
                    new_order = Order(
                        ib_order_id=ib_order_id,
                        perm_id=perm_id,
                        symbol=symbol,
                        quantity=quantity,
                        side=side,
                        status=status,
                        filled=filled_flag,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    self.db.add(new_order)

            self.db.commit()
            logger.info("Upserted open orders: %d items", len(ib_open_trades))
        except Exception:
            self.db.rollback()
            logger.exception("Failed to upsert open orders")

    def upsert_completed_orders(self, completed_orders: list):
        """
        For each completed or canceled order (ib_insync.CompletedOrder),
        upsert into 'orders' table with final status and perm_id.
        """
        try:
            for c in completed_orders:
                contract = c.contract
                order = c.order
                order_state = c.orderState

                ib_order_id = order.orderId
                perm_id = order.permId  # permanent ID
                symbol = contract.symbol
                quantity = int(order.totalQuantity)
                side = order.action.upper()
                status = order_state.status
                filled_flag = (status == 'Filled')

                existing = self.db.query(Order).filter(Order.ib_order_id == ib_order_id).first()
                if existing:
                    existing.perm_id = perm_id
                    existing.symbol = symbol
                    existing.quantity = quantity
                    existing.side = side
                    existing.status = status
                    existing.filled = filled_flag
                    existing.updated_at = datetime.utcnow()
                else:
                    new_order = Order(
                        ib_order_id=ib_order_id,
                        perm_id=perm_id,
                        symbol=symbol,
                        quantity=quantity,
                        side=side,
                        status=status,
                        filled=filled_flag,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    self.db.add(new_order)

                # If filled, create a Trade if one doesn't exist yet
                if filled_flag:
                    trade_exists = self.db.query(Trade).filter(Trade.ib_order_id == ib_order_id).first()
                    if not trade_exists:
                        fill_price = float(order_state.completedAveragePrice or 0.0)
                        buy_px = fill_price if side == 'BUY' else None
                        sell_px = fill_price if side == 'SELL' else None

                        new_trade = Trade(
                            ib_order_id=ib_order_id,
                            symbol=symbol,
                            side=side,
                            quantity=quantity,
                            buy_price=buy_px,
                            sell_price=sell_px,
                            profit_loss=0.0
                        )
                        self.db.add(new_trade)

            self.db.commit()
            logger.info("Upserted completed orders: %d items", len(completed_orders))
        except Exception:
            self.db.rollback()
            logger.exception("Failed to upsert completed orders")

    # ----- Positions -----
    def save_positions(self, positions_data: list):
        """
        Clears the positions table and re-inserts current positions from IB.
        If you want historical position tracking, do something more advanced.
        """
        try:
            self.db.query(Positions).delete()

            for pos in positions_data:
                self.db.add(Positions(
                    symbol=pos['symbol'],
                    quantity=pos['quantity'],
                    avg_cost=pos['avgCost'],
                    account=pos['account'],
                    is_open=True
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
            runner = Runner(**data.dict())
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
