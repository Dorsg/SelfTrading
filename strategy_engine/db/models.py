from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Strategy(Base):
    __tablename__ = 'strategies'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    symbol = Column(String, index=True)
    is_active = Column(Boolean, default=True)

class TradeLog(Base):
    __tablename__ = 'trade_logs'

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

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
    
