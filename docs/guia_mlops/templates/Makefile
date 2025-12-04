# ════════════════════════════════════════════════════════════════════════════════
# MAKEFILE - Proyecto MLOps
# Comandos comunes para desarrollo, testing y deployment
# ════════════════════════════════════════════════════════════════════════════════

.PHONY: help install install-dev test lint format train predict serve \
        docker-build docker-run clean setup-dvc mlflow-ui

# Variables
PYTHON := python3
PIP := pip
PROJECT_NAME := ml-project
DOCKER_IMAGE := $(PROJECT_NAME):latest
PORT := 8000

# ─────────────────────────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────────────────────────

help: ## Muestra esta ayuda
	@echo "════════════════════════════════════════════════════════════════════════"
	@echo "                    📚 COMANDOS DISPONIBLES                              "
	@echo "════════════════════════════════════════════════════════════════════════"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ─────────────────────────────────────────────────────────────────────────────────
# Setup & Installation
# ─────────────────────────────────────────────────────────────────────────────────

install: ## Instala dependencias de producción
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-dev: install ## Instala dependencias de desarrollo
	$(PIP) install -r requirements-dev.txt
	pre-commit install

setup-env: ## Crea entorno virtual
	$(PYTHON) -m venv venv
	@echo "Activar con: source venv/bin/activate"

# ─────────────────────────────────────────────────────────────────────────────────
# Code Quality
# ─────────────────────────────────────────────────────────────────────────────────

lint: ## Ejecuta linters (flake8, mypy)
	flake8 src/ tests/ --max-line-length=100
	mypy src/ --ignore-missing-imports

format: ## Formatea código con black e isort
	black src/ tests/
	isort src/ tests/

format-check: ## Verifica formato sin modificar
	black --check --diff src/ tests/
	isort --check-only --diff src/ tests/

# ─────────────────────────────────────────────────────────────────────────────────
# Testing
# ─────────────────────────────────────────────────────────────────────────────────

test: ## Ejecuta todos los tests
	pytest tests/ -v

test-cov: ## Ejecuta tests con coverage
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "Reporte HTML en: htmlcov/index.html"

test-fast: ## Ejecuta tests rápidos (sin slow markers)
	pytest tests/ -v -m "not slow"

test-watch: ## Ejecuta tests en modo watch
	ptw tests/ -- -v

# ─────────────────────────────────────────────────────────────────────────────────
# ML Pipeline
# ─────────────────────────────────────────────────────────────────────────────────

train: ## Entrena el modelo
	$(PYTHON) src/models/train.py

predict: ## Ejecuta predicciones
	$(PYTHON) src/models/predict.py

evaluate: ## Evalúa el modelo
	$(PYTHON) src/models/evaluate.py

pipeline: ## Ejecuta pipeline completo con DVC
	dvc repro

# ─────────────────────────────────────────────────────────────────────────────────
# Data Management
# ─────────────────────────────────────────────────────────────────────────────────

setup-dvc: ## Inicializa DVC
	dvc init
	dvc remote add -d storage /tmp/dvc-storage
	@echo "DVC inicializado. Configura remote para producción."

data-pull: ## Descarga datos con DVC
	dvc pull

data-push: ## Sube datos con DVC
	dvc push

data-status: ## Muestra estado de datos DVC
	dvc status

# ─────────────────────────────────────────────────────────────────────────────────
# Experiment Tracking
# ─────────────────────────────────────────────────────────────────────────────────

mlflow-ui: ## Inicia MLflow UI
	mlflow ui --port 5000

mlflow-clean: ## Limpia experimentos antiguos
	@echo "⚠️  Esto eliminará experimentos. Usa con cuidado."
	# mlflow gc

# ─────────────────────────────────────────────────────────────────────────────────
# API & Serving
# ─────────────────────────────────────────────────────────────────────────────────

serve: ## Inicia servidor API en modo desarrollo
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port $(PORT)

serve-prod: ## Inicia servidor API en modo producción
	gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker \
		--bind 0.0.0.0:$(PORT)

# ─────────────────────────────────────────────────────────────────────────────────
# Docker
# ─────────────────────────────────────────────────────────────────────────────────

docker-build: ## Construye imagen Docker
	docker build -t $(DOCKER_IMAGE) .

docker-run: ## Ejecuta contenedor Docker
	docker run -p $(PORT):$(PORT) $(DOCKER_IMAGE)

docker-shell: ## Abre shell en contenedor
	docker run -it --rm $(DOCKER_IMAGE) /bin/bash

docker-clean: ## Limpia imágenes Docker no usadas
	docker system prune -f

# ─────────────────────────────────────────────────────────────────────────────────
# Documentation
# ─────────────────────────────────────────────────────────────────────────────────

docs: ## Genera documentación
	mkdocs build

docs-serve: ## Sirve documentación localmente
	mkdocs serve

# ─────────────────────────────────────────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────────────────────────────────────────

clean: ## Limpia archivos temporales
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	rm -rf .pytest_cache htmlcov .mypy_cache build dist *.egg-info

clean-all: clean ## Limpieza profunda (incluye modelos y datos procesados)
	rm -rf models/*.pkl models/*.joblib
	rm -rf data/processed/*
	rm -rf mlruns

# ─────────────────────────────────────────────────────────────────────────────────
# Shortcuts
# ─────────────────────────────────────────────────────────────────────────────────

all: format lint test ## Ejecuta format, lint y test

ci: format-check lint test-cov ## Simula pipeline CI localmente

run: train serve ## Entrena y sirve el modelo

# ─────────────────────────────────────────────────────────────────────────────────
# Default
# ─────────────────────────────────────────────────────────────────────────────────

.DEFAULT_GOAL := help
