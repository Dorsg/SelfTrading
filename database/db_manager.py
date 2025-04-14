import logging
from datetime import datetime
from sqlalchemy.orm import Session
from database.models import (
    AccountSnapshot, Trade, Positions,
    Runner, Order
)

logger = logging.getLogger(__name__)

class DBManager:
    def __init__(self, db_session: Session):
        self.db = db_session

 