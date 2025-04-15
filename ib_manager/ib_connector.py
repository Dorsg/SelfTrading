import logging
from dotenv import load_dotenv
import os
from ib_insync import IB, Position

load_dotenv()
logger = logging.getLogger(__name__)

IB_GATEWAY_HOST = os.getenv("IB_GATEWAY_HOST")
IB_GATEWAY_PORT = int(os.getenv("IB_GATEWAY_PORT", 4002))
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

    def get_account_information(self, accountId=None):
        """
        Return a dict of selected account summary tags.
        """
        try:
            summary = self.ib.accountSummary()
            result = {}
            wanted_tags = {
                'TotalCashValue', 'CashBalance', 'AccruedCash',
                'AvailableFunds', 'ExcessLiquidity', 'NetLiquidation',
                'RealizedPnL', 'UnrealizedPnL',
                'GrossPositionValue', 'BuyingPower'
            }

            account = None

            for item in summary:
                if item.tag in wanted_tags:
                    key = f"{item.tag} ({item.currency})" if item.currency else item.tag
                    result[key] = item.value

                if not account and item.account != "All":
                    account = item.account  # grab real account name once

            if account:
                result["account"] = account
            else:
                logger.warning("No specific account ID found in summary.")

            logger.info("Account summary fetched successfully")
            return result

        except Exception:
            logger.exception("Error fetching account summary")
            return {}



    def get_open_positions(self):   
        positions_data = []
        try:
            ib_positions = self.ib.positions() 
            for pos in ib_positions:
                logger.info("Position: %s", pos)
                positions_data.append({
                    'symbol': pos.contract.symbol,
                    'quantity': pos.position,
                    'avgCost': pos.avgCost,
                    'account': pos.account
                })
            logger.info("Fetched %d positions from IB", len(positions_data))
        except Exception:
            logger.exception("Error fetching positions from IB")
        return positions_data
