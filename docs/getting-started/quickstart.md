<div class="portfolio-page" markdown="1">

# Quick Start

Get the full ML/MLOps stack running in 5 minutes.

## Prerequisites

- Docker 20.10+ and Docker Compose 2.0+
- 8 GB RAM minimum
- 20 GB disk space

## Setup

```bash
# 1. Clone
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio

# 2. Generate demo models (first time only)
bash scripts/setup_demo_models.sh

# 3. Start stack
docker compose -f docker-compose.demo.yml up -d --build

# 4. Verify (wait 30s for startup)
docker compose -f docker-compose.demo.yml ps
```

## Access

| Service | URL |
|---------|-----|
| BankChurn API | [localhost:8001/docs](http://localhost:8001/docs) |
| NLPInsight API | [localhost:8003/docs](http://localhost:8003/docs) |
| MLflow UI | [localhost:5000](http://localhost:5000) |

## Test Predictions

```bash
# BankChurn
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"CreditScore":650,"Geography":"France","Gender":"Male","Age":40,"Tenure":5,"Balance":60000,"NumOfProducts":2,"HasCrCard":1,"IsActiveMember":1,"EstimatedSalary":50000}'

# NLPInsight
curl -X POST http://localhost:8003/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"The company reported strong quarterly earnings"}'
```

## Stop

```bash
docker compose -f docker-compose.demo.yml down
```

---

*Last Updated: March 2026*

</div>
