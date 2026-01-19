.PHONY: help dev dev-stop up down build logs test fmt clean

help:
	@echo "Available commands:"
	@echo "  make dev        - run backend locally using venv"
	@echo "  make dev-stop   - stop local dev server"
	@echo "  make up         - start full system with Docker"
	@echo "  make down       - stop Docker services"
	@echo "  make build      - build Docker images"
	@echo "  make logs       - show Docker logs"
	@echo "  make test       - run tests"
	@echo "  make fmt        - format code"
	@echo "  make clean      - cleanup containers and volumes"

# Local development (venv)
dev:
	@echo "Starting backend in local dev mode"
	cd backend && \
	. ../.venv/bin/activate && \
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-stop:
	@echo "Stop local dev server manually (CTRL+C)"

# Docker system
up:
	@echo "Starting full system with Docker"
	docker compose up -d --build

down:
	@echo "Stopping Docker services"
	docker compose down

build:
	@echo "Building Docker images"
	docker compose build

logs:
	@echo "Showing Docker logs"
	docker compose logs -f

# Quality
test:
	@echo "Running tests"
	cd backend && \
	. ../.venv/bin/activate && \
	pytest

fmt:
	@echo "Formatting code"
	cd backend && \
	. ../.venv/bin/activate && \
	black .

clean:
	@echo "Removing containers, volumes and orphaned resources"
	docker compose down -v --remove-orphans
