import time
from ib_insync import IB, Stock, MarketOrder
from database.database import SessionLocal
from sqlalchemy.orm import Session

class StrategyManager:
    def should_make_the_order():
        return True

