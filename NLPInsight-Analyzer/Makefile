# Workspace .venv at the repo root, synced from uv.lock (ADR-019).
# --no-sync: running never changes the installed set.
RUN=uv run --frozen --no-sync
PYTHON=$(RUN) python
CONFIG=configs/config.yaml

.PHONY: install train eval predict serve test clean start-demo

install:
	uv sync --frozen --package nlpinsight-analyzer --all-groups
	uv sync --frozen --only-dev --inexact

train:
	$(PYTHON) main.py --mode train --config $(CONFIG)

eval:
	$(PYTHON) main.py --mode eval --config $(CONFIG)

predict:
	$(PYTHON) main.py --mode predict --config $(CONFIG) --input_csv data/raw/train.csv --output_path artifacts/predictions.csv

serve:
	$(RUN) uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

start-demo: install
	$(PYTHON) main.py --mode train --config $(CONFIG)
	$(MAKE) serve

docker-demo:
	docker-compose -f docker-compose.yml up --build

test:
	$(RUN) pytest -q

clean:
	rm -rf artifacts models/__pycache__ .pytest_cache
