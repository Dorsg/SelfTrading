from __future__ import annotations
import socket
from starlette.status import HTTP_200_OK
import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path
from starlette.status import HTTP_504_GATEWAY_TIMEOUT

from api_gateway.security.auth import get_current_user, User
from api_gateway.routes.schemas.runner import RunnerCreate, RunnerIds
from database.db_manager import DBManager
from sqlalchemy.inspection import inspect as sqla_inspect

logger = logging.getLogger(__name__)
router = APIRouter()


# ───────────────── helpers ──────────────────────────────────────────
def to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in sqla_inspect(obj).mapper.column_attrs}


def _log_call(name: str, *, user: User, extra: str | None = None) -> None:
    logger.info(
        "%s user=%s id=%s %s",
        name.ljust(22),
        user.username,
        user.id,
        extra or "",
    )


# ───────────────── account info ─────────────────────────────────────
@router.get("/account/snapshot")
def get_account_snapshot(current: User = Depends(get_current_user)):
    """
    Return today’s account snapshot if we already stored one;
    otherwise pull it via the user’s dedicated IB-Gateway container
    (`ib-gateway-<user-id>` on port 4004) and persist it.
    """
    _log_call("GET /snapshot", user=current)

    with DBManager() as db:
        try:
            snap = db.get_today_snapshot(user_id=current.id)
            if snap is not None:
                logger.debug("snapshot cached → rows=#1")
                return to_dict(snap)

            # pull live from gateway
            from ib_manager.ib_connector import IBManager

            gateway_host = f"ib-gateway-{current.id}"
            logger.info(
                "connecting IB gateway host=%s port=%s cid=%s",
                gateway_host,
                4004,
                100 + current.id,
            )
            ib = IBManager(
                host=gateway_host,
                port=4004,
                client_id=100 + current.id,
            )

            data = ib.get_account_information()
            ib.disconnect()
            logger.debug("ib.get_account_information returned keys=%d", len(data))

            if not data:
                raise HTTPException(500, "Failed to fetch data from IB")

            snap = db.create_account_snapshot(user_id=current.id, snapshot_data=data)
            if not snap:
                raise HTTPException(500, "Failed to store snapshot")

            logger.info("snapshot persisted id=%s", snap.id)
            return to_dict(snap)

        except RuntimeError as e:  # raised by IBManager after all retries
            logger.warning("gateway not ready for user=%s: %s", current.id, e)
            raise HTTPException(
                status_code=HTTP_504_GATEWAY_TIMEOUT,
                detail="IB-Gateway not ready, please retry in a minute.",
            )
        except HTTPException:
            raise
        except Exception:
            logger.exception("unhandled error in /account/snapshot")
            raise HTTPException(500, "Internal server error")


@router.get("/account/positions")
def get_open_positions(current: User = Depends(get_current_user)):
    _log_call("GET /positions", user=current)
    with DBManager() as db:
        rows = [to_dict(p) for p in db.get_open_positions(user_id=current.id)]
        logger.debug("positions rows=%d", len(rows))
        return rows


# ───────────────── orders & trades ────────────────────────────────
@router.get("/orders")
def get_all_orders(current: User = Depends(get_current_user)):
    _log_call("GET /orders", user=current)
    with DBManager() as db:
        rows = [to_dict(o) for o in db.get_all_orders(user_id=current.id)]
        logger.debug("orders rows=%d", len(rows))
        return rows


@router.get("/executed-trades")
def get_all_executed_trades(current: User = Depends(get_current_user)):
    _log_call("GET /trades", user=current)
    with DBManager() as db:
        rows = [to_dict(t) for t in db.get_all_executed_trades(user_id=current.id)]
        logger.debug("trades rows=%d", len(rows))
        return rows


# ───────────────── runners CRUD ───────────────────────────────────
@router.post("/runners", status_code=201)
def create_runner(
    runner: RunnerCreate, current: User = Depends(get_current_user)
):
    _log_call("POST /runners", user=current, extra=f"name={runner.name!r}")
    with DBManager() as db:
        obj = db.create_runner(
            user_id=current.id, data=runner.model_dump(exclude={"id", "created_at"})
        )
        return to_dict(obj)


@router.delete("/runners")
def delete_runners(payload: RunnerIds, current: User = Depends(get_current_user)):
    _log_call("DEL /runners", user=current, extra=f"ids={payload.ids}")
    with DBManager() as db:
        deleted = db.delete_runners(user_id=current.id, ids=payload.ids)
        logger.info("deleted runners=%d", deleted)
        return {"deleted": deleted}


@router.post("/runners/activate")
def activate_runners(payload: RunnerIds, current: User = Depends(get_current_user)):
    _log_call("ACT /runners", user=current, extra=f"ids={payload.ids}")
    with DBManager() as db:
        updated = db.update_runners_activation(
            user_id=current.id, ids=payload.ids, activation="active"
        )
        logger.info("activated runners=%d", updated)
        return {"updated": updated}


@router.post("/runners/deactivate")
def deactivate_runners(payload: RunnerIds, current: User = Depends(get_current_user)):
    _log_call("DEACT /runners", user=current, extra=f"ids={payload.ids}")
    with DBManager() as db:
        updated = db.update_runners_activation(
            user_id=current.id, ids=payload.ids, activation="inactive"
        )
        logger.info("deactivated runners=%d", updated)
        return {"updated": updated}


# ───────── runner-scoped helpers ────────────────────────────────
@router.get("/runners/{runner_id}/orders")
def get_runner_orders(
    runner_id: int = Path(..., gt=0), current: User = Depends(get_current_user)
):
    _log_call("RUNNER orders", user=current, extra=f"rid={runner_id}")
    with DBManager() as db:
        rows = [
            to_dict(o) for o in db.get_runner_orders(user_id=current.id, runner_id=runner_id)
        ]
        logger.debug("runner orders rows=%d", len(rows))
        return rows


@router.get("/runners/{runner_id}/trades")
def get_runner_trades(
    runner_id: int = Path(..., gt=0), current: User = Depends(get_current_user)
):
    _log_call("RUNNER trades", user=current, extra=f"rid={runner_id}")
    with DBManager() as db:
        rows = [
            to_dict(t) for t in db.get_runner_trades(user_id=current.id, runner_id=runner_id)
        ]
        logger.debug("runner trades rows=%d", len(rows))
        return rows


@router.get("/runners/active")
def get_active_runners(current: User = Depends(get_current_user)):
    _log_call("GET /runners/active", user=current)
    with DBManager() as db:
        rows = [to_dict(r) for r in db.get_active_runners(user_id=current.id)]
        logger.debug("active runners rows=%d", len(rows))
        return rows

@router.get("/ib/status", status_code=HTTP_200_OK)
def ib_connection_status(current: User = Depends(get_current_user)):
    """
    Quick-probe the user’s IB-Gateway container (ib-gateway-<uid>:4004).

    Returns:
        {"connected": true}   when TCP-4004 opens within 2 s
        {"connected": false}  otherwise
    """
    _log_call("GET /ib/status", user=current)

    host = f"ib-gateway-{current.id}"
    port = 4004
    try:
        with socket.create_connection((host, port), 2):
            return {"connected": True}
    except OSError:
        return {"connected": False}