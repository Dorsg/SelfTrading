import logging
import math
import random
from dotenv import load_dotenv
import os
from ib_insync import IB, LimitOrder, MarketOrder, Stock, StopOrder

from database.db_manager import DBManager
from .market_data_manager import MarketDataManager


load_dotenv()
logger = logging.getLogger(__name__)

IB_GATEWAY_HOST = os.getenv("IB_GATEWAY_HOST")
IB_GATEWAY_PORT = int(os.getenv("IB_GATEWAY_PORT", 4002))
IB_CLIENT_ID = int(os.getenv("IB_CLIENT_ID"))

class IBManager:
    def __init__(self, client_id: int = None):
        self.ib = IB()
        client_id = client_id or int(os.getenv("IB_CLIENT_ID", 15))
        try:
            self.ib.connect(IB_GATEWAY_HOST, IB_GATEWAY_PORT, clientId=client_id)
            logger.info("Connected to IB Gateway (host=%s, port=%d, client_id=%d)", IB_GATEWAY_HOST, IB_GATEWAY_PORT, client_id)
        except Exception:
            logger.exception("Failed to connect to IB Gateway")
            raise

    def get_account_information(self, accountId=None):
        """
        Return a dict of selected account summary tags.
        """
        try:
            summary = self.ib.accountSummary()
            result = {}
            wanted_tags = {
                'TotalCashValue', 'CashBalance', 'AccruedCash',
                'AvailableFunds', 'ExcessLiquidity', 'NetLiquidation',
                'RealizedPnL', 'UnrealizedPnL',
                'GrossPositionValue', 'BuyingPower'
            }

            account = None

            for item in summary:
                if item.tag in wanted_tags:
                    key = f"{item.tag} ({item.currency})" if item.currency else item.tag
                    result[key] = item.value

                if not account and item.account != "All":
                    account = item.account  # grab real account name once

            if account:
                result["account"] = account
            else:
                logger.warning("No specific account ID found in summary.")

            logger.info("Account summary fetched successfully")
            return result

        except Exception:
            logger.exception("Error fetching account summary")
            return {}



    def get_open_positions(self):   
        positions_data = []
        try:
            ib_positions = self.ib.positions() 
            for pos in ib_positions:
                positions_data.append({
                    'symbol': pos.contract.symbol,
                    'quantity': pos.position,
                    'avgCost': pos.avgCost,
                    'account': pos.account
                })
            logger.info("Fetched %d positions from IB", len(positions_data))
        except Exception:
            logger.exception("Error fetching positions from IB")
        return positions_data
    

    def place_test_stop_order(self, runner_id: int):
            """
            Places a stop order 0.5% above the current market price for a random stock.
            Persists the order to the DB after it's been submitted.
            """
            try:
                stock_symbol = random.choice(["AAPL", "NVDA", "TSLA", "PLTR"])
                contract = Stock(stock_symbol, 'SMART', 'USD')

                # Fetch current price
                mdm = MarketDataManager()

                # Check if market is open before fetching price
                if not mdm.is_market_open():
                    logger.warning("Market is currently closed. Order will not be placed.")
                    return {"status": "market_closed"}

                current_price = mdm.get_current_price(stock_symbol)

                if not current_price or math.isnan(current_price):
                    logger.warning("Real-time price unavailable for %s", stock_symbol)
                    return {"symbol": stock_symbol, "status": "price_unavailable"}

                stop_price = round(current_price * 1.005, 2)

                # Place order
                self.ib.qualifyContracts(contract)
                order = StopOrder('BUY', 1, stop_price)
                order.tif = 'GTC'
                order.outsideRth = True
                trade = self.ib.placeOrder(contract, order)

                # Allow IB time to assign permId
                for _ in range(30):  # 30 x 0.1s = 3s timeout
                    if trade.order.permId != 0:
                        break
                    self.ib.sleep(0.1)

                status = trade.orderStatus.status
                perm_id = trade.order.permId

                logger.info("Placed stop order for %s at %.2f (status: %s, permId: %s)", stock_symbol, stop_price, status, perm_id)

                if not perm_id or perm_id == 0:
                    logger.error("IBKR returned invalid permId for %s. Order not saved.", stock_symbol)
                    return {
                        "symbol": stock_symbol,
                        "stop_price": stop_price,
                        "status": "invalid_perm_id"
                    }

                # Save order
                db = DBManager()
                try:
                    db.save_order({
                        "runner_id": runner_id,
                        "ibkr_perm_id": perm_id,
                        "symbol": stock_symbol,
                        "action": order.action,
                        "order_type": order.orderType,
                        "quantity": order.totalQuantity,
                        "stop_price": stop_price,
                        "status": status,
                        "account": trade.order.account or "",
                        "filled_quantity": trade.orderStatus.filled,
                        "avg_fill_price": trade.orderStatus.avgFillPrice,
                    })
                finally:
                    db.close()

                return {
                    "symbol": stock_symbol,
                    "stop_price": stop_price,
                    "status": status,
                    "ibkr_perm_id": perm_id
                }

            except Exception:
                logger.exception("Error placing test stop order")
                return {"status": "error"}
            
            
    def place_test_aggressive_limit(self, runner_id: int):
        """
        Places a 1‑share BUY limit order at +2 % above the current price so it
        fills immediately (even in pre/after hours).  Persists to DB.
        """
        try:
            stock_symbol = random.choice(["AAPL", "NVDA", "TSLA", "PLTR"])
            contract      = Stock(stock_symbol, "SMART", "USD")

            mdm = MarketDataManager()
            if not mdm.is_market_open():
                logger.warning("Market closed; not placing order.")
                return {"status": "market_closed"}

            price = mdm.get_current_price(stock_symbol)
            if not price or math.isnan(price):
                logger.warning("No real‑time price for %s", stock_symbol)
                return {"symbol": stock_symbol, "status": "price_unavailable"}

            # ─── aggressive limit: 2 % above last price ──
            limit_px = round(price * 1.02, 2)

            self.ib.qualifyContracts(contract)
            order              = LimitOrder("BUY", 1, limit_px)
            order.outsideRth   = True          # <‑‑ key flag
            order.tif          = "GTC"         
            trade              = self.ib.placeOrder(contract, order)
            # ──────────────────────────────────────────────

            # wait up to 5 s for permId
            for _ in range(50):
                if trade.order.permId:
                    break
                self.ib.sleep(0.1)

            perm_id = trade.order.permId
            status  = trade.orderStatus.status
            logger.info("Placed BUY LMT %s at %.2f (status=%s, permId=%s)",
                        stock_symbol, limit_px, status, perm_id)

            if not perm_id:
                logger.error("Invalid permId – order not saved.")
                return {"symbol": stock_symbol, "status": "invalid_perm_id"}

            # ---- persist in DB ----
            db = DBManager()
            try:
                db.save_order({
                    "runner_id":       runner_id,
                    "ibkr_perm_id":    perm_id,
                    "symbol":          stock_symbol,
                    "action":          order.action,
                    "order_type":      order.orderType,   # 'LMT'
                    "quantity":        order.totalQuantity,
                    "limit_price":     limit_px,
                    "stop_price":      None,
                    "status":          status,
                    "account":         trade.order.account or "",
                    "filled_quantity": trade.orderStatus.filled,
                    "avg_fill_price":  trade.orderStatus.avgFillPrice,
                })
            finally:
                db.close()

            return {
                "symbol":       stock_symbol,
                "limit_price":  limit_px,
                "status":       status,
                "ibkr_perm_id": perm_id,
            }

        except Exception:
            logger.exception("Error placing aggressive limit order")
            return {"status": "error"}
               
    def sync_orders_from_ibkr(self):
        """
        Fetch all open trades from IBKR and sync with database.
        """
        try:
            open_trades = self.ib.trades()
            order_data_list = []
            if not open_trades: 
                logger.warning("No orders found in IBKR.")
                return

            for trade in open_trades:
                perm_id = trade.order.permId
                if not perm_id or perm_id == 0:
                    logger.warning("Skipping order with missing permId")
                    continue

                order_data = {
                    "runner_id": 123,  # Placeholder; update if runner_id is known
                    "ibkr_perm_id": perm_id,
                    "symbol": trade.contract.symbol,
                    "action": trade.order.action,
                    "order_type": trade.order.orderType,
                    "quantity": trade.order.totalQuantity,
                    "limit_price": getattr(trade.order, 'lmtPrice', None),
                    "stop_price": getattr(trade.order, 'auxPrice', None),
                    "status": trade.orderStatus.status,
                    "filled_quantity": trade.orderStatus.filled,
                    "avg_fill_price": trade.orderStatus.avgFillPrice,
                    "account": trade.order.account or "",
                }

                order_data_list.append(order_data)

            db = DBManager()
            db.sync_orders(order_data_list)
        except Exception:
            logger.exception("Failed to sync IBKR orders to DB.")

    def sync_executed_trades(self):
        """
        Extracts all fills from current trades and stores them in the executed_trades table.
        """
        try:
            trades = self.ib.trades()
            executed_trades = []
            if not trades:
                logger.warning("No trades found in IBKR.")
                return
            for trade in trades:
                for fill in trade.fills:
                    executed_trades.append({
                        "perm_id": trade.order.permId,
                        "symbol": trade.contract.symbol,
                        "action": trade.order.action,
                        "order_type": trade.order.orderType,
                        "quantity": fill.execution.shares,
                        "price": fill.execution.price,
                        "fill_time": fill.time,
                        "account": fill.execution.acctNumber,
                    })

            if executed_trades:
                db = DBManager()
                db.save_executed_trades(executed_trades)
                db.close()
        except Exception:
            logger.exception("Failed to sync executed trades.")