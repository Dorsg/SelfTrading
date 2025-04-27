from __future__ import annotations

# ---------------------------------------------------------------------------
# AnyIO worker threads (uvicorn) sometimes have no loop by default
# ---------------------------------------------------------------------------
import asyncio

try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import logging
import math
import os
import random
import socket
import time
from contextlib import contextmanager
from typing import Optional

from dotenv import load_dotenv
from ib_insync import IB, LimitOrder, Stock

from database.db_manager import DBManager
from ib_manager.market_data_manager import MarketDataManager

# ────────────────────────── logging ──────────────────────────
load_dotenv(dotenv_path="/app/.env", override=True)

logger = logging.getLogger("ib_manager.ib_connector")

# Make sure we really see our lines even when Uvicorn already configured root
LOGLEVEL = os.getenv("LOGLEVEL", "INFO").upper()
logger.setLevel(LOGLEVEL)
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(
        logging.Formatter(
            "%(asctime)s  %(levelname)-8s %(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
        )
    )
    logger.addHandler(h)

# ───────── constants ─────────
MAX_TRIES = int(os.getenv("IB_CONNECT_TRIES", 60))  # 60 × 2 s ≈ 2 min
RETRY_DELAY = int(os.getenv("IB_CONNECT_DELAY", 2))
TIMEOUT = int(os.getenv("IB_CONNECT_TIMEOUT", 6))

DEFAULT_CLIENT_ID = int(os.getenv("IB_CLIENT_ID", 15))


@contextmanager
def _timed(label: str):
    """Log duration; print INFO if the call is > 1 s, DEBUG otherwise."""
    start = time.perf_counter()
    yield
    dur = (time.perf_counter() - start) * 1000
    level = logging.INFO if dur > 1000 else logging.DEBUG
    logger.log(level, "%s took %.0f ms", label, dur)


class IBManager:
    """
    Very small wrapper around ib_insync.IB.
    One instance → one user’s gateway connection.
    """

    # ─────────────── lifecycle ───────────────
    def __init__(self, *, host: str, port: int, client_id: int | None = None) -> None:
        self.host = host
        self.port = port
        self.client_id = client_id or DEFAULT_CLIENT_ID
        self.ib = IB()

        logger.debug("Booting IBManager(host=%s, port=%s, cid=%s)", host, port, self.client_id)

        # 1️⃣ wait until Docker DNS resolves the container name
        while True:
            try:
                socket.gethostbyname(self.host)
                break
            except socket.gaierror:
                logger.debug("DNS not ready for %s → retry in 1 s", self.host)
                time.sleep(1)

        # 2️⃣ connect with retries
        for attempt in range(1, MAX_TRIES + 1):
            try:
                with _timed("ib.connect"):
                    self.ib.connect(host, port, clientId=self.client_id, timeout=TIMEOUT)
                logger.info("connected  %s:%s  (cid=%s)", host, port, self.client_id)
                break
            except (TimeoutError, socket.error) as e:
                logger.warning(
                    "Gateway %s:%s not ready (%d/%d) – %s",
                    host,
                    port,
                    attempt,
                    MAX_TRIES,
                    e.__class__.__name__,
                )
                time.sleep(RETRY_DELAY)
        else:
            logger.error("Gave up connecting to %s:%s after %d attempts", host, port, MAX_TRIES)
            raise RuntimeError("gateway-unreachable")

    def disconnect(self) -> None:
        try:
            self.ib.disconnect()
            logger.debug("Disconnected from %s:%s", self.host, self.port)
        except Exception:
            logger.exception("Error during disconnect")

    # ───────────────────── helpers ─────────────────────
    def _safe_call(self, label: str, fn, *args, **kwargs):
        try:
            with _timed(label):
                return fn(*args, **kwargs)
        except Exception:
            logger.exception("%s failed", label)
            return None

    # ───────────────────── account info ─────────────────────
    def get_account_information(self) -> dict:
        summary = self._safe_call("accountSummary", self.ib.accountSummary)
        if summary is None:
            return {}

        wanted = {
            "TotalCashValue",
            "CashBalance",
            "AccruedCash",
            "AvailableFunds",
            "ExcessLiquidity",
            "NetLiquidation",
            "RealizedPnL",
            "UnrealizedPnL",
            "GrossPositionValue",
            "BuyingPower",
        }
        res: dict = {}
        acct: Optional[str] = None
        for item in summary:
            if item.tag in wanted:
                key = f"{item.tag} ({item.currency})" if item.currency else item.tag
                res[key] = item.value
            if not acct and item.account != "All":
                acct = item.account
        if acct:
            res["account"] = acct
        logger.debug("Account summary parsed: %s", res)
        return res

    # ───────────────────── positions ─────────────────────
    def get_open_positions(self) -> list[dict]:
        positions = self._safe_call("ib.positions", self.ib.positions) or []
        out: list[dict] = [
            {
                "symbol": p.contract.symbol,
                "quantity": p.position,
                "avgCost": p.avgCost,
                "account": p.account,
            }
            for p in positions
        ]
        logger.debug("Fetched %d open positions", len(out))
        return out

    # ───────────────────── demo orders ─────────────────────
    def place_test_aggressive_limit(self, *, user_id: int, runner_id: int) -> dict:
        """
        1-share aggressive BUY LMT at +2 % so it fills instantly.
        Persists to DB with proper user_id.
        """
        try:
            symbol = random.choice(["AAPL", "NVDA", "TSLA", "PLTR"])
            contract = Stock(symbol, "SMART", "USD")

            mdm = MarketDataManager()
            if not mdm.is_market_open():
                return {"status": "market_closed"}

            price = mdm.get_current_price(symbol)
            if not price or math.isnan(price):
                return {"status": "price_unavailable", "symbol": symbol}

            lmt_px = round(price * 1.02, 2)
            self.ib.qualifyContracts(contract)
            order = LimitOrder("BUY", 1, lmt_px, tif="GTC", outsideRth=True)
            trade = self.ib.placeOrder(contract, order)

            # wait a bit for permId
            for _ in range(50):
                if trade.order.permId:
                    break
                self.ib.sleep(0.1)

            perm_id = trade.order.permId
            status = trade.orderStatus.status

            DBManager().save_order(
                {
                    "user_id": user_id,
                    "runner_id": runner_id,
                    "ibkr_perm_id": perm_id,
                    "symbol": symbol,
                    "action": order.action,
                    "order_type": order.orderType,
                    "quantity": order.totalQuantity,
                    "limit_price": lmt_px,
                    "status": status,
                    "account": trade.order.account or "",
                    "filled_quantity": trade.orderStatus.filled,
                    "avg_fill_price": trade.orderStatus.avgFillPrice,
                }
            )
            logger.info("Placed test LMT %s %s @ %.2f → %s", order.action, symbol, lmt_px, status)
            return {"status": status, "ibkr_perm_id": perm_id, "limit_price": lmt_px}
        except Exception:
            logger.exception("Error placing test limit")
            return {"status": "error"}

    # ───────────────────── sync helpers ─────────────────────
    def sync_orders_from_ibkr(self, *, user_id: int) -> None:
        try:
            count = 0
            for tr in self.ib.trades():
                pid = tr.order.permId
                if not pid:
                    continue
                DBManager().sync_orders(
                    [
                        {
                            "user_id": user_id,
                            "runner_id": None,  # fill if you can map
                            "ibkr_perm_id": pid,
                            "symbol": tr.contract.symbol,
                            "action": tr.order.action,
                            "order_type": tr.order.orderType,
                            "quantity": tr.order.totalQuantity,
                            "limit_price": getattr(tr.order, "lmtPrice", None),
                            "stop_price": getattr(tr.order, "auxPrice", None),
                            "status": tr.orderStatus.status,
                            "filled_quantity": tr.orderStatus.filled,
                            "avg_fill_price": tr.orderStatus.avgFillPrice,
                            "account": tr.order.account or "",
                        }
                    ]
                )
                count += 1
            logger.debug("Synchronized %d orders from IBKR", count)
        except Exception:
            logger.exception("sync_orders_from_ibkr failed")

    def sync_executed_trades(self, *, user_id: int) -> None:
        try:
            count = 0
            for tr in self.ib.trades():
                pid = tr.order.permId
                if not pid:
                    continue
                for f in tr.fills:
                    DBManager().sync_executed_trades(
                        [
                            {
                                "user_id": user_id,
                                "perm_id": pid,
                                "symbol": tr.contract.symbol,
                                "action": tr.order.action,
                                "order_type": tr.order.orderType,
                                "quantity": f.execution.shares,
                                "price": f.execution.price,
                                "fill_time": f.time,
                                "account": f.execution.acctNumber,
                            }
                        ]
                    )
                    count += 1
            logger.debug("Synchronized %d executed trades", count)
        except Exception:
            logger.exception("sync_executed_trades failed")
