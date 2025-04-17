from fastapi import APIRouter, HTTPException
from database.db_manager import DBManager
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/account/snapshot")
def get_account_snapshot():
    """
    Retrieves today's account snapshot from the database.
    If it does not exist, it fetches account information from IB,
    creates the snapshot in the database, and returns the stored data.
    """
    dbm = DBManager()
    try:
        snapshot = dbm.get_today_snapshot()

        if snapshot:
            return snapshot

        from ib_manager.ib_connector import IBManager
        ib = IBManager()
        data = ib.get_account_information()

        if not data:
            raise HTTPException(status_code=500, detail="Failed to fetch data from IB")

        snapshot = dbm.create_account_snapshot(data)
        if not snapshot:
            raise HTTPException(status_code=500, detail="Failed to store snapshot")

        return snapshot

    except Exception:
        logger.exception("Error in /account/snapshot")
        raise HTTPException(status_code=500, detail="Internal server error")



@router.get("/account/positions")
def get_open_positions():
    """
    Retrieves the currently open positions from the database.
    """
    dbm = DBManager()
    try:
        positions = dbm.get_open_positions()
        return positions

    except Exception:
        logger.exception("Failed to retrieve open positions")
        raise HTTPException(status_code=500, detail="Failed to retrieve positions")

