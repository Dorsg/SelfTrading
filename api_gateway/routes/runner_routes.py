from fastapi import APIRouter, Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database.db_core import SessionLocal
from database.db_manager import DBManager
import logging



logger = logging.getLogger(__name__)
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/account/snapshot")
def get_account_snapshot(db: Session = Depends(get_db)):
    """
    Retrieves today's account snapshot from the database.
    If it does not exist, it fetches account information from IB,
    creates the snapshot in the database, and returns the stored data.
    """
    dbm = DBManager(db)
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