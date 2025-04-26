from fastapi import FastAPI
from api_gateway.routes import runner_routes
from api_gateway.routes import auth_routes 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runner_routes.router)
app.include_router(auth_routes.router)