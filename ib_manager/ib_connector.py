import logging
from ib_insync import IB, Stock, MarketOrder, Trade
logger = logging.getLogger(__name__)

class IBManager:
    def __init__(self, host='host.docker.internal', port=4002, client_id=15):
        self.ib = IB()
        try:
            self.ib.connect(host, port, clientId=client_id)
            logger.info("Connected to IB Gateway (host=%s, port=%d, client_id=%d)", host, port, client_id)
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
                'GrossPositionValue', 'EquityWithLoanValue',
                'BuyingPower', 'Cushion'
            }
            for item in summary:
                if item.tag in wanted_tags:
                    key = f"{item.tag} ({item.currency})" if item.currency else item.tag
                    result[key] = item.value

            logger.info("Account summary fetched successfully")
            return result
        except Exception:
            logger.exception("Error fetching account summary")
            return {}

    def place_market_order(self, symbol: str, quantity: int) -> str:
        """
        Place a simple market BUY order for 'symbol' with size 'quantity'.
        Returns the final status string, e.g. 'Filled' or 'Submitted'.
        """
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            order = MarketOrder('BUY', quantity)
            trade = self.ib.placeOrder(contract, order)
            self.ib.sleep(3)  # wait for fill

            status = trade.orderStatus.status
            logger.info("Order placed: %s x%d => %s", symbol, quantity, status)
            # If you want to store orderId in DB, it's 'trade.order.orderId'
            return status
        except Exception:
            logger.exception("Error placing market order for %s x%d", symbol, quantity)
            return None

    def get_all_trades(self) -> list[Trade]:
        """
        Return all trades from this session; you can match them by orderId to DB.
        """
        try:
            trades = self.ib.trades()
            return trades
        except Exception:
            logger.exception("Error fetching trades from IB")
            return []

    def get_positions(self):
        """
        Return a list of dicts with the fields you want from .positions().
        """
        positions_data = []
        try:
            ib_positions = self.ib.positions()  # returns a list of Position objects
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
