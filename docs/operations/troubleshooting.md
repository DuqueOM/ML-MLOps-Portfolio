# Troubleshooting Guide

Comprehensive troubleshooting guide for Docker, CI/CD, model serving, and dependency issues.

---

## Quick Diagnostics

```bash
# System health check
./scripts/health_check.sh

# Or manually:
docker-compose ps                    # Container status
docker stats                         # Resource usage
curl localhost:8001/health           # API health
```

---

## Docker Issues

### Container fails to start

**Symptoms:** Container exits immediately or restarts continuously.

**Diagnosis:**

```bash
# Check logs
docker-compose logs --tail 100 <service-name>

# Check exit code
docker-compose ps

# Inspect container
docker inspect <container-id> | jq '.[0].State'
```

**Common Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Missing model file | Run `scripts/setup_demo_models.sh` |
| Port already in use | Change port or stop conflicting service |
| Out of memory | Increase Docker memory limit |
| Permission denied | Check file ownership in volumes |

### Port conflicts

**Symptoms:** `Error: bind: address already in use`

```bash
# Find process using port
lsof -i :8001

# Or on Linux
netstat -tulpn | grep 8001

# Kill the process
kill -9 <PID>

# Or change ports in docker-compose
ports:
  - "9001:8000"  # Use different host port
```

### Out of memory

**Symptoms:** Container killed, `OOMKilled: true`

```bash
# Check memory usage
docker stats

# Increase limits in docker-compose
services:
  bankchurn:
    deploy:
      resources:
        limits:
          memory: 2G
```

### Build failures

**Symptoms:** Docker build fails during pip install

```bash
# Clear Docker cache
docker builder prune -f

# Build without cache
docker-compose build --no-cache

# Check for network issues
docker-compose build --network host
```

---

## CI/CD Issues

### Tests fail in CI but pass locally

**Diagnosis checklist:**

- [ ] Python version mismatch?
- [ ] Missing test dependencies?
- [ ] Environment variables not set?
- [ ] Different OS (Linux vs macOS)?

```bash
# Match CI Python version
python --version  # Should be 3.11 or 3.12

# Run with CI environment
CI=true pytest tests/ -v
```

### Flake8/Black conflicts

**Symptoms:** `E203 whitespace before ':'`

**Solution:** Already configured in `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/pycqa/flake8
  hooks:
    - id: flake8
      args: ["--max-line-length=120", "--extend-ignore=E203,W503"]
```

### Docker build fails in CI

**Symptoms:** `No such image` errors

**Solution:** Ensure image names match service names:

```yaml
# docker-compose.demo.yml
services:
  bankchurn:
    image: ml-portfolio-bankchurn:latest  # Pre-built in CI
```

### Coverage below threshold

**Symptoms:** `FAIL Required test coverage of 70% not reached`

```bash
# Check current coverage
pytest tests/ --cov=src/ --cov-report=term-missing

# Identify uncovered lines
pytest tests/ --cov=src/ --cov-report=html
open htmlcov/index.html
```

### Gitleaks false positives

**Symptoms:** CI fails on non-secret strings

**Solution:** Add to `.gitleaksignore`:

```
# .gitleaksignore
notebooks/EDA.ipynb:aws-access-token:123
```

---

## Model Serving Issues

### Model fails to load

**Symptoms:** `FileNotFoundError: models/model.pkl`

```bash
# Check model exists
ls -la models/

# Generate demo model
python -m bankchurn.cli train --config configs/config.yaml

# Or use setup script
bash scripts/setup_demo_models.sh
```

### Prediction returns 422 error

**Symptoms:** Validation error on predict endpoint

**Diagnosis:**

```bash
# Check error message
curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"invalid": "data"}' | jq .
```

**Common validation errors:**

| Error | Field | Fix |
|-------|-------|-----|
| `value is not a valid integer` | CreditScore | Use integer, not string |
| `field required` | Missing field | Add all required fields |
| `unexpected value` | Categorical | Use valid enum value |

### Prediction returns 500 error

**Symptoms:** Internal server error during inference

```bash
# Check API logs
docker-compose logs --tail 50 bankchurn-api

# Common causes:
# 1. Feature mismatch between training and inference
# 2. NaN values in input
# 3. Memory issues
```

### Slow predictions

**Symptoms:** P95 latency > 500ms

**Diagnosis:**

```bash
# Time a prediction
time curl -X POST http://localhost:8001/predict \
  -H "Content-Type: application/json" \
  -d '{"CreditScore": 650, ...}'
```

**Solutions:**

1. **Enable model caching:**
   ```python
   from functools import lru_cache
   
   @lru_cache(maxsize=1)
   def load_model():
       return joblib.load("models/model.pkl")
   ```

2. **Reduce model size:**
   ```python
   # Use fewer estimators
   RandomForestClassifier(n_estimators=50)  # Instead of 100
   ```

3. **Enable batch predictions:**
   ```python
   # Process multiple requests together
   model.predict(batch_of_inputs)
   ```

---

## API Issues

### CORS errors

**Symptoms:** Browser console shows CORS error

**Solution:** FastAPI already configured, but verify:

```python
# app/fastapi_app.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Connection refused

**Symptoms:** `Connection refused` when calling API

```bash
# Check if service is running
docker-compose ps

# Check if port is exposed
docker-compose port bankchurn 8000

# Check logs for startup errors
docker-compose logs bankchurn-api | head -50
```

### Request timeout

**Symptoms:** Request hangs, then times out

```bash
# Check for deadlocks
docker-compose exec bankchurn-api ps aux

# Check resource usage
docker stats bankchurn-api

# Increase timeout
curl --max-time 30 http://localhost:8001/predict
```

---

## Dependency Issues

### Package version conflicts

**Symptoms:** `pip install` fails with version conflict

```bash
# Show dependency tree
pip install pipdeptree
pipdeptree

# Find conflicts
pip check
```

### NumPy/Pandas compatibility

**Symptoms:** `AttributeError: module 'numpy' has no attribute 'xxx'`

**Solution:** Pin compatible versions:

```txt
# requirements.txt
numpy>=1.24.0,<2.0.0
pandas>=2.0.0,<3.0.0
```

### scikit-learn version mismatch

**Symptoms:** `AttributeError: Can't get attribute 'xxx'`

**Cause:** Model trained with different scikit-learn version.

**Solution:**

```bash
# Check model version
python -c "
import joblib
model = joblib.load('models/model.pkl')
print(model.__class__.__module__)
"

# Retrain with current version
python -m bankchurn.cli train
```

---

## MLflow Issues

### Cannot connect to MLflow

**Symptoms:** `ConnectionRefusedError: [Errno 111]`

```bash
# Start MLflow
docker-compose -f docker-compose.mlflow.yml up -d

# Check status
docker-compose -f docker-compose.mlflow.yml ps

# View logs
docker-compose -f docker-compose.mlflow.yml logs
```

### Artifact storage errors

**Symptoms:** `OSError: Unable to create artifact directory`

```bash
# Check permissions
ls -la mlruns/

# Fix permissions
chmod -R 777 mlruns/
```

---

## Data Issues

### DVC pull fails

**Symptoms:** `ERROR: failed to pull data`

```bash
# Check remote configuration
dvc remote list

# Configure remote
dvc remote add -d storage s3://bucket/path

# Or use local storage
dvc remote add -d local /path/to/storage
```

### Missing training data

**Symptoms:** `FileNotFoundError: data/raw/train.csv`

```bash
# Pull from DVC
dvc pull

# Or download manually
wget <data-url> -O data/raw/train.csv
```

---

## Performance Debugging

### Profile slow code

```python
import cProfile
import pstats

# Profile prediction
cProfile.run('model.predict(X)', 'profile.stats')

# Analyze results
stats = pstats.Stats('profile.stats')
stats.sort_stats('cumulative')
stats.print_stats(10)
```

### Memory profiling

```bash
# Install memory profiler
pip install memory-profiler

# Profile function
python -m memory_profiler your_script.py
```

---

## Getting Help

### Before opening an issue:

1. Check this guide
2. Search existing issues
3. Collect diagnostics:

```bash
# System info
python --version
pip freeze > requirements_current.txt
docker --version
docker-compose --version

# Logs
docker-compose logs > docker_logs.txt

# Error message
# (copy full traceback)
```

### Open an issue with:

- [ ] Clear description of the problem
- [ ] Steps to reproduce
- [ ] Expected vs actual behavior
- [ ] Environment details
- [ ] Relevant logs
- [ ] What you've already tried
