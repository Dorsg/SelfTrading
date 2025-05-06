from fastapi import FastAPI
from api_gateway.routes import runner_routes, auth_routes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all routers under /api
app.include_router(auth_routes.router,   prefix="/api")
app.include_router(runner_routes.router, prefix="/api")