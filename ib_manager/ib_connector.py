import logging
from typing import List
from ib_insync import (
    IB, Stock, Order, MarketOrder, Trade, ExecutionFilter
)

logger = logging.getLogger(__name__)

class IBManager:
    def __init__(self, host='127.0.0.1', port=4002, client_id=15):
        self.ib = IB()
        try:
            self.ib.connect(host, port, clientId=client_id)
            logger.info("Connected to IB Gateway (host=%s, port=%d, client_id=%d)", host, port, client_id)
        except Exception:
            logger.exception("Failed to connect to IB Gateway")
            raise

    def get_market_price(self, symbol):
        contract = Stock(symbol, 'SMART', 'USD')
        self.ib.qualifyContracts(contract)
        market_data = self.ib.reqMktData(contract, "", False, False)
        self.ib.sleep(2)
        price = market_data.last or market_data.close
        return float(price) if price else None

    def place_order(self, symbol: str, quantity: int, side: str = 'BUY',
                    order_type: str = 'MKT', aux_price: float = None, limit_price: float = None):
        """
        General-purpose order placer. Supports: MKT, LMT, STP, STP LMT

        Examples:
            ib.place_order('AAPL', 1, side='BUY', order_type='MKT')
            ib.place_order('AAPL', 1, side='BUY', order_type='STP', aux_price=150.0)
            ib.place_order('AAPL', 1, side='SELL', order_type='LMT', limit_price=145.0)
            ib.place_order('AAPL', 1, side='BUY', order_type='STP LMT', aux_price=150.0, limit_price=151.0)
        """
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            self.ib.qualifyContracts(contract)

            order = Order(
                action=side,
                totalQuantity=quantity,
                orderType=order_type,
                auxPrice=aux_price,
                lmtPrice=limit_price,
                transmit=True
            )

            trade = self.ib.placeOrder(contract, order)
            self.ib.sleep(2)

            status = trade.orderStatus.status
            ib_order_id = trade.order.orderId
            perm_id = trade.order.permId
            fill_price = trade.orderStatus.avgFillPrice if status == 'Filled' else None

            logger.info(
                "%s order placed: %s x%d (%s). status=%s, ib_order_id=%d, perm_id=%s, fill_price=%s",
                order_type, symbol, quantity, side, status, ib_order_id, perm_id, fill_price
            )
            return status, ib_order_id, fill_price, perm_id
        except Exception:
            logger.exception("Error placing %s %s order for %s x%d", side, order_type, symbol, quantity)
            return None, None, None, None

    def get_all_orders_status(self):
        try:
            trades = self.ib.trades()
            return [{
                'orderId': t.order.orderId,
                'status': t.orderStatus.status,
                'fillPrice': t.orderStatus.avgFillPrice
            } for t in trades]
        except Exception:
            logger.exception("Error fetching orders status from IB")
            return []

    def fetch_all_executions(self):
        try:
            exec_filter = ExecutionFilter()
            exec_details = self.ib.reqExecutions(exec_filter)
            results = []
            for detail in exec_details:
                execution = detail.execution
                contract = detail.contract
                side = "BUY" if execution.side.upper() == "BOT" else "SELL"
                results.append({
                    'ib_order_id': execution.orderId,
                    'symbol': contract.symbol,
                    'side': side,
                    'quantity': execution.shares,
                    'price': execution.avgPrice,
                    'exec_time': execution.time
                })
            logger.info("Fetched %d executions from IB", len(results))
            return results
        except Exception:
            logger.exception("Error fetching all executions from IB")
            return []

    def fetch_all_open_orders(self):
        try:
            self.ib.reqAllOpenOrders()
            self.ib.sleep(2)
            open_trades = self.ib.openTrades()
            logger.info("Fetched %d open trades (orders) from IB", len(open_trades))
            return open_trades
        except Exception:
            logger.exception("Error fetching all open orders from IB")
            return []

    def fetch_completed_orders(self) -> List[Trade]:
        logger.info("Fetching completed orders (synchronously) from IB...")
        try:
            self.ib.reqCompletedOrders(apiOnly=False)
            self.ib.sleep(2)
            if hasattr(self.ib, 'completedOrders'):
                completed_list = self.ib.completedOrders()
                logger.info("Fetched %d completed orders from IB", len(completed_list))
                return completed_list
            else:
                logger.warning("This ib_insync build has no 'completedOrders' method. Returning [].")
                return []
        except Exception:
            logger.exception("Error fetching completed orders from IB")
            return []

    def get_positions(self):
        try:
            ib_positions = self.ib.positions()
            return [{
                'symbol': pos.contract.symbol,
                'quantity': pos.position,
                'avgCost': pos.avgCost,
                'account': pos.account
            } for pos in ib_positions]
        except Exception:
            logger.exception("Error fetching positions from IB")
            return []
