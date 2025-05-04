import docker
import logging
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# ──────────── Setup Logging ────────────
log = logging.getLogger("IBKR-Gateway-Manager")

# ──────────── Constants ────────────
GATEWAY_IMAGE = os.getenv("DOCKER_IMAGE")
DOCKER_NETWORK = os.getenv("DOCKER_NETWORK")
CONTAINER_PORT = int(os.getenv("CONTAINER_PORT"))
HOST_PORT = int(os.getenv("HOST_PORT"))

# ──────────── Docker Setup ────────────
docker_client = docker.from_env()

def container_exists(user_id: int) -> bool:
    name = f"ib-gateway-{user_id}"
    try:
        docker_client.containers.get(name)
        log.debug(f"Container for user {user_id} exists.")
        return True
    except docker.errors.NotFound:
        log.debug(f"Container for user {user_id} not found.")
        return False

def start_container(user):
    name = f"ib-gateway-{user.id}"
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
        "VNC_SERVER_PASSWORD": os.getenv("VNC_SERVER_PASSWORD"),
        "OVERRIDE_API_PORT": str(CONTAINER_PORT),
    }

    log.info(f"Creating container for user {user.id} ({user.ib_username})")
    docker_client.containers.run(
        GATEWAY_IMAGE,
        name=name,
        environment=env,
        ports={f"{CONTAINER_PORT}/tcp": HOST_PORT + user.id},
        network=DOCKER_NETWORK,
        detach=True,
        restart_policy={"Name": "always"},
    )
    log.info(f"Container for user {user.id} started.")
