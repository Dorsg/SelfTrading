from fastapi import FastAPI
from api_gateway.routes import runner_routes

app = FastAPI()

app.include_router(runner_routes.router)