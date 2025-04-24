import logging
from datetime import date, datetime
from sqlite3 import IntegrityError
from typing import List

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert 
from sqlalchemy.orm import Session

from database.db_core import SessionLocal
from database.models import (
    AccountSnapshot, ExecutedTrade, OpenPosition, Order, Runner
)

logger = logging.getLogger(__name__)


class DBManager:
    """
    Wrapper around a SQLAlchemy session with:
      • optional external session injection
      • context-manager support  →  `with DBManager() as db: ...`
      • one-liner `_commit()` that handles commit / rollback / log
    Public method *signatures* stay exactly the same.
    """

    # ─────────────────────────── lifecycle ────────────────────────────
    def __init__(self, db_session: Session | None = None) -> None:
        self._own_session = db_session is None
        self.db: Session = db_session or SessionLocal()

    def close(self) -> None:  # called by API layer today
        if self._own_session:
            self.db.close()

    # context-manager sugar – *optional* use
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        try:
            if exc_type:
                self.db.rollback()
            else:
                self.db.commit()
        finally:
            self.close()

    # ------------------------------------------------------------------
    def _commit(self, op: str) -> bool:
        """commit wrapper used by every mutating method"""
        try:
            self.db.commit()
            logger.info("%s – OK", op)
            return True
        except Exception:
            logger.exception("%s – FAILED", op)
            self.db.rollback()
            return False

    # ──────────────────── account-snapshot CRUD ───────────────────────
    # (unchanged except we now call _commit)
    def get_today_snapshot(self):
        return (
            self.db.query(AccountSnapshot)
            .filter(func.date(AccountSnapshot.timestamp) == date.today())
            .first()
        )

    def create_account_snapshot(self, snapshot_data: dict):
        snap = AccountSnapshot(
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

    # ───────────────────────── open positions ─────────────────────────
    def update_open_positions(self, positions: list):
        self.db.query(OpenPosition).delete()
        self.db.bulk_save_objects(
            OpenPosition(
                symbol=p["symbol"],
                quantity=p["quantity"],
                avg_price=p["avgCost"],
                account=p["account"],
            )
            for p in positions
        )
        self._commit("Update open positions")

    def get_open_positions(self):
        return self.db.query(OpenPosition).all()

    # ───────────── helpers ─────────────
    def get_runner_by_name(self, name: str):
        return self.db.query(Runner).filter(Runner.name == name).first()
    
    # ───────────────────────────── runners ────────────────────────────
    def create_runner(self, data: dict):
        # pre-check – nicer error than raw 500
        if self.get_runner_by_name(data["name"]):
            raise ValueError("Runner name already exists")

        runner = Runner(**data)
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

    def delete_runners(self, ids: List[int]) -> int:
        rows = (
            self.db.query(Runner)
            .filter(Runner.id.in_(ids))
            .delete(synchronize_session=False)
        )
        self._commit(f"Delete {rows} runner(s)")
        return rows

    def update_runners_activation(self, ids: List[int], activation: str) -> int:
        rows = (
            self.db.query(Runner)
            .filter(Runner.id.in_(ids))
            .update(
                {"activation": activation, "updated_at": datetime.utcnow()},
                synchronize_session=False,
            )
        )
        self._commit(f"{activation.capitalize()} {rows} runner(s)")
        return rows

    # ───────────────────────────── orders ─────────────────────────────
    def save_order(self, order_data: dict):
        obj = Order(**order_data)
        self.db.add(obj)
        return obj if self._commit("Insert order") else None

    def sync_orders(self, orders: List[dict]):
        """
        Upsert on `ibkr_perm_id`.  Uses one INSERT … ON CONFLICT when running
        on PostgreSQL; otherwise falls back to a row-by-row merge.
        """
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
                index_elements=["ibkr_perm_id"],
                set_=update_cols,
            )
            self.db.execute(stmt)
        else:  # generic merge (SQLite, MySQL, …)
            for data in orders:
                obj = self.db.query(Order).filter(
                    Order.ibkr_perm_id == data["ibkr_perm_id"]
                ).first()
                if obj:
                    for k, v in data.items():
                        setattr(obj, k, v)
                else:
                    self.db.add(Order(**data))

        self._commit(f"Sync {len(orders)} order(s)")

    # ────────────────────── executed trades sync ─────────────────────
    def sync_executed_trades(self, trades: List[dict]):
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
                constraint="uix_perm_id_fill_time",
                set_=update_cols,
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

    # ──────────────────────── read helpers ────────────────────────────
    def get_all_orders(self):
        return self.db.query(Order).order_by(Order.created_at.desc()).all()

    def get_all_executed_trades(self):
        return (
            self.db.query(ExecutedTrade)
            .order_by(ExecutedTrade.fill_time.desc())
            .all()
        )

    # ────────────────── runner-scoped read helpers ───────────────────
    def get_runner_orders(self, runner_id: int):
        """
        Return *all* orders that belong to a single runner, newest first.
        """
        return (
            self.db.query(Order)
            .filter(Order.runner_id == runner_id)
            .order_by(Order.created_at.desc())
            .all()
        )

    def get_runner_trades(self, runner_id: int):
        """
        Return *all* executed trades for a runner by linking orders → trades
        through perm_id (no additional joins needed thanks to the FK).
        """
        subq = (
            self.db.query(Order.ibkr_perm_id)
            .filter(Order.runner_id == runner_id)
            .subquery()
        )
        return (
            self.db.query(ExecutedTrade)
            .filter(ExecutedTrade.perm_id.in_(subq))
            .order_by(ExecutedTrade.fill_time.desc())
            .all()
        )

    # (nice-to-have) quickly fetch active runners — could drive dashboards
    def get_active_runners(self):
        return self.db.query(Runner).filter(Runner.activation == "active").all()