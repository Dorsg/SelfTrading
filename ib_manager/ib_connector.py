import logging
import math
import random
from typing import Optional
from ib_insync import IB, LimitOrder, Stock
import os

from database.db_manager import DBManager
from ib_manager.market_data_manager import MarketDataManager

# ──────────── Setup Logging ────────────
log = logging.getLogger("IBKR-Business-Manager")

# Load connection timeout from environment variables
IB_CONNECTION_TIMEOUT = int(os.getenv("IB_CONNECTION_TIMEOUT", 60))

class IBBusinessManager:
    def __init__(self, user):
        self.user = user
        self.ib = IB()
        self.port = 4004 + user.id

    async def connect(self):
        try:
            log.info(f"Connecting to IB Gateway for user {self.user.id} on port {self.port}")
            await self.ib.connectAsync("host.docker.internal", self.port, clientId=1, timeout=IB_CONNECTION_TIMEOUT)
            if not self.ib.isConnected():
                raise ConnectionError("Failed to connect")

            log.info(f"Connected to IBKR as {self.user.ib_username}")
        except Exception as e:
            log.error(f"Error for user {self.user.ib_username}: {e}")

    def disconnect(self):
        try:
            if self.ib.isConnected():
                self.ib.disconnect()
                log.debug(f"Disconnected from IB Gateway for user {self.user.ib_username}")
        except Exception as e:
            log.error(f"Error during disconnection for user {self.user.ib_username}: {e}")


    async def get_account_information(self) -> dict:
        try:
            summary = await self.ib.accountSummaryAsync()
            if summary is None:
                return {}

            wanted = {
                "TotalCashValue", "CashBalance", "AccruedCash", "AvailableFunds",
                "ExcessLiquidity", "NetLiquidation", "RealizedPnL", "UnrealizedPnL",
                "GrossPositionValue", "BuyingPower"
            }
            res: dict = {}
            acct: Optional[str] = None
            for item in summary:
                if item.tag in wanted:
                    key = f"{item.tag} ({item.currency})" if item.currency else item.tag
                    res[key] = item.value
                if not acct and item.account != "All":
                    acct = item.account
            if acct:
                res["account"] = acct
            log.debug("Parsed account summary: %s", res)
            return res
        except Exception as e:
            log.error(f"Error fetching account summary for user {self.user.ib_username}: {e}")

    def get_open_positions(self) -> list[dict]:
        positions = self.ib.positions()
        out = [
            {
                "symbol": p.contract.symbol,
                "quantity": p.position,
                "avgCost": p.avgCost,
                "account": p.account,
            }
            for p in positions
        ]
        log.debug("Retrieved %d open positions", len(out))
        return out

    def place_test_aggressive_limit(self, *, user_id: int, runner_id: int) -> dict:
        try:
            symbol = random.choice(["AAPL", "NVDA", "TSLA", "PLTR"])
            contract = Stock(symbol, "SMART", "USD")

            mdm = MarketDataManager()
            if not mdm.is_market_open():
                log.warning("Market is closed, cannot place order")
                return

            price = mdm.get_current_price(symbol)
            if not price or math.isnan(price):
                log.warning("Price unavailable for %s", symbol)
                return

            lmt_px = round(price * 1.02, 2)
            self.ib.qualifyContracts(contract)
            order = LimitOrder("BUY", 1, lmt_px, tif="GTC", outsideRth=True)
            trade = self.ib.placeOrder(contract, order)

            for _ in range(50):
                if trade.order.permId:
                    break
                self.ib.sleep(0.1)

            perm_id = trade.order.permId
            status = trade.orderStatus.status

            DBManager().save_order({
                "user_id": user_id,
                "runner_id": runner_id,
                "ibkr_perm_id": perm_id,
                "symbol": symbol,
                "action": order.action,
                "order_type": order.orderType,
                "quantity": order.totalQuantity,
                "limit_price": lmt_px,
                "status": status,
                "account": trade.order.account or "",
                "filled_quantity": trade.orderStatus.filled,
                "avg_fill_price": trade.orderStatus.avgFillPrice,
            })

            log.info("Placed test limit order: %s %s @ %.2f → %s", order.action, symbol, lmt_px, status)
            return {"status": status, "ibkr_perm_id": perm_id, "limit_price": lmt_px}
        except Exception:
            log.exception("Error placing test aggressive limit order")
            return {"status": "error"}

    def sync_orders_from_ibkr(self, *, user_id: int) -> None:
        try:
            log.debug("Starting synchronization of orders for user %d", user_id)
            count = 0

            # Check if trades exist
            trades = list(self.ib.trades())  # Convert to list to log if empty
            if not trades:
                log.warning("No orders found for user %d", user_id)
            
            for tr in trades:
                log.debug("Processing trade: %s", tr)

                pid = tr.order.permId
                if not pid:
                    log.warning("Skipping trade with no permId: %s", tr)
                    continue

                order_data = {
                    "user_id": user_id,
                    "runner_id": None,
                    "ibkr_perm_id": pid,
                    "symbol": tr.contract.symbol,
                    "action": tr.order.action,
                    "order_type": tr.order.orderType,
                    "quantity": tr.order.totalQuantity,
                    "limit_price": getattr(tr.order, "lmtPrice", None),
                    "stop_price": getattr(tr.order, "auxPrice", None),
                    "status": tr.orderStatus.status,
                    "filled_quantity": tr.orderStatus.filled,
                    "avg_fill_price": tr.orderStatus.avgFillPrice,
                    "account": tr.order.account or "",
                }

                log.debug("Prepared order data: %s", order_data)

                # Sync orders to DB
                try:
                    DBManager().sync_orders([order_data])
                    log.debug("Order with permId %d synchronized successfully", pid)
                    count += 1
                except Exception as e:
                    log.error("Failed to sync order with permId %d: %s", pid, e)

            log.debug("Synchronized %d orders from IBKR for user %d", count, user_id)

        except Exception:
            log.exception("sync_orders_from_ibkr failed for user %d", user_id)


    def sync_executed_trades(self, *, user_id: int) -> None:
        try:
            log.debug("Starting synchronization of executed trades for user %d", user_id)
            count = 0

            # Check if trades exist
            trades = list(self.ib.trades())  # Convert to list to log if empty
            if not trades:
                log.warning("No trades found for user %d", user_id)

            for tr in trades:
                log.debug("Processing trade: %s", tr)

                pid = tr.order.permId
                if not pid:
                    log.warning("Skipping trade with no permId: %s", tr)
                    continue

                for f in tr.fills:
                    trade_data = {
                        "user_id": user_id,
                        "perm_id": pid,
                        "symbol": tr.contract.symbol,
                        "action": tr.order.action,
                        "order_type": tr.order.orderType,
                        "quantity": f.execution.shares,
                        "price": f.execution.price,
                        "fill_time": f.time,
                        "account": f.execution.acctNumber,
                    }

                    log.debug("Prepared executed trade data: %s", trade_data)

                    # Sync executed trades to DB
                    try:
                        DBManager().sync_executed_trades([trade_data])
                        log.debug("Executed trade with permId %d synchronized successfully", pid)
                        count += 1
                    except Exception as e:
                        log.error("Failed to sync executed trade with permId %d: %s", pid, e)

            log.debug("Synchronized %d executed trades for user %d", count, user_id)

        except Exception:
            log.exception("sync_executed_trades failed for user %d", user_id)

