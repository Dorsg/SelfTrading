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
