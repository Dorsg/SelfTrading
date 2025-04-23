# ========== DEV MODE (Fast, Local) ==========

# Start Postgres in Docker only (that's OK)
dev-db:
	docker-compose -f docker-compose.yml up -d db

# Run init_db.py using your local Python env (no Docker!)
dev-db-init:
	@echo "Waiting for DB to initialize..."
	@timeout /T 15
	@set PYTHONPATH=.; call venv\Scripts\activate && python database/init_db.py

# Run FastAPI with hot reload
dev-api:
	call venv\Scripts\activate && uvicorn api_gateway.main:app --reload

# Run Vite frontend
dev-ui:
	cd client-ui-naive && npm install && npm run dev

# Run Python scheduler
dev-scheduler:
	set PYTHONPATH=.; call venv\Scripts\activate && python runner_scheduler/main.py

# Launch all dev services
start-dev:
	start cmd /k "make dev-api"
	start cmd /k "make dev-scheduler"
	start cmd /k "make dev-ui"

# ========== Docker Utilities ==========
stop-docker:
	docker-compose down

reset-db:
	docker-compose down -v

prod-up:
	docker-compose up --build

logs:
	docker-compose logs -f
