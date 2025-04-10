from ib_insync import IB, Stock, MarketOrder

class IBManager:
    def __init__(self, host='127.0.0.1', port=4002, client_id=15):
        self.ib = IB()
        try:
            self.ib.connect(host, port, clientId=client_id)
            print("✅ Connected to IB Gateway")
        except Exception as e:
            print(f"❌ Failed to connect to IB Gateway: {e}")
            raise



    def get_account_information(self, accountId=None):
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

        return result

    def place_market_order(self, symbol: str, quantity: int) -> str:
        try:
            contract = Stock(symbol, 'SMART', 'USD')
            order = MarketOrder('BUY', quantity)
            trade = self.ib.placeOrder(contract, order)
            self.ib.sleep(3)  # wait for order execution

            status = trade.orderStatus.status
            print(f"📤 Order placed: {symbol} x{quantity} => {status}")
            return status
        except Exception as e:
            print(f"❌ Error placing market order: {e}")
            return None