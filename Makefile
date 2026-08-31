# Alfchamps - Makefile for local development and container management.
# This is a LOCAL-ONLY tool: services bind to 127.0.0.1.

SHELL := /bin/bash
PYTHON ?= python3
VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: help setup run-backend run-frontend build test-backend lint lint-frontend \
        podman-up podman-down docker-up docker-down clean

help:
	@echo "Alfchamps targets:"
	@echo "  make setup           Create venv, install backend+frontend deps"
	@echo "  make run-backend     Run FastAPI on http://127.0.0.1:8000"
	@echo "  make run-frontend    Run Vite dev on http://127.0.0.1:5173"
	@echo "  make build           Build the frontend for production"
	@echo "  make test-backend    Run backend pytest suite"
	@echo "  make lint            Run backend ruff"
	@echo "  make lint-frontend   Run frontend eslint"
	@echo "  make podman-up       Build & start containerized app"
	@echo "  make podman-down     Stop containers"
	@echo "  make docker-up       Build & start containerized app (docker compose)"
	@echo "  make docker-down     Stop containers (docker compose)"

setup:
	bash setup.sh

run-backend:
	$(PY) -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

build:
	cd frontend && npm run build

test-backend:
	$(PY) -m pytest backend/tests

lint:
	$(VENV)/bin/ruff check backend/app backend/tests

lint-frontend:
	cd frontend && npm run lint

podman-up:
	podman-compose up -d --build

podman-down:
	podman-compose down

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

clean:
	rm -rf .venv frontend/node_modules frontend/dist data/*.db
