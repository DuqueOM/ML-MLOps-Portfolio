# Pull Request Plan - Portfolio Standardization & Optimization

## Executive Summary

This document outlines a prioritized plan of 10 Pull Requests to standardize, optimize, and enhance the ML-MLOps Portfolio across all three projects. Each PR is designed to be independent and deliverable within 1-3 days.

---

## PR #1: Standardize Docker Multi-Stage Builds [HIGH PRIORITY]

**Title**: `feat: Standardize multi-stage Dockerfiles across all projects`

**Objective**: Ensure consistent, secure, and optimized Docker images for all three projects.

**Files Changed**:
- `BankChurn-Predictor/Dockerfile` (modify runtime Python version)
- `CarVision-Market-Intelligence/Dockerfile` (convert to multi-stage)
- `TelecomAI-Customer-Intelligence/Dockerfile` (convert to multi-stage)

**Changes Summary**:
1. Standardize base image to `python:3.11-slim`
2. Implement multi-stage builds (builder + runtime)
3. Add non-root user (`appuser`, UID 1000)
4. Optimize layer caching
5. Add comprehensive health checks
6. Include metadata labels

**Risk Level**: **MEDIUM**
- Requires testing all Docker builds
- May affect deployment configs
- Should not affect application logic

**Testing Checklist**:
- [ ] Build all three Docker images successfully
- [ ] Run docker-compose.demo.yml
- [ ] Verify health checks respond correctly
- [ ] Confirm images run as non-root user
- [ ] Check image size reduction (~50% expected)

**Diff Preview** (CarVision-Market-Intelligence/Dockerfile):
```dockerfile
# BEFORE
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]

# AFTER
FROM python:3.11-slim AS builder
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /build
RUN apt-get update && apt-get install -y gcc g++ build-essential
COPY requirements.txt ./
RUN python -m venv /opt/venv && . /opt/venv/bin/activate && \
    pip install --upgrade pip && pip install -r requirements.txt

FROM python:3.11-slim AS runtime
ENV PYTHONPATH=/app PATH="/opt/venv/bin:$PATH"
RUN apt-get update && apt-get install -y curl && \
    groupadd -r appuser --gid=1000 && useradd -r -g appuser --uid=1000 appuser
WORKDIR /app
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv
COPY --chown=appuser:appuser . .
USER appuser
EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "app.fastapi_app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Rollback Plan**: Revert to original single-stage Dockerfiles

---

## PR #2: Unified CI/CD with Matrix Testing [HIGH PRIORITY]

**Title**: `feat: Enhanced CI/CD with Python matrix and integration tests`

**Objective**: Comprehensive CI/CD pipeline covering all projects with multiple Python versions.

**Files Changed**:
- `.github/workflows/ci-mlops.yml` (major refactor)
- `tests/integration/test_demo.py` (new file)
- `.github/workflows/publish-images.yml` (new file)

**Changes Summary**:
1. Add Python version matrix (3.11, 3.12)
2. Integrate cross-project integration tests
3. Add automated Docker image publishing to GHCR
4. Improve artifact collection and reporting
5. Add deployment workflow (staging/production)

**Risk Level**: **LOW**
- Changes only affect CI/CD
- Does not modify application code
- Can be tested in feature branch

**Key Features**:
```yaml
strategy:
  matrix:
    python-version: ['3.11', '3.12']
    project: [BankChurn-Predictor, CarVision-Market-Intelligence, TelecomAI-Customer-Intelligence]
```

**Testing Checklist**:
- [ ] All tests pass on both Python versions
- [ ] Docker builds complete successfully
- [ ] Integration tests pass
- [ ] Coverage reports uploaded to Codecov
- [ ] Security scans complete (Trivy, Bandit)

**Rollback Plan**: Revert to previous ci-mlops.yml

---

## PR #3: Centralize Common Utilities [MEDIUM PRIORITY]

**Title**: `refactor: Extract shared utilities to common_utils module`

**Objective**: Eliminate code duplication by centralizing common functionality.

**Files Changed**:
- `common_utils/seed.py` (✅ already exists)
- `common_utils/logger.py` (✅ already created)
- `common_utils/config.py` (new)
- `common_utils/validation.py` (new)
- Update imports in all three projects

**Changes Summary**:
1. Shared logging configuration
2. Unified seed management (reproducibility)
3. Common configuration loading utilities
4. Shared validation helpers
5. Update all projects to use common utilities

**Example - logger.py**:
```python
import logging
import sys

def setup_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """Configure consistent logging across all projects."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger
```

**Risk Level**: **MEDIUM**
- Changes import statements across projects
- Needs thorough testing
- Low risk of breaking functionality

**Testing Checklist**:
- [ ] All unit tests pass
- [ ] No import errors
- [ ] Logging works consistently
- [ ] Seed produces reproducible results

**Rollback Plan**: Revert imports to local implementations

---

## PR #4: Dependency Standardization [HIGH PRIORITY]

**Title**: `fix: Standardize and pin critical dependencies across projects`

**Objective**: Resolve version conflicts and ensure reproducible builds.

**Files Changed**:
- `BankChurn-Predictor/requirements.in`
- `BankChurn-Predictor/requirements.txt`
- `CarVision-Market-Intelligence/requirements.in`
- `CarVision-Market-Intelligence/requirements.txt`
- `TelecomAI-Customer-Intelligence/requirements.in`
- `TelecomAI-Customer-Intelligence/requirements.txt`
- `common_requirements.in` (new)
- `docs/DEPENDENCY_CONFLICTS.md` (update)

**Changes Summary**:
1. Pin PyArrow to 21.0.0 across all projects
2. Pin Pydantic to v1.10.x (<2.0.0)
3. Standardize scikit-learn to 1.4.0
4. Create common_requirements.in for shared deps
5. Recompile all requirements.txt with hashes

**Key Pins**:
```python
# common_requirements.in
python>=3.11,<3.13
pandas==2.1.4
numpy==1.26.0
scikit-learn==1.4.0
fastapi==0.109.0
uvicorn==0.27.0
pydantic>=1.10.0,<2.0.0
pyarrow==21.0.0
mlflow==2.9.2
pytest==7.4.3
pytest-cov==4.1.0
```

**Risk Level**: **HIGH**
- Changes core dependencies
- Requires extensive testing
- May reveal hidden compatibility issues

**Testing Checklist**:
- [ ] All projects install successfully
- [ ] No dependency conflicts
- [ ] All unit tests pass
- [ ] Docker builds succeed
- [ ] Models train and predict correctly
- [ ] Integration tests pass

**Rollback Plan**: Revert requirements files to previous versions

---

## PR #5: Kubernetes Manifests Enhancement [MEDIUM PRIORITY]

**Title**: `feat: Enhanced K8s manifests with HPA, probes, and resource limits`

**Objective**: Production-ready Kubernetes deployments with autoscaling and monitoring.

**Files Changed**:
- `k8s/bankchurn-deployment.yaml`
- `k8s/carvision-deployment.yaml`
- `k8s/telecom-deployment.yaml`
- `k8s/hpa.yaml` (new)
- `k8s/configmap.yaml` (new)
- `k8s/ingress.yaml` (update)

**Changes Summary**:
1. Add resource requests and limits
2. Implement readiness and liveness probes
3. Add Horizontal Pod Autoscaler (HPA)
4. Create ConfigMaps for environment variables
5. Update Ingress with TLS configuration
6. Add PodDisruptionBudget

**Example - Resource Limits**:
```yaml
resources:
  requests:
    cpu: "250m"
    memory: "512Mi"
  limits:
    cpu: "1000m"
    memory: "2Gi"
```

**HPA Configuration**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bankchurn-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: bankchurn
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Risk Level**: **LOW**
- Only affects K8s deployments
- Can be tested in staging cluster
- Does not affect local development

**Testing Checklist**:
- [ ] Deployments create successfully
- [ ] Health probes respond correctly
- [ ] HPA scales up under load
- [ ] Services are accessible via Ingress
- [ ] ConfigMaps injected correctly

**Rollback Plan**: `kubectl rollout undo deployment/<name>`

---

## PR #6: Comprehensive Documentation Update [LOW PRIORITY]

**Title**: `docs: Complete portfolio documentation with architecture diagrams`

**Objective**: Professional documentation for recruiters and technical leads.

**Files Changed**:
- `README.md` (major update)
- `docs/ARCHITECTURE_PORTFOLIO.md` (✅ created)
- `docs/OPERATIONS_PORTFOLIO.md` (✅ created)
- `docs/RELEASE.md` (✅ created)
- `docs/DEPENDENCY_CONFLICTS.md` (✅ created)
- `BankChurn-Predictor/README.md` (update)
- `CarVision-Market-Intelligence/README.md` (update)
- `TelecomAI-Customer-Intelligence/README.md` (update)

**Changes Summary**:
1. Update root README with unified quickstart
2. Add architecture diagrams (Mermaid)
3. Document deployment processes
4. Add troubleshooting guides
5. Create API documentation links
6. Add badges (build status, coverage, etc.)

**Risk Level**: **NONE**
- Documentation only
- No code changes

**Testing Checklist**:
- [ ] All links work
- [ ] Mermaid diagrams render
- [ ] Commands execute correctly
- [ ] Spelling and grammar check

---

## PR #7: Root README Overhaul [HIGH PRIORITY]

**Title**: `docs: Professional root README with badges, quickstart, and architecture`

**Objective**: Create a compelling portfolio entry point.

**Files Changed**:
- `README.md` (complete rewrite)

**Changes Summary**:
1. Add CI/CD badges (build status, coverage)
2. Create eye-catching hero section
3. Add one-liner demo command
4. Include architecture diagram
5. List all three projects with links
6. Add technology stack overview
7. Include screenshots/GIFs
8. Add contributor section

**Example Structure**:
```markdown
# 🚀 ML/MLOps Portfolio - Production-Ready ML Systems

[![CI/CD](https://github.com/DuqueOM/ML-MLOps-Portfolio/workflows/CI%2FCD%20MLOps%20Portfolio/badge.svg)](https://github.com/DuqueOM/ML-MLOps-Portfolio/actions)
[![Coverage](https://codecov.io/gh/DuqueOM/ML-MLOps-Portfolio/branch/main/graph/badge.svg)](https://codecov.io/gh/DuqueOM/ML-MLOps-Portfolio)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> **Three production-grade ML systems** with unified MLOps infrastructure, CI/CD, and monitoring.

## 🎯 Quick Start (10 Minutes)

\`\`\`bash
git clone https://github.com/DuqueOM/ML-MLOps-Portfolio.git
cd ML-MLOps-Portfolio
docker-compose -f docker-compose.demo.yml up
# Access: http://localhost:8001/docs (BankChurn), http://localhost:8002/docs (CarVision), http://localhost:8003/docs (TelecomAI)
\`\`\`

## 📊 Projects

### 1. BankChurn-Predictor
- **Domain**: Customer Churn Prediction (Banking)
- **ML**: XGBoost + Optuna
- **Metrics**: 92% F1-score, 0.94 AUC-ROC
- [Docs](./BankChurn-Predictor/README.md) | [API](http://localhost:8001/docs)

### 2. CarVision-Market-Intelligence
- **Domain**: Vehicle Price Prediction
- **ML**: Random Forest Regressor
- **Metrics**: R²=0.675, RMSE=$6,009
- [Docs](./CarVision-Market-Intelligence/README.md) | [Dashboard](http://localhost:8501)

### 3. TelecomAI-Customer-Intelligence
- **Domain**: Telecom Plan Recommendation
- **ML**: Scikit-Learn Classifier
- **Metrics**: 85% Accuracy
- [Docs](./TelecomAI-Customer-Intelligence/README.md) | [API](http://localhost:8003/docs)
```

**Risk Level**: **NONE**

---

## PR #8: Integration Tests Suite [MEDIUM PRIORITY]

**Title**: `test: Comprehensive integration tests for demo stack`

**Objective**: Automated testing of full system integration.

**Files Changed**:
- `tests/integration/test_demo.py` (✅ created)
- `tests/integration/test_performance.py` (new)
- `tests/integration/test_security.py` (new)
- `scripts/run_demo_tests.sh` (update)

**Changes Summary**:
1. Health check tests for all services
2. Prediction endpoint tests
3. Performance benchmarks (response time)
4. Security tests (input validation, CORS)
5. Load testing scenarios

**Example Test**:
```python
def test_bankchurn_batch_prediction():
    url = f"{BASE_URLS['bankchurn']}/predict_batch"
    customers = [
        {"CreditScore": 650, "Geography": "France", "Gender": "Female", 
         "Age": 40, "Tenure": 3, "Balance": 60000.0, "NumOfProducts": 2,
         "HasCrCard": 1, "IsActiveMember": 1, "EstimatedSalary": 50000.0}
        for _ in range(10)
    ]
    response = requests.post(url, json={"customers": customers})
    assert response.status_code == 200
    data = response.json()
    assert len(data["predictions"]) == 10
    assert data["processing_time_seconds"] < 1.0  # Performance requirement
```

**Risk Level**: **LOW**

**Testing Checklist**:
- [ ] All integration tests pass
- [ ] Tests cover all critical paths
- [ ] Performance benchmarks met

---

## PR #9: Monitoring & Observability Stack [LOW PRIORITY]

**Title**: `feat: Production monitoring with Prometheus and Grafana`

**Objective**: Complete observability for all services.

**Files Changed**:
- `infra/prometheus-config.yaml` (update)
- `infra/grafana-dashboards/` (new directory)
- `k8s/prometheus-deployment.yaml` (update)
- `k8s/grafana-deployment.yaml` (update)
- Add Prometheus client to all FastAPI apps

**Changes Summary**:
1. Configure Prometheus scraping for all APIs
2. Create Grafana dashboards for each project
3. Add custom metrics to FastAPI apps
4. Set up alerting rules
5. Document monitoring workflows

**Custom Metrics**:
```python
from prometheus_client import Counter, Histogram

prediction_count = Counter('predictions_total', 'Total predictions', ['project', 'status'])
prediction_duration = Histogram('prediction_duration_seconds', 'Prediction duration')

@app.post("/predict")
async def predict(data: InputData):
    with prediction_duration.time():
        result = model.predict(data)
    prediction_count.labels(project='bankchurn', status='success').inc()
    return result
```

**Risk Level**: **LOW**

---

## PR #10: Security Hardening [MEDIUM PRIORITY]

**Title**: `security: Enhanced security with rate limiting, input validation, and CORS`

**Objective**: Production-ready security measures.

**Files Changed**:
- All `app/fastapi_app.py` files
- Add `requirements-security.txt`
- `.github/workflows/security-scan.yml` (new)
- `k8s/network-policy.yaml` (new)

**Changes Summary**:
1. Implement rate limiting (slowapi)
2. Add request ID tracking
3. Enhance CORS configuration
4. Add input sanitization
5. Implement API key authentication (optional)
6. Create Kubernetes NetworkPolicies
7. Add security headers

**Rate Limiting Example**:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/predict")
@limiter.limit("100/minute")
async def predict(request: Request, data: InputData):
    ...
```

**Risk Level**: **MEDIUM**
- Changes API behavior
- May affect existing clients
- Requires testing rate limits

**Testing Checklist**:
- [ ] Rate limits enforce correctly
- [ ] CORS allows expected origins
- [ ] Security headers present
- [ ] API keys work (if implemented)

---

## Priority Summary

### Week 1 (Must-Have)
1. **PR #1**: Standardize Docker (HIGH)
2. **PR #4**: Dependency Standardization (HIGH)
3. **PR #7**: Root README Overhaul (HIGH)

### Week 2 (Should-Have)
4. **PR #2**: Unified CI/CD (HIGH)
5. **PR #3**: Common Utilities (MEDIUM)
6. **PR #5**: K8s Enhancements (MEDIUM)

### Week 3 (Nice-to-Have)
7. **PR #8**: Integration Tests (MEDIUM)
8. **PR #10**: Security Hardening (MEDIUM)

### Week 4 (Optional)
9. **PR #6**: Documentation (LOW)
10. **PR #9**: Monitoring Stack (LOW)

---

## Delivery Timeline

| Week | PRs | Focus |
|------|-----|-------|
| 1 | #1, #4, #7 | Infrastructure & Documentation |
| 2 | #2, #3, #5 | CI/CD & Code Quality |
| 3 | #8, #10 | Testing & Security |
| 4 | #6, #9 | Polish & Monitoring |

**Total Duration**: 4 weeks (20 business days)

---

## Success Criteria

- [ ] All Docker images build successfully
- [ ] CI/CD pipeline passes for all projects
- [ ] Integration tests achieve >90% pass rate
- [ ] Documentation complete and accurate
- [ ] No critical security vulnerabilities
- [ ] Demo stack runs in <5 minutes
- [ ] Code coverage >75% for all projects
- [ ] All dependencies pinned and compatible

---

## Rollback Strategy

Each PR includes a rollback plan. General rollback procedure:

```bash
# Identify problematic PR
git log --oneline

# Revert specific commit
git revert <commit-hash>

# Or rollback deployment
kubectl rollout undo deployment/<name>

# Or restore Docker images
docker pull ghcr.io/duqueom/project:previous-tag
```

---

## Post-Merge Checklist

After each PR merge:
- [ ] Update CHANGELOG.md
- [ ] Run full integration tests
- [ ] Update documentation if needed
- [ ] Deploy to staging environment
- [ ] Monitor for 24 hours
- [ ] Tag release if milestone reached
