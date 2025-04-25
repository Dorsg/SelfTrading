# api_gateway/routes/runner_routes.py
from fastapi import APIRouter, HTTPException, Path, Query
from sqlalchemy.inspection import inspect as sqla_inspect

from database.db_manager import DBManager
from api_gateway.routes.schemas.runner import RunnerCreate, RunnerIds

import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ───────────────────────── helpers ──────────────────────────
def to_dict(obj):
    """Convert any SQLAlchemy model instance to a plain-python dict."""
    return {c.key: getattr(obj, c.key)
            for c in sqla_inspect(obj).mapper.column_attrs}


# ───────────────────────── Account info ──────────────────────────
@router.get("/account/snapshot")
def get_account_snapshot():
    """
    Return today's snapshot; create one on-the-fly if missing.
    """
    with DBManager() as db:
        try:
            snap = db.get_today_snapshot()
            if snap:
                return to_dict(snap)

            from ib_manager.ib_connector import IBManager  # local import avoids cycle
            ib   = IBManager()
            data = ib.get_account_information()
            if not data:
                raise HTTPException(500, "Failed to fetch data from IB")

            snap = db.create_account_snapshot(data)
            if not snap:
                raise HTTPException(500, "Failed to store snapshot")
            return to_dict(snap)
        except HTTPException:
            raise
        except Exception:
            logger.exception("Error in /account/snapshot")
            raise HTTPException(500, "Internal server error")


@router.get("/account/positions")
def get_open_positions():
    with DBManager() as db:
        try:
            return [to_dict(p) for p in db.get_open_positions()]
        except Exception:
            logger.exception("Failed to retrieve open positions")
            raise HTTPException(500, "Failed to retrieve positions")


# ───────────────────────── Global orders / trades ─────────────────
@router.get("/orders")
def get_all_orders():
    with DBManager() as db:
        try:
            orders = db.get_all_orders()
            return [to_dict(o) for o in orders]
        except Exception:
            logger.exception("Failed to retrieve orders")
            raise HTTPException(500, "Failed to retrieve orders")


@router.get("/executed-trades")
def get_all_executed_trades():
    with DBManager() as db:
        try:
            trades = db.get_all_executed_trades()
            return [to_dict(t) for t in trades]
        except Exception:
            logger.exception("Failed to retrieve executed trades")
            raise HTTPException(500, "Failed to retrieve executed trades")


# ─────────────────────────── Runners CRUD ─────────────────────────
    
@router.post("/runners", status_code=201)
def create_runner(runner: RunnerCreate):
    with DBManager() as db:
        try:
            obj = db.create_runner(runner.model_dump(exclude={"id", "created_at"}))
            if not obj:
                raise HTTPException(500, "Failed to create runner")
            return to_dict(obj)
        except HTTPException:
            raise
        except Exception:
            logger.exception("Error creating runner")
            raise HTTPException(500, "Internal server error")


@router.delete("/runners")
def delete_runners(payload: RunnerIds):
    with DBManager() as db:
        try:
            deleted = db.delete_runners(payload.ids)
            return {"deleted": deleted}
        except Exception:
            logger.exception("Error deleting runners")
            raise HTTPException(500, "Internal server error")


@router.post("/runners/activate")
def activate_runners(payload: RunnerIds):
    with DBManager() as db:
        try:
            updated = db.update_runners_activation(payload.ids, "active")
            return {"updated": updated}
        except Exception:
            logger.exception("Error activating runners")
            raise HTTPException(500, "Internal server error")


@router.post("/runners/deactivate")
def deactivate_runners(payload: RunnerIds):
    with DBManager() as db:
        try:
            updated = db.update_runners_activation(payload.ids, "inactive")
            return {"updated": updated}
        except Exception:
            logger.exception("Error deactivating runners")
            raise HTTPException(500, "Internal server error")


# ───────────────────── Runner-scoped data helpers ──────────────────
@router.get("/runners/{runner_id}/orders")
def get_runner_orders(runner_id: int = Path(..., gt=0)):
    with DBManager() as db:
        try:
            orders = db.get_runner_orders(runner_id)
            return [to_dict(o) for o in orders]
        except Exception:
            logger.exception("Failed to retrieve runner orders")
            raise HTTPException(500, "Failed to retrieve orders")


@router.get("/runners/{runner_id}/trades")
def get_runner_trades(runner_id: int = Path(..., gt=0)):
    with DBManager() as db:
        try:
            trades = db.get_runner_trades(runner_id)
            return [to_dict(t) for t in trades]
        except Exception:
            logger.exception("Failed to retrieve runner trades")
            raise HTTPException(500, "Failed to retrieve trades")


@router.get("/runners/active")
def get_active_runners():
    with DBManager() as db:
        try:
            runners = db.get_active_runners()
            return [to_dict(r) for r in runners]
        except Exception:
            logger.exception("Failed to retrieve active runners")
            raise HTTPException(500, "Failed to retrieve active runners")
