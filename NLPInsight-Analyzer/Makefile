PYTHON=python
CONFIG=configs/config.yaml

.PHONY: train eval predict serve test clean start-demo

install:
	$(PYTHON) -m pip install -r requirements.txt

train:
	$(PYTHON) main.py --mode train --config $(CONFIG)

eval:
	$(PYTHON) main.py --mode eval --config $(CONFIG)

predict:
	$(PYTHON) main.py --mode predict --config $(CONFIG) --input_csv data/raw/train.csv --output_path artifacts/predictions.csv

serve:
	uvicorn app.fastapi_app:app --host 0.0.0.0 --port 8000

start-demo:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) main.py --mode train --config $(CONFIG)
	$(MAKE) serve

docker-demo:
	docker-compose -f docker-compose.yml up --build

test:
	pytest -q

clean:
	rm -rf artifacts models/__pycache__ .pytest_cache
