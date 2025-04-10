import time
from ib_insync import IB, Stock, MarketOrder
from strategy_engine.db.database import SessionLocal
from strategy_engine.db.models import TradeLog
from sqlalchemy.orm import Session

class StrategyManager:
    def __init__(self):
        self.ib = IB()
        self.ib.connect('127.0.0.1', 4002, clientId=1)  # paper account
        print("Connected to IB Gateway")

    def run(self):
        # Get account summary
        summary = self.ib.accountSummary()

        # Tags to extract
        cash_tags = {
            'TotalCashValue',
            'CashBalance',
            'AccruedCash',
            'AvailableFunds',
            'ExcessLiquidity',
            'NetLiquidation'
        }

        pnl_tags = {
          'RealizedPnL',
          'UnrealizedPnL',
        }

        performance_tags = {
         'GrossPositionValue',
         'EquityWithLoanValue',
         'BuyingPower',
          'Cushion'
        }

        # Combine all tags
        wanted_tags = cash_tags | pnl_tags | performance_tags

        # Extract and display
        print("\n🟢 Account Snapshot:\n")

        for item in summary:
            if item.tag in wanted_tags:
                label = f"{item.tag} ({item.currency})" if item.currency else item.tag
                print(f"{label}: {item.value}")
        #while True:
         #   try:
          #      self.execute_trade()
           # except Exception as e:
            #    print(f"Error: {e}")
            #time.sleep(300)  # every 5 minutes

    def execute_trade(self):
        contract = Stock('AAPL', 'SMART', 'USD')
        order = MarketOrder('BUY', 1)

        trade = self.ib.placeOrder(contract, order)
        self.ib.sleep(3)

        status = trade.orderStatus.status
        print(f"Placed order: {status}")

        self.log_trade('AAPL', 1, status)

    def log_trade(self, symbol: str, qty: int, status: str):
        db: Session = SessionLocal()
        try:
            log = TradeLog(symbol=symbol, quantity=qty, status=status)
            db.add(log)
            db.commit()
        finally:
            db.close()
