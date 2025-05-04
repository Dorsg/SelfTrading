import asyncio
import logging
from runner_scheduler.scheduler import main_loop 

logger = logging.getLogger("runner-scheduler")

# ──────────── Entrypoint ────────────
if __name__ == "__main__":
    try:
        logger.info("Starting the main loop...")
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        logger.info("Shutting down test POC loop.")
