import logging
from dotenv import load_dotenv
import os
from typing import List
from ib_insync import (
    IB, Stock, Order, MarketOrder, Trade, ExecutionFilter
)

load_dotenv() 
logger = logging.getLogger(__name__)

IB_GATEWAY_HOST = os.getenv("IB_GATEWAY_HOST")
IB_GATEWAY_PORT = int(os.getenv("IB_GATEWAY_PORT", 4002)) ## 4002 for paper (demo) account
IB_CLIENT_ID = int(os.getenv("IB_CLIENT_ID"))

class IBManager:
    def __init__(self):
        self.ib = IB()
     
        try:
            self.ib.connect(IB_GATEWAY_HOST, IB_GATEWAY_PORT, clientId=IB_CLIENT_ID)
            logger.info("Connected to IB Gateway (host=%s, port=%d, client_id=%d)", IB_GATEWAY_HOST, IB_GATEWAY_PORT, IB_CLIENT_ID)
        except Exception:
            logger.exception("Failed to connect to IB Gateway")
            raise
