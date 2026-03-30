.PHONY: help install dev-backend dev-frontend db-setup db-migrate db-migrate-create \
        test-backend test-frontend test lint fmt clean \
        docker-up docker-down docker-dev-up docker-dev-down docker-logs docker-build docker-ps

# ── Variables ─────────────────────────────────────────────────────────
PYTHON      := python3.12
VENV        := backend/.venv
PIP         := $(VENV)/bin/pip
PYTEST      := $(VENV)/bin/pytest
ALEMBIC     := $(VENV)/bin/alembic
UVICORN     := $(VENV)/bin/uvicorn

# ── Help ──────────────────────────────────────────────────────────────
help:
	@echo "AgenticRAG — development commands"
	@echo ""
	@echo "  make install           Install all dependencies"
	@echo "  make dev-backend       Start backend dev server (port 8000)"
	@echo "  make dev-frontend      Start frontend dev server (port 5173)"
	@echo "  make db-setup          Create DB + enable pgvector extension"
	@echo "  make db-migrate        Run Alembic migrations (upgrade head)"
	@echo "  make db-migrate-create MSG='description'  Create new migration"
	@echo "  make test-backend      Run backend pytest suite"
	@echo "  make test-frontend     Run frontend vitest suite"
	@echo "  make test              Run all tests"
	@echo "  make lint              Run ruff linter"
	@echo "  make fmt               Run ruff formatter"
	@echo ""
	@echo "Docker commands:"
	@echo "  make docker-up         Build + start all services (DB+backend+frontend)"
	@echo "  make docker-down       Stop and remove containers"
	@echo "  make docker-dev-up     Dev mode: DB + backend only (hot-reload)"
	@echo "  make docker-dev-down   Stop dev containers"
	@echo "  make docker-logs       Tail logs for all services"
	@echo "  make docker-build      Rebuild images without cache"
	@echo "  make docker-ps         Show running containers"

# ── Install ───────────────────────────────────────────────────────────
install: install-backend install-frontend

install-backend:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r backend/requirements.txt

install-frontend:
	cd frontend && npm install

# ── Dev servers ───────────────────────────────────────────────────────
dev-backend:
	cd backend && $(UVICORN) app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

# ── Database ──────────────────────────────────────────────────────────
db-setup:
	bash scripts/setup_db.sh

db-migrate:
	cd backend && $(ALEMBIC) -c alembic/alembic.ini upgrade head

db-migrate-create:
	cd backend && $(ALEMBIC) -c alembic/alembic.ini revision --autogenerate -m "$(MSG)"

db-downgrade:
	cd backend && $(ALEMBIC) -c alembic/alembic.ini downgrade -1

# ── Tests ─────────────────────────────────────────────────────────────
test-backend:
	cd backend && $(PYTEST) tests/ -v

test-frontend:
	cd frontend && npm test

test: test-backend test-frontend

# ── Code quality ──────────────────────────────────────────────────────
lint:
	cd backend && $(VENV)/bin/ruff check app/ tests/

fmt:
	cd backend && $(VENV)/bin/ruff format app/ tests/

# ── Clean ─────────────────────────────────────────────────────────────
clean:
	find backend -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find backend -name "*.pyc" -delete 2>/dev/null || true
	rm -rf frontend/node_modules frontend/dist 2>/dev/null || true

# ── Docker: full stack ────────────────────────────────────────────────
docker-up:
	docker compose up --build -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-build:
	docker compose build --no-cache

docker-ps:
	docker compose ps

# ── Docker: dev mode (DB + backend only, hot-reload) ──────────────────
docker-dev-up:
	docker compose -f docker-compose.dev.yml up --build -d

docker-dev-down:
	docker compose -f docker-compose.dev.yml down

docker-dev-logs:
	docker compose -f docker-compose.dev.yml logs -f
