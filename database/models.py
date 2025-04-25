from datetime import datetime

from sqlalchemy import (
    Column, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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

# ─────────────────────────── Runner ────────────────────────────
class Runner(Base):
    __tablename__ = "runners"

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    name             = Column(String,  nullable=False, unique=True, index=True) 
    strategy         = Column(String,  nullable=False)
    budget           = Column(Float,   nullable=False)
    stock            = Column(String,  nullable=False)
    time_frame       = Column(Integer, nullable=False)
    stop_loss        = Column(Float,   nullable=False)
    take_profit      = Column(Float,   nullable=False)
    time_range_from  = Column(DateTime)
    time_range_to    = Column(DateTime)
    commission_ratio = Column(Float)
    exit_strategy    = Column(String,  nullable=False)
    activation       = Column(String,  default="active", nullable=False)
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow,
                               onupdate=datetime.utcnow)

    # ①  Runner → Order (1-to-many)
    orders = relationship(
        "Order",
        back_populates="runner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # ③  Runner → ExecutedTrade (via Order.perm_id) – convenience only
    trades = relationship(
        "ExecutedTrade",
        secondary="orders",
        primaryjoin="Runner.id == Order.runner_id",
        secondaryjoin="Order.ibkr_perm_id == ExecutedTrade.perm_id",
        viewonly=True,
    )

# ─────────────────────────── Order ─────────────────────────────
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    # ① FK to runner
    runner_id = Column(Integer,
                       ForeignKey("runners.id", ondelete="CASCADE"),
                       nullable=False, index=True)

    # ② permId – unique in IBKR
    ibkr_perm_id = Column(Integer, nullable=False, unique=True, index=True)

    symbol        = Column(String, nullable=False)
    action        = Column(String, nullable=False)   # BUY / SELL
    order_type    = Column(String, nullable=False)   # LIMIT / STOP …
    quantity      = Column(Float,  nullable=False)
    limit_price   = Column(Float)
    stop_price    = Column(Float)

    status            = Column(String)
    filled_quantity   = Column(Float)
    avg_fill_price    = Column(Float)

    account      = Column(String)
    created_at   = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow,
                          onupdate=datetime.utcnow)

    runner = relationship("Runner", back_populates="orders")

    # ② Order → ExecutedTrade (1-to-many)
    trades = relationship(
        "ExecutedTrade",
        primaryjoin="Order.ibkr_perm_id == ExecutedTrade.perm_id",
        viewonly=True,
    )

# ─────────────────────── Executed Trade ────────────────────────
class ExecutedTrade(Base):
    __tablename__  = "executed_trades"
    __table_args__ = (
        UniqueConstraint("perm_id", "fill_time",
                         name="uix_perm_id_fill_time"),
    )

    id        = Column(Integer, primary_key=True)

    # ② FK to orders.ibkr_perm_id
    perm_id   = Column(Integer,
                       ForeignKey("orders.ibkr_perm_id",
                                  ondelete="SET NULL"),
                       index=True)

    symbol     = Column(String)
    action     = Column(String)
    order_type = Column(String)
    quantity   = Column(Float)
    price      = Column(Float)
    fill_time  = Column(DateTime)   # tz-aware UTC
    account    = Column(String)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    ib_account_id = Column(String, nullable=True)
    ib_username   = Column(String, nullable=True)
    ib_password   = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Optional: Relationship to link user to their runners
    runners = relationship("Runner", backref="user", cascade="all, delete-orphan")