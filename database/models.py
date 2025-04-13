from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# ----- Account Snapshot -----
class AccountSnapshot(Base):
    __tablename__ = 'account_snapshots'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_cash_value = Column(Float)
    net_liquidation = Column(Float)
    available_funds = Column(Float)
    buying_power = Column(Float)
    unrealized_pnl = Column(Float)
    realized_pnl = Column(Float)
    equity_with_loan_value = Column(Float)
    excess_liquidity = Column(Float)
    gross_position_value = Column(Float)
    cushion = Column(Float)

# ----- Strategy -----
class Strategy(Base):
    __tablename__ = 'strategies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    symbol = Column(String, index=True)
    is_active = Column(Boolean, default=True)

# ----- Runner -----
class Runner(Base):
    __tablename__ = 'runners'

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    atrategy = Column(String, nullable=False)
    stock_symbol = Column(String, nullable=False)
    strategy_name = Column(String, nullable=False)
    time_frame = Column(Integer, nullable=False)
    max_loss_perc = Column(Integer, nullable=False)
    take_profit_perc = Column(Integer, nullable=False)
    date_range = Column(String, nullable=False)
    stock_number_limit = Column(Integer, nullable=False)

# ----- Orders -----
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    runner_id = Column(Integer, ForeignKey('runners.id'), nullable=True)
    ib_order_id = Column(Integer, nullable=False, unique=True)
    perm_id = Column(Integer, nullable=True)  # <-- NEW COLUMN for IB's permanent ID

    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    side = Column(String, nullable=False)    # 'BUY'/'SELL'
    status = Column(String, nullable=False, default='Open')  # 'Open', 'Filled', 'Cancelled', etc.
    filled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    runner = relationship("Runner", backref="orders")

# ----- Trades -----
class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # references
    runner_id = Column(Integer, ForeignKey('runners.id'), nullable=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=True)

    # store IB order ID to match with historical fetch (reqExecutions)
    ib_order_id = Column(Integer, nullable=True)

    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # 'BUY'/'SELL'
    quantity = Column(Integer, nullable=False)

    buy_price = Column(Float, nullable=True)
    sell_price = Column(Float, nullable=True)
    profit_loss = Column(Float, nullable=True, default=0.0)

    runner = relationship("Runner", backref="trades")
    order = relationship("Order", backref="trade")

# ----- Positions -----
class Positions(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    avg_cost = Column(Float, nullable=False)
    account = Column(String, nullable=False)
    is_open = Column(Boolean, default=True)
    last_update = Column(DateTime, default=datetime.utcnow)
