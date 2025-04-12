from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.db_core import SessionLocal
from database.db_manager import DBManager
from pydantic import BaseModel
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RunnerCreate(BaseModel):
    symbol: str
    atrategy: str
    stock_symbol: str
    strategy_name: str
    time_frame: int
    max_loss_perc: int
    take_profit_perc: int
    date_range: str
    stock_number_limit: int

@router.get("/account")
def get_account_info():
    logger.info("GET /account - Fetching account information")
    from ib_manager.ib_connector import IBManager
    ib = IBManager()
    info = ib.get_account_information()
    logger.debug("Account info fetched: %s", info)
    return info

@router.get("/runners", response_model=List[RunnerCreate])
def get_runners(db: Session = Depends(get_db)):
    logger.info("GET /runners - Fetching all runners")
    db_manager = DBManager(db)
    runners = db_manager.get_all_runners()
    logger.debug("Found %d runners", len(runners))
    return runners

@router.post("/runners")
def create_runner(runner: RunnerCreate, db: Session = Depends(get_db)):
    logger.info("POST /runners - Creating runner: %s", runner.symbol)
    db_manager = DBManager(db)
    new_runner = db_manager.create_runner(runner)
    logger.debug("Runner created with ID: %d", new_runner.id)
    return {"message": "Runner created", "id": new_runner.id}

@router.delete("/runners/{runner_id}")
def delete_runner(runner_id: int, db: Session = Depends(get_db)):
    logger.info("DELETE /runners/%d - Deleting runner", runner_id)
    db_manager = DBManager(db)
    success = db_manager.delete_runner(runner_id)
    if not success:
        logger.warning("Runner with ID %d not found", runner_id)
        raise HTTPException(status_code=404, detail="Runner not found")
    logger.debug("Runner with ID %d deleted", runner_id)
    return {"message": "Runner deleted"}
