import asyncio
import logging
from dotenv import load_dotenv
from database.db_manager import DBManager
from database.models import User
from ib_manager.gateway_manager import container_exists
from ib_manager.ib_connector import IBBusinessManager

# Load environment variables from .env file
load_dotenv()

# ──────────── Setup Logging ────────────
logging.basicConfig(
    level=logging.INFO,  # Change to INFO to minimize debug noise
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("Scheduler")  

async def connect_to_ib_gateway(user: User) -> IBBusinessManager:
    log.info(f"Attempting to connect and fetch data for user {user.id}")
    business_manager = IBBusinessManager(user)
    await business_manager.connect()
    return business_manager

async def fetch_and_store_snapshot(user: User, db: DBManager, business_manager: IBBusinessManager):
    if not db.get_today_snapshot(user.id):
        log.debug("Fetching account snapshot for %s", user.username)
        data = await business_manager.get_account_information()
        if data:
            db.create_account_snapshot(user_id=user.id, snapshot_data=data)
            log.info("Snapshot stored for %s", user.username)
        else:
            log.warning("No snapshot data for %s (gateway returned empty)", user.username)

async def fetch_open_positions(user: User, db: DBManager, business_manager: IBBusinessManager):
    log.debug("Fetching open positions for %s", user.username)
    positions = business_manager.get_open_positions()
    log.info("%d open positions for %s", len(positions), user.username)
    if positions:
        db.update_open_positions(user_id=user.id, positions=positions)

async def place_test_order(user: User, business_manager: IBBusinessManager):
    db = DBManager()
    existing_runner_id = db.get_existing_runner_id(user_id=user.id)
    if existing_runner_id is None:
        log.warning("No existing runner ID found for user %s", user.username)
        return
    await business_manager.place_test_aggressive_limit(user_id=user.id, runner_id=existing_runner_id)
    await asyncio.sleep(2)

async def sync_orders_and_trades(user: User, business_manager: IBBusinessManager):
    await business_manager.sync_orders_from_ibkr(user_id=user.id)
    await asyncio.sleep(2)

    business_manager.sync_executed_trades(user_id=user.id)
    await asyncio.sleep(2)

async def main_loop():
    db = DBManager()

    while True:
        log.info("Starting a new loop iteration...")
        users = DBManager().get_users_with_ib()
        if not users:
            log.warning("No users with IB accounts found.")

        for user in users:
            # Step 1: Start container if needed
            if not container_exists(user.id):
                log.warning(f"Static IB Gateway container missing: {user.id}")
                # skip current iteration if container is missing
                continue 

            # Step 2: Connect to IB Gateway
            business_manager = await connect_to_ib_gateway(user)

            # Step 3: Fetch and store snapshot
            await fetch_and_store_snapshot(user, db, business_manager)

            # Step 4: Fetch open positions
            await fetch_open_positions(user, db, business_manager)

            # Step 5: Place test order
            await place_test_order(user, business_manager)

            # Step 6: Sync orders and executed trades
            await sync_orders_and_trades(user, business_manager)

            # Step 7: Disconnect from IB Gateway
            business_manager.disconnect()

        log.info("Sleeping before next iteration...")
        ## sleep for 30 minutes 
        await asyncio.sleep(1800)
       
