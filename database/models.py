from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# ----- Account Snapshot -----
class AccountSnapshot(Base):
    __tablename__ = 'account_snapshots'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    account = Column(String, nullable=False)
    total_cash_value = Column(Float)
    net_liquidation = Column(Float)
    available_funds = Column(Float)
    buying_power = Column(Float)
    unrealized_pnl = Column(Float)
    realized_pnl = Column(Float)
    excess_liquidity = Column(Float)
    gross_position_value = Column(Float)

# ----- Open Positions -----
class OpenPosition(Base):
    __tablename__ = 'open_positions'

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)
    account = Column(String, nullable=False)
    last_update = Column(DateTime, default=datetime.utcnow)

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    runner_id = Column(Integer, nullable=False, index=True)
    ibkr_perm_id = Column(Integer, nullable=False, unique=True, index=True)

    symbol = Column(String, nullable=False)
    action = Column(String, nullable=False)  # e.g. 'BUY' or 'SELL'
    order_type = Column(String, nullable=False)  # e.g. 'LIMIT', 'STOP', etc.
    quantity = Column(Float, nullable=False)
    limit_price = Column(Float, nullable=True)
    stop_price = Column(Float, nullable=True)

    status = Column(String, nullable=True)  # e.g. 'Submitted', 'Filled', etc.
    filled_quantity = Column(Float, nullable=True)
    avg_fill_price = Column(Float, nullable=True)

    account = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ExecutedTrade(Base):
    __tablename__ = "executed_trades"
    __table_args__ = (
        UniqueConstraint("perm_id", "fill_time", name="uix_perm_id_fill_time"),
    )

    id         = Column(Integer, primary_key=True)
    perm_id    = Column(Integer, index=True)          # same as order.permId
    symbol     = Column(String)
    action     = Column(String)
    order_type = Column(String)
    quantity   = Column(Float)
    price      = Column(Float)
    fill_time  = Column(DateTime)                     # IBKR gives UTC tz‑aware dt
    account    = Column(String)
