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