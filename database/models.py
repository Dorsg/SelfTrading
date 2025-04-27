# database/models.py
from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# ───────────────────────────── Users ─────────────────────────────
class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String, unique=True, nullable=False, index=True)
    username        = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)

    # optional IB creds (NULL → read-only / paper user)
    ib_account_id = Column(String)
    ib_username   = Column(String)
    ib_password   = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    runners = relationship(
        "Runner", back_populates="user", cascade="all, delete-orphan"
    )

# ───────────────────── Account snapshots ─────────────────────
class AccountSnapshot(Base):
    __tablename__ = "account_snapshots"

    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp = Column(DateTime, default=datetime.utcnow)
    account   = Column(String, nullable=False)

    total_cash_value     = Column(Float)
    net_liquidation      = Column(Float)
    available_funds      = Column(Float)
    buying_power         = Column(Float)
    unrealized_pnl       = Column(Float)
    realized_pnl         = Column(Float)
    excess_liquidity     = Column(Float)
    gross_position_value = Column(Float)

# ─────────────────────── Open positions ───────────────────────
class OpenPosition(Base):
    __tablename__ = "open_positions"

    id      = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    symbol      = Column(String, nullable=False)
    quantity    = Column(Float, nullable=False)
    avg_price   = Column(Float, nullable=False)
    account     = Column(String, nullable=False)
    last_update = Column(DateTime, default=datetime.utcnow)

# ─────────────────────────── Runner ────────────────────────────
class Runner(Base):
    __tablename__  = "runners"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uix_user_runner_name"),
    )

    id      = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name             = Column(String, nullable=False, index=True)
    strategy         = Column(String, nullable=False)
    budget           = Column(Float,  nullable=False)
    stock            = Column(String, nullable=False)
    time_frame       = Column(Integer, nullable=False)
    stop_loss        = Column(Float,   nullable=False)
    take_profit      = Column(Float,   nullable=False)
    time_range_from  = Column(DateTime)
    time_range_to    = Column(DateTime)
    commission_ratio = Column(Float)
    exit_strategy    = Column(String,  nullable=False)
    activation       = Column(String,  default="active", nullable=False)
    created_at       = Column(DateTime, default=datetime.utcnow)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user   = relationship("User", back_populates="runners")
    orders = relationship(
        "Order",
        back_populates="runner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

# ─────────────────────────── Order ────────────────────────────
class Order(Base):
    __tablename__ = "orders"

    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    runner_id = Column(
        Integer, ForeignKey("runners.id", ondelete="CASCADE"), nullable=False, index=True
    )

    ibkr_perm_id = Column(Integer, nullable=False, unique=True, index=True)

    symbol      = Column(String, nullable=False)
    action      = Column(String, nullable=False)
    order_type  = Column(String, nullable=False)
    quantity    = Column(Float,  nullable=False)
    limit_price = Column(Float)
    stop_price  = Column(Float)

    status          = Column(String)
    filled_quantity = Column(Float)
    avg_fill_price  = Column(Float)

    account      = Column(String)
    created_at   = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    runner = relationship("Runner", back_populates="orders")
    trades = relationship(
        "ExecutedTrade",
        primaryjoin="Order.ibkr_perm_id == ExecutedTrade.perm_id",
        viewonly=True,
    )

# ─────────────────────── Executed trade ───────────────────────
class ExecutedTrade(Base):
    __tablename__  = "executed_trades"
    __table_args__ = (
        UniqueConstraint("perm_id", "fill_time", name="uix_perm_id_fill_time"),
    )

    id      = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    perm_id = Column(
        Integer, ForeignKey("orders.ibkr_perm_id", ondelete="SET NULL"), index=True
    )

    symbol     = Column(String)
    action     = Column(String)
    order_type = Column(String)
    quantity   = Column(Float)
    price      = Column(Float)
    fill_time  = Column(DateTime)
    account    = Column(String)
