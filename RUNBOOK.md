# Operations Runbook

Quick reference for running, testing, and deploying the ML/MLOps Portfolio.

## Quick Reference

| Operation | Command |
|-----------|---------|
| Start demo stack | `make docker-demo` |
| Health check | `make health-check` |
| Run all tests | `make test` |
| Stop services | `docker compose -f docker-compose.demo.yml down` |
| View logs | `docker compose -f docker-compose.demo.yml logs -f <service>` |

## Prerequisites

- Python 3.11+, Docker 20.10+, Docker Compose 2.0+, Make, Git
- RAM: 8GB min (16GB recommended)

```bash
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio
bash scripts/setup_demo_models.sh   # one-time model generation
make docker-demo                     # start all services
```

## Services

| Service | Port | Health |
|---------|------|--------|
| BankChurn API | 8001 | `curl localhost:8001/health` |
| NLPInsight API | 8003 | `curl localhost:8003/health` |
| ChicagoTaxi API | 8004 | `curl localhost:8004/health` |
| MLflow | 5000 | `curl localhost:5000` |

## Per-Project Commands

```bash
# BankChurn
cd BankChurn-Predictor
python main.py --mode train --config configs/config.yaml
uvicorn app.fastapi_app:app --port 8000

# NLPInsight
cd NLPInsight-Analyzer
python main.py --mode train --config configs/config.yaml
uvicorn app.fastapi_app:app --port 8000

# ChicagoTaxi (batch pipeline)
cd ChicagoTaxi-Demand-Pipeline
python scripts/spark_etl.py --input data/raw/taxi_trips.csv --output data/processed/taxi_trips_parquet
python scripts/batch_predict.py --input data/processed/taxi_trips_parquet/hourly_demand --train
uvicorn app.fastapi_app:app --port 8000
```

## Testing

```bash
make test                                          # all projects
cd BankChurn-Predictor && pytest tests/ -v --cov   # individual
pytest tests/integration/test_demo.py -v           # integration (requires running stack)
```

## Docker

```bash
make docker-build                                             # build all
docker build -t bankchurn:latest ./BankChurn-Predictor        # individual
docker compose -f docker-compose.demo.yml down -v --rmi all   # full cleanup
```

## Kubernetes (Production)

```bash
kubectl apply -f k8s/                              # GKE
kubectl apply -k k8s/overlays/aws/                 # EKS
kubectl get pods -n ml-portfolio                   # verify
./scripts/upload-models-to-gcs.sh all              # upload models
./scripts/deploy-canary.sh bankchurn v3.6.0        # canary deploy
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | `export PYTHONPATH=$PWD` |
| Port in use | `lsof -i :8001` then `kill -9 <PID>` |
| Container crash | `docker logs <container>` |
| Model not found | `make train` or `bash scripts/setup_demo_models.sh` |
| OOM | Increase Docker memory to 8GB+ |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_PATH` | `models/model.joblib` | Model artifact path |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `LOG_FORMAT` | `human` | `json` for production |
| `MLFLOW_TRACKING_URI` | `file:./mlruns` | MLflow server |

## CI/CD

Pipeline (`.github/workflows/ci-mlops.yml`): Tests → Quality Gates → Security → Docker Build → Container Scan → E2E → Publish

```bash
git push origin main                              # trigger CI
git tag -a v3.2.1 -m "Release" && git push --tags # release
```

## Links

- [README.md](README.md) — Portfolio overview
- [QUICK_START.md](QUICK_START.md) — 5-minute setup
- [docs/DEPLOYMENT_EVIDENCE.md](docs/DEPLOYMENT_EVIDENCE.md) — Production evidence
