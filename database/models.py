from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
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

# ----- Trade Log -----
class TradeLog(Base):
    __tablename__ = 'trade_logs'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    side = Column(String, nullable=False)
    status = Column(String, nullable=False)
    order_id = Column(Integer, nullable=True)
    strategy_name = Column(String, nullable=True)
    is_open = Column(Boolean, default=True)  # track open vs closed trades

# ----- Positions -----
class Positions(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    avg_cost = Column(Float, nullable=False)
    account = Column(String, nullable=False)
    last_update = Column(DateTime, default=datetime.utcnow)
