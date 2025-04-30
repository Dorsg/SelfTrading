"""
Start / restart / prune one IB-Gateway container per user that has credentials.

▸ waits for Postgres TCP and for the `users` table to exist
▸ verifies that the API socket (port 4004) is really open before it
  considers the container “ready”
▸ runs forever, retrying on every error
"""
from __future__ import annotations

import logging
import os
import socket
import time
from typing import List

import docker
from docker.errors import APIError, NotFound
from ib_insync import IB
from psycopg2.errors import UndefinedTable
from sqlalchemy.exc import OperationalError, ProgrammingError

from database.db_manager import DBManager

# ────────────────────────── logging ──────────────────────────
logging.basicConfig(
    level=os.getenv("LOGLEVEL", "INFO").upper(),
    format="%(asctime)s  %(levelname)-8s %(name)s: %(message)s",
)
log = logging.getLogger("gateway-manager")

# ────────────────────────── constants ─────────────────────────
IMAGE = "ghcr.io/gnzsnz/ib-gateway:vnc"
CHECK_INTERVAL = 30          # sec between main-loop iterations
SETTINGS_VOL = "ib_settings"
API_PORT = 4004              # inside the compose network

PROJECT = os.getenv("COMPOSE_PROJECT_NAME") or "selftrading"
DOCKER_NET = f"{PROJECT}_default"

cli = docker.from_env()

# ───────────────── helpers ───────────────────────────────────

def _wait_api(host: str, port: int = 4004, tries: int = 60, delay: int = 2) -> bool:
    """
    Check that the IB Gateway is truly ready by:
    1. Ensuring the TCP socket opens
    2. Actually connecting with IB() and immediately disconnecting
    """
    log.debug("Checking socket readiness for %s:%d", host, port)
    for i in range(1, tries + 1):
        try:
            with socket.create_connection((host, port), timeout=2):
                log.info("%s:%d TCP socket open (try %d/%d)", host, port, i, tries)
                break
        except Exception:
            log.debug("Socket not open on %s:%d (try %d/%d)", host, port, i, tries)
            time.sleep(delay)
    else:
        log.error("Socket never opened on %s:%d", host, port)
        return False

    log.debug("Checking IB API readiness via ib.connect() on %s:%d", host, port)
    ib = IB()
    for i in range(1, tries + 1):
        try:
            ib.connect(host, port, clientId=9999, timeout=5)
            ib.disconnect()
            log.info("IB Gateway ready on %s:%d (API check passed, try %d/%d)", host, port, i, tries)
            return True
        except Exception as e:
            log.debug("IB API not ready on %s:%d — %s (try %d/%d)", host, port, type(e).__name__, i, tries)
            time.sleep(delay)

    log.error("Gave up waiting for IB API on %s:%d", host, port)
    return False


def _run_and_attach(name: str, env: dict) -> bool:
    """
    Launch the gateway container and verify it becomes reachable.
    Returns True if ready, False if failed (container removed).
    """
    log.info("Launching container %s with %d env vars", name, len(env))
    try:
        container = cli.containers.run(
            IMAGE,
            name=name,
            hostname=name,
            network=DOCKER_NET,
            detach=True,
            environment=env,
            volumes={SETTINGS_VOL: {"bind": "/home/ibgateway/tws_settings"}},
            restart_policy={"Name": "always"},
            ports={"5900/tcp": ("127.0.0.1", None)},
        )
        cli.networks.get(DOCKER_NET).connect(container, aliases=[name])
        log.debug("Attached %s to network %s with alias %s", name, DOCKER_NET, name)
    except Exception as e:
        log.exception("Failed to run container %s: %s", name, type(e).__name__)
        return False

    if not _wait_api(name, API_PORT):
        log.warning("%s: API not reachable – removing container", name)
        container.remove(force=True)
        return False

    log.info("Container %s ready and reachable", name)
    return True


def ensure_container(user) -> None:
    """
    Make sure a gateway container for *user* exists and is running.
    Retries once if container failed to become ready.
    """
    name = f"ib-gateway-{user.id}"
    log.debug("Ensuring container %s for user=%s", name, user.username)

    try:
        c = cli.containers.get(name)
        if c.status != "running":
            log.warning("%s status=%s – restarting", name, c.status)
            c.restart()
            if not _wait_api(name, API_PORT):
                log.warning("%s failed to restart — removing", name)
                c.remove(force=True)
            else:
                log.info("Restarted %s and ready", name)
                return
        else:
            log.info("%s already running", name)
            return
    except NotFound:
        log.info("%s does not exist – creating", name)
    except APIError:
        log.exception("Docker API error while inspecting %s", name)
        return

    env = {
        "TWS_USERID": user.ib_username,
        "TWS_PASSWORD": user.ib_password,
        "TRADING_MODE": "paper",
        "READ_ONLY_API": "no",
        "TIME_ZONE": "Asia/Jerusalem",
        "TWS_ACCEPT_INCOMING": "accept",
        "BYPASS_WARNING": "yes",
        "BypassOrderPrecautions": "yes",
        "BypassPriceBasedVolatilityRiskWarning": "yes",
        "BypassNoOverfillProtectionPrecaution": "yes",
        "BypassRedirectOrderWarning": "yes",
        "AllowBlindTrading": "yes",
        "ENABLE_VNC": "yes",
        "ENABLE_VNC_SERVER": "true",
        "VNC_SERVER_PASSWORD": "trader123",
        "OVERRIDE_API_PORT": "4004",
    }

    success = _run_and_attach(name, env)
    if not success:
        log.error("Failed to bring up container %s for user %s", name, user.username)


def prune_orphans(active_ids: set[int]) -> None:
    """Remove gateway containers that belong to no active user."""
    for c in cli.containers.list(filters={"ancestor": IMAGE}):
        if not c.name.startswith("ib-gateway-"):
            continue
        try:
            uid = int(c.name.split("ib-gateway-")[1])
        except ValueError:
            continue
        if uid not in active_ids:
            log.info("Pruning orphan %s (uid=%s not in %s)", c.name, uid, sorted(active_ids))
            c.remove(force=True)


# ───────────────── resilient main loop ──────────────────────
def fetch_users() -> List:
    """Return users with creds – or raise if the schema isn’t ready yet."""
    with DBManager() as db:
        return db.get_users_with_ib()


def main() -> None:
    log.info("Gateway-manager starting on network %s  (interval=%ss)", DOCKER_NET, CHECK_INTERVAL)

    while True:
        loop_start = time.time()
        try:
            users = fetch_users()
            log.info("Found %d IB-user(s) in DB: %s", len(users), [u.id for u in users])
        except (OperationalError, ProgrammingError, UndefinedTable) as e:
            log.warning("DB not ready (%s) – retrying in %s s", e.__class__.__name__, CHECK_INTERVAL)
            time.sleep(CHECK_INTERVAL)
            continue
        except Exception:
            log.exception("Unexpected DB error – retrying")
            time.sleep(CHECK_INTERVAL)
            continue

        ids = {u.id for u in users}
        running = {c.name for c in cli.containers.list(filters={"ancestor": IMAGE})}
        log.info("Currently running containers: %s", sorted(running))

        for u in users:
            ensure_container(u)
        prune_orphans(ids)

        elapsed = time.time() - loop_start
        sleep_for = max(0, CHECK_INTERVAL - elapsed)
        log.debug("Loop finished in %.1f s – sleeping %.1f s", elapsed, sleep_for)
        time.sleep(sleep_for)


if __name__ == "__main__":
    main()
