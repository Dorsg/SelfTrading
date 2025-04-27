from __future__ import annotations

import logging
import time

import schedule

from database.db_manager import DBManager
from ib_manager.ib_connector import IBManager
from logger_config import setup_logging

setup_logging()
logger = logging.getLogger("runner-scheduler")

# ───────────────────── helpers ─────────────────────
def safe(fn, *args):
    """
    Wrap a job so that any exception is logged but does not kill the scheduler.
    """
    def _wrap():
        logger.debug("running job %s …", fn.__name__)
        try:
            fn(*args)
        except Exception:
            logger.exception("job %s crashed", fn.__name__)
        else:
            logger.debug("job %s finished", fn.__name__)
    return _wrap


def create_ib_for_user(user) -> IBManager:
    """
    Each user’s gateway container is named  ib-gateway-<user.id>
    and always listens on port 4004.
    """
    host = f"ib-gateway-{user.id}"
    port = 4004
    client_id = 100 + user.id
    logger.debug("Creating IBManager(host=%s,port=%s,cid=%s)", host, port, client_id)
    return IBManager(host=host, port=port, client_id=client_id)

# ───────────────────── per-user work ─────────────────────
def handle_user(user) -> None:
    logger.info("── handling user %s (id=%s) ──", user.username, user.id)
    ib = create_ib_for_user(user)
    db = DBManager()

    try:
        # snapshot (once per day)
        if not db.get_today_snapshot(user.id):
            data = ib.get_account_information()
            if data:
                db.create_account_snapshot(user_id=user.id, snapshot_data=data)
                logger.info("snapshot stored for %s", user.username)
            else:
                logger.warning("No snapshot data for %s (gateway returned empty)", user.username)

        # positions
        positions = ib.get_open_positions()
        logger.info("%d open positions for %s", len(positions), user.username)
        if positions:
            db.update_open_positions(user_id=user.id, positions=positions)

        # place a test order
        result = ib.place_test_aggressive_limit(user_id=user.id, runner_id=user.id + 100)

        if result.get("status") == "market_closed":
            logger.warning("Market is closed — no test order placed for %s", user.username)
        elif result.get("status") == "error":
            logger.error("Error placing test order for %s", user.username)
        else:
            logger.info("Test order placed for %s: %s", user.username, result)

        # always sync orders & trades
        ib.sync_orders_from_ibkr(user_id=user.id)
        ib.sync_executed_trades(user_id=user.id)

    finally:
        db.close()
        ib.disconnect()
        logger.debug("Closed DB + disconnected IB for %s", user.username)




def process_all_users():
    users = DBManager().get_users_with_ib()
    if not users:
        logger.warning("No users with IB creds")
        return
    logger.info("processing %d user(s)", len(users))
    for u in users:
        handle_user(u)
    logger.info("processed all users")


# ───────────────────── main loop ─────────────────────
def run_scheduler():
    logger.info("Scheduler booting …")
    schedule.every(1).minutes.do(safe(process_all_users))

    # run once immediately
    safe(process_all_users)()

    while True:
        schedule.run_pending()
        time.sleep(0.5)
