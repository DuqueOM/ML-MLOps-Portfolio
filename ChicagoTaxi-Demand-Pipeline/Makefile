# Makefile for ChicagoTaxi Demand Pipeline
# Usage: make <target>

.PHONY: help install test test-coverage lint format etl predict serve docker-build docker-run clean

# Workspace .venv at the repo root, synced from uv.lock (ADR-019).
# --no-sync: running never changes the installed set.
RUN := uv run --frozen --no-sync
PYTHON := $(RUN) python
PACKAGE := chicagotaxi-demand-pipeline
DOCKER_IMAGE := chicagotaxi-demand
DOCKER_TAG := latest

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\n", $$1, $$2}'

install: ## Install everything: API + ETL (PySpark, Dask) + dev tools, from uv.lock
	uv sync --frozen --package $(PACKAGE) --all-groups
	uv sync --frozen --only-dev --inexact

install-prod: ## Install the API's dependencies only (= the image)
	uv sync --frozen --package $(PACKAGE) --no-dev

test: ## Run tests
	$(PYTHON) -m pytest tests/ -v --tb=short

test-coverage: ## Run tests with coverage
	$(PYTHON) -m pytest tests/ --cov=src --cov=app --cov-report=html --cov-report=term

lint: ## Check code quality
	$(RUN) flake8 src/ app/ tests/
	$(RUN) mypy src/ --ignore-missing-imports

format: ## Format code
	$(RUN) black src/ app/ tests/
	$(RUN) isort src/ app/ tests/

etl: ## Run PySpark ETL pipeline
	$(PYTHON) scripts/spark_etl.py \
		--input "data/raw/Taxi_Trips_(2013-2023)_20260304.csv" \
		--output data/processed/taxi_trips_parquet

predict: ## Run Dask batch predictions
	$(PYTHON) scripts/batch_predict.py

serve: ## Start FastAPI server
	cd app && $(RUN) uvicorn fastapi_app:app --host 0.0.0.0 --port 8004 --reload

docker-build: ## Build Docker image (context = repo root: installs from uv.lock, ADR-019)
	docker build -f Dockerfile -t $(DOCKER_IMAGE):$(DOCKER_TAG) ..

docker-run: ## Run Docker container
	docker run -d --name chicagotaxi-container -p 8004:8000 $(DOCKER_IMAGE):$(DOCKER_TAG)

clean: ## Clean temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache/ htmlcov/ .coverage

pipeline: ## Run full pipeline (ETL + train + predict)
	$(MAKE) etl
	$(MAKE) predict

.DEFAULT_GOAL := help
