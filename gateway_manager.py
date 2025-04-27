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


def _wait_api(host: str, port: int = API_PORT, tries: int = 60, delay: int = 2) -> bool:
    """
    Poll <host>:<port> until it answers or we run out of tries.
    Returns True if the socket opened, False otherwise.
    """
    for i in range(1, tries + 1):
        try:
            with socket.create_connection((host, port), 2):
                log.info("%s:%s API port open (try %s/%s)", host, port, i, tries)
                return True
        except (socket.timeout, OSError):
            if i == 1:
                log.debug("%s:%s waiting for API …", host, port)
            time.sleep(delay)
    log.error("%s:%s never opened after %s tries", host, port, tries)
    return False


def _run_and_attach(name: str, env: dict) -> None:
    """
    Launch the gateway container on the compose network *without* publishing
    its ports to the host.  Inside the network it will be reachable via
    TCP-4004 at hostname == <name>.
    """
    log.info("→ docker run %s (env keys=%d)", name, len(env))
    container = cli.containers.run(
        IMAGE,
        name=name,
        hostname=name,
        network=DOCKER_NET,
        detach=True,
        environment=env,
        volumes={SETTINGS_VOL: {"bind": "/home/ibgateway/tws_settings"}},
        restart_policy={"Name": "always"},
        # Uncomment next line if you want VNC access on a random host port
        ports={"5900/tcp": ("127.0.0.1", None)},
    )

    # Belt-and-braces: add explicit DNS alias even though `hostname=` should do it
    cli.networks.get(DOCKER_NET).connect(container, aliases=[name])
    log.debug("  attached %s to %s with alias=%s", name, DOCKER_NET, name)

    # Block until the API socket is ready (or give up)
    if not _wait_api(name, API_PORT):
        log.warning("%s: API not reachable – removing container", name)
        container.remove(force=True)


def ensure_container(user) -> None:
    """
    Make sure a gateway container for *user* exists and is running.
    Creates / restarts it if necessary.
    """
    name = f"ib-gateway-{user.id}"
    log.debug("check-container %s for user=%s", name, user.username)
    log.info("DOR ib username: %s ib password: %s", user.ib_username, user.ib_password)

    try:
        c = cli.containers.get(name)
        if c.status != "running":
            log.warning("%s status=%s – restarting …", name, c.status)
            c.restart()
            _wait_api(name, API_PORT)
        return
    except NotFound:
        log.info("%s does not exist – will create", name)
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
        "OVERRIDE_API_PORT": "4004",  # ← ADD THIS LINE
    }
    _run_and_attach(name, env)


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
            log.info("pruning orphan %s (uid=%s not in %s)", c.name, uid, sorted(active_ids))
            c.remove(force=True)


# ───────────────── resilient main loop ──────────────────────
def fetch_users() -> List:
    """Return users with creds – or raise if the schema isn’t ready yet."""
    with DBManager() as db:
        return db.get_users_with_ib()


def main() -> None:
    log.info(
        "Gateway-manager starting on network %s  (interval=%ss)", DOCKER_NET, CHECK_INTERVAL
    )

    while True:
        loop_start = time.time()
        try:
            users = fetch_users()
            log.info("IB-users in DB: %d  ids=%s", len(users), [u.id for u in users])
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
        log.info("Gateway containers running: %s", sorted(running))

        for u in users:
            ensure_container(u)
        prune_orphans(ids)

        elapsed = time.time() - loop_start
        sleep_for = max(0, CHECK_INTERVAL - elapsed)
        log.debug("loop done in %.1f s → sleep %.1f s", elapsed, sleep_for)
        time.sleep(sleep_for)


if __name__ == "__main__":
    main()
