from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from strategy_engine.db.database import SessionLocal
from strategy_engine.db.models import Runner
from api_gateway.schemas.runner import RunnerCreate, RunnerResponse
from typing import List

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/runners", response_model=RunnerResponse)
def create_runner(runner: RunnerCreate, db: Session = Depends(get_db)):
    db_runner = Runner(**runner.dict())
    db.add(db_runner)
    db.commit()
    db.refresh(db_runner)
    return db_runner

@router.get("/runners", response_model=List[RunnerResponse])
def get_all_runners(db: Session = Depends(get_db)):
    return db.query(Runner).all()
