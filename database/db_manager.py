# database/db_manager.py
from __future__ import annotations

import logging
from datetime import date, datetime
from sqlite3 import IntegrityError
from typing import List, Sequence

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from api_gateway.security.auth import hash_password, verify_password
from database.db_core import SessionLocal
from database.models import (
    AccountSnapshot,
    ExecutedTrade,
    OpenPosition,
    Order,
    Runner,
    User,
)

logger = logging.getLogger(__name__)


class DBManager:
    """
    Thin wrapper around a SQLAlchemy session (+ context-manager sugar).
    All public methods take an explicit `user_id` where relevant.
    """

    # ───────────────────── lifecycle ─────────────────────
    def __init__(self, db_session: Session | None = None) -> None:
        self._own_session = db_session is None
        self.db: Session = db_session or SessionLocal()

    # context-manager
    def __enter__(self) -> "DBManager":
        return self

    def __exit__(self, exc_t, exc_v, tb) -> None:
        try:
            if exc_t:
                self.db.rollback()
            else:
                self.db.commit()
        finally:
            self.close()

    def close(self) -> None:
        if self._own_session:
            self.db.close()

    # ------------------------------------------------------------------
    def _commit(self, msg: str) -> bool:
        try:
            self.db.commit()
            logger.info("%s – OK", msg)
            return True
        except Exception:
            logger.exception("%s – FAILED", msg)
            self.db.rollback()
            return False

    # ───────────────────── users ─────────────────────
    def get_user_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_users_with_ib(self) -> Sequence[User]:
        return (
            self.db.query(User)
            .filter(User.ib_username.isnot(None), User.ib_password.isnot(None))
            .all()
        )

    def create_user(self, *, username: str, email: str, password: str, ib_username: str | None = None, ib_password: str | None = None,) -> User:
        if self.get_user_by_username(username) or self.get_user_by_email(email):
            raise ValueError("Username or e-mail already taken")

        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            ib_username=ib_username,
            ib_password=ib_password,
        )
        self.db.add(user)
        self._commit("Create user")
        return user

    def authenticate(self, *, username: str, password: str) -> User | None:
        user = self.get_user_by_username(username)
        if user and verify_password(password, user.hashed_password):
            return user
        return None

    # ─────────────────── account snapshots ───────────────────
    def get_today_snapshot(self, user_id: int) -> AccountSnapshot | None:
        return (
            self.db.query(AccountSnapshot)
            .filter(
                AccountSnapshot.user_id == user_id,
                func.date(AccountSnapshot.timestamp) == date.today(),
            )
            .first()
        )

    def create_account_snapshot(
        self, *, user_id: int, snapshot_data: dict
    ) -> AccountSnapshot | None:
        snap = AccountSnapshot(
            user_id=user_id,
            timestamp=datetime.utcnow(),
            total_cash_value=snapshot_data.get("TotalCashValue (USD)"),
            net_liquidation=snapshot_data.get("NetLiquidation (USD)"),
            available_funds=snapshot_data.get("AvailableFunds (USD)"),
            buying_power=snapshot_data.get("BuyingPower (USD)"),
            unrealized_pnl=snapshot_data.get("UnrealizedPnL (USD)"),
            realized_pnl=snapshot_data.get("RealizedPnL (USD)"),
            excess_liquidity=snapshot_data.get("ExcessLiquidity (USD)"),
            gross_position_value=snapshot_data.get("GrossPositionValue (USD)"),
            account=snapshot_data.get("account"),
        )
        self.db.add(snap)
        return snap if self._commit("Insert snapshot") else None

    # ─────────────────── open positions ───────────────────
    def update_open_positions(self, *, user_id: int, positions: list[dict]) -> None:
        self.db.query(OpenPosition).filter(OpenPosition.user_id == user_id).delete()
        self.db.bulk_save_objects(
            OpenPosition(
                user_id=user_id,
                symbol=p["symbol"],
                quantity=p["quantity"],
                avg_price=p["avgCost"],
                account=p["account"],
            )
            for p in positions
        )
        self._commit("Update open positions")

    def get_open_positions(self, *, user_id: int) -> Sequence[OpenPosition]:
        return self.db.query(OpenPosition).filter(OpenPosition.user_id == user_id).all()

    # ─────────────────── runners ───────────────────
    def create_runner(self, *, user_id: int, data: dict) -> Runner:
        runner = Runner(user_id=user_id, **data)
        self.db.add(runner)
        try:
            self.db.commit()
            logger.info("Create runner – OK")
            return runner
        except IntegrityError:
            self.db.rollback()
            raise ValueError("Runner name already exists")
        except Exception:
            self.db.rollback()
            logger.exception("Create runner – FAILED")
            raise

    def delete_runners(self, *, user_id: int, ids: List[int]) -> int:
        rows = (
            self.db.query(Runner)
            .filter(Runner.user_id == user_id, Runner.id.in_(ids))
            .delete(synchronize_session=False)
        )
        self._commit(f"Delete {rows} runner(s)")
        return rows

    def update_runners_activation(
        self, *, user_id: int, ids: List[int], activation: str
    ) -> int:
        rows = (
            self.db.query(Runner)
            .filter(Runner.user_id == user_id, Runner.id.in_(ids))
            .update(
                {"activation": activation, "updated_at": datetime.utcnow()},
                synchronize_session=False,
            )
        )
        self._commit(f"{activation.capitalize()} {rows} runner(s)")
        return rows

    def get_active_runners(self, *, user_id: int) -> Sequence[Runner]:
        return (
            self.db.query(Runner)
            .filter(Runner.user_id == user_id, Runner.activation == "active")
            .all()
        )

    # ─────────────────── orders ───────────────────
    def save_order(self, order_data: dict) -> Order | None:
        if "user_id" not in order_data:
            raise ValueError("order_data must include user_id")
        obj = Order(**order_data)
        self.db.add(obj)
        return obj if self._commit("Insert order") else None

    def sync_orders(self, orders: List[dict]) -> None:
        if not orders:
            return
        if self.db.bind.dialect.name == "postgresql":
            insert_stmt = insert(Order).values(orders)
            update_cols = {
                c.name: getattr(insert_stmt.excluded, c.name)
                for c in Order.__table__.columns
                if c.name not in ("id", "ibkr_perm_id", "created_at")
            }
            stmt = insert_stmt.on_conflict_do_update(
                index_elements=["ibkr_perm_id"], set_=update_cols
            )
            self.db.execute(stmt)
        else:
            for data in orders:
                obj = (
                    self.db.query(Order)
                    .filter(Order.ibkr_perm_id == data["ibkr_perm_id"])
                    .first()
                )
                if obj:
                    for k, v in data.items():
                        setattr(obj, k, v)
                else:
                    self.db.add(Order(**data))
        self._commit(f"Sync {len(orders)} order(s)")

    # ─────────────────── executed trades ───────────────────
    def sync_executed_trades(self, trades: List[dict]) -> None:
        if not trades:
            return
        if self.db.bind.dialect.name == "postgresql":
            insert_stmt = insert(ExecutedTrade).values(trades)
            update_cols = {
                c.name: getattr(insert_stmt.excluded, c.name)
                for c in ExecutedTrade.__table__.columns
                if c.name not in ("id", "perm_id", "fill_time")
            }
            stmt = insert_stmt.on_conflict_do_update(
                constraint="uix_perm_id_fill_time", set_=update_cols
            )
            self.db.execute(stmt)
        else:
            for t in trades:
                obj = (
                    self.db.query(ExecutedTrade)
                    .filter(
                        ExecutedTrade.perm_id == t["perm_id"],
                        ExecutedTrade.fill_time == t["fill_time"],
                    )
                    .first()
                )
                if obj:
                    for k, v in t.items():
                        setattr(obj, k, v)
                else:
                    self.db.add(ExecutedTrade(**t))
        self._commit(f"Sync {len(trades)} trade(s)")

    # ─────────────────── read helpers ───────────────────
    def get_all_orders(self, *, user_id: int) -> Sequence[Order]:
        return (
            self.db.query(Order)
            .filter(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
            .all()
        )

    def get_all_executed_trades(self, *, user_id: int) -> Sequence[ExecutedTrade]:
        return (
            self.db.query(ExecutedTrade)
            .filter(ExecutedTrade.user_id == user_id)
            .order_by(ExecutedTrade.fill_time.desc())
            .all()
        )

    # runner-scoped
    def get_runner_orders(self, *, user_id: int, runner_id: int) -> Sequence[Order]:
        return (
            self.db.query(Order)
            .filter(Order.user_id == user_id, Order.runner_id == runner_id)
            .order_by(Order.created_at.desc())
            .all()
        )

    def get_runner_trades(
        self, *, user_id: int, runner_id: int
    ) -> Sequence[ExecutedTrade]:
        subq = (
            self.db.query(Order.ibkr_perm_id)
            .filter(Order.user_id == user_id, Order.runner_id == runner_id)
            .subquery()
        )
        return (
            self.db.query(ExecutedTrade)
            .filter(ExecutedTrade.user_id == user_id, ExecutedTrade.perm_id.in_(subq))
            .order_by(ExecutedTrade.fill_time.desc())
            .all()
        )
