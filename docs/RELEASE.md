# Release Management Guide

## Release Process

### Version Strategy

We follow [Semantic Versioning](https://semver.org/) (SemVer):
- **MAJOR.MINOR.PATCH** (e.g., `1.2.3`)
- **MAJOR**: Incompatible API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

#### 1. Pre-Release Preparation

- [ ] All tests passing on `develop` branch
- [ ] Code coverage >= 75% for all projects
- [ ] Security scans clean (no CRITICAL/HIGH vulnerabilities)
- [ ] Documentation updated (README, CHANGELOG)
- [ ] Model performance meets thresholds
- [ ] Integration tests pass

#### 2. Version Bump

```bash
# Update version in all projects
cd BankChurn-Predictor
# Update version in: __init__.py, pyproject.toml, Dockerfile LABEL

cd ../CarVision-Market-Intelligence
# Update version files

cd ../TelecomAI-Customer-Intelligence
# Update version files

# Update CHANGELOG.md
vim CHANGELOG.md
```

**CHANGELOG.md format**:
```markdown
## [1.2.0] - 2025-01-15

### Added
- New feature X in BankChurn
- Dashboard improvements in CarVision

### Changed
- Updated sklearn to 1.4.0
- Improved API response times

### Fixed
- Bug fix in TelecomAI prediction endpoint

### Security
- Updated dependencies with CVE fixes
```

#### 3. Create Release Branch

```bash
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0
```

#### 4. Final Testing

```bash
# Run full test suite
pytest --cov=. --cov-report=html

# Build Docker images
docker-compose -f docker-compose.demo.yml build

# Run integration tests
docker-compose -f docker-compose.demo.yml up -d
pytest tests/integration/test_demo.py -v
docker-compose -f docker-compose.demo.yml down

# Security scans
bandit -r . -f json -o bandit-report.json
docker run --rm -v $(pwd):/app aquasec/trivy image ml-portfolio:latest
```

#### 5. Merge to Main

```bash
git checkout main
git merge release/v1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin main --tags
```

#### 6. Create GitHub Release

**Via GitHub UI**:
1. Go to **Releases** → **Draft a new release**
2. Choose tag `v1.2.0`
3. Title: `Release v1.2.0`
4. Description: Copy from CHANGELOG
5. Upload artifacts (optional)
6. **Publish release**

**Via GitHub CLI**:
```bash
gh release create v1.2.0 \
  --title "Release v1.2.0" \
  --notes-file CHANGELOG.md
```

#### 7. Build & Push Docker Images to GHCR

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Build and tag images
docker build -t ghcr.io/duqueom/bankchurn-api:1.2.0 ./BankChurn-Predictor
docker build -t ghcr.io/duqueom/bankchurn-api:latest ./BankChurn-Predictor

docker build -t ghcr.io/duqueom/carvision-api:1.2.0 ./CarVision-Market-Intelligence
docker build -t ghcr.io/duqueom/carvision-api:latest ./CarVision-Market-Intelligence

docker build -t ghcr.io/duqueom/telecom-api:1.2.0 ./TelecomAI-Customer-Intelligence
docker build -t ghcr.io/duqueom/telecom-api:latest ./TelecomAI-Customer-Intelligence

# Push to registry
docker push ghcr.io/duqueom/bankchurn-api:1.2.0
docker push ghcr.io/duqueom/bankchurn-api:latest

docker push ghcr.io/duqueom/carvision-api:1.2.0
docker push ghcr.io/duqueom/carvision-api:latest

docker push ghcr.io/duqueom/telecom-api:1.2.0
docker push ghcr.io/duqueom/telecom-api:latest
```

#### 8. Deploy to Production

**Kubernetes**:
```bash
# Update image tags in K8s manifests
sed -i 's/latest/1.2.0/g' k8s/*-deployment.yaml

# Apply to production
kubectl apply -f k8s/ -n ml-production

# Verify rollout
kubectl rollout status deployment/bankchurn -n ml-production
kubectl rollout status deployment/carvision -n ml-production
kubectl rollout status deployment/telecom -n ml-production
```

**Docker Compose** (staging):
```bash
# Update docker-compose.demo.yml with new tags
docker-compose -f docker-compose.demo.yml pull
docker-compose -f docker-compose.demo.yml up -d
```

#### 9. Post-Release Verification

```bash
# Health checks
curl https://api.production.com/bankchurn/health
curl https://api.production.com/carvision/health
curl https://api.production.com/telecom/health

# Smoke tests
./scripts/smoke_tests.sh production

# Monitor logs and metrics
kubectl logs -f deployment/bankchurn -n ml-production
```

#### 10. Merge Back to Develop

```bash
git checkout develop
git merge main
git push origin develop
```

## GitHub Container Registry (GHCR) Setup

### Initial Setup

1. **Create Personal Access Token (PAT)**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate new token with scopes: `write:packages`, `read:packages`, `delete:packages`
   - Save token securely

2. **Configure Package Visibility**:
   - Go to package settings on GitHub
   - Set visibility to **Public** or **Private**

3. **Add to GitHub Actions Secrets**:
   - Repository Settings → Secrets → Actions
   - Add secret: `GHCR_TOKEN` with PAT value

### Automated Publishing (GitHub Actions)

Create `.github/workflows/publish-images.yml`:

```yaml
name: Publish Docker Images

on:
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  IMAGE_PREFIX: ghcr.io/${{ github.repository_owner }}

jobs:
  publish:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        project:
          - BankChurn-Predictor
          - CarVision-Market-Intelligence
          - TelecomAI-Customer-Intelligence
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.IMAGE_PREFIX }}/${{ matrix.project }}
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=semver,pattern={{major}}
            type=raw,value=latest
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: ./${{ matrix.project }}
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
```

## Rollback Procedure

### Quick Rollback (Kubernetes)

```bash
# Rollback to previous version
kubectl rollout undo deployment/bankchurn -n ml-production

# Rollback to specific revision
kubectl rollout history deployment/bankchurn -n ml-production
kubectl rollout undo deployment/bankchurn --to-revision=3 -n ml-production
```

### Docker Compose Rollback

```bash
# Pull previous version
docker pull ghcr.io/duqueom/bankchurn-api:1.1.0

# Update docker-compose.yml with old tag
docker-compose -f docker-compose.demo.yml up -d
```

### Full Rollback (Git)

```bash
# Revert to previous release
git revert v1.2.0
git tag -a v1.2.1 -m "Rollback to v1.1.0 state"
git push origin main --tags
```

## Hotfix Process

For urgent bug fixes in production:

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/critical-bug-fix

# Make fixes
# ... edit files ...

# Test
pytest tests/
docker-compose -f docker-compose.demo.yml up -d
pytest tests/integration/test_demo.py
docker-compose -f docker-compose.demo.yml down

# Bump patch version (e.g., 1.2.0 → 1.2.1)
# Update CHANGELOG.md

# Merge to main and develop
git checkout main
git merge hotfix/critical-bug-fix
git tag -a v1.2.1 -m "Hotfix: Critical bug fix"
git push origin main --tags

git checkout develop
git merge hotfix/critical-bug-fix
git push origin develop

# Deploy
kubectl set image deployment/bankchurn bankchurn=ghcr.io/duqueom/bankchurn-api:1.2.1 -n ml-production
```

## Model Release Management

### Model Versioning

```python
# Register model in MLflow
import mlflow

with mlflow.start_run():
    # Train model
    model = train_model()
    
    # Log model
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name="BankChurn-XGBoost"
    )
    
    # Tag version
    client = mlflow.tracking.MlflowClient()
    client.create_model_version(
        name="BankChurn-XGBoost",
        source="models:/BankChurn-XGBoost/1",
        run_id=run.info.run_id,
        tags={"version": "1.2.0", "stage": "production"}
    )
```

### Model Deployment

```bash
# Export model from MLflow
mlflow models serve -m "models:/BankChurn-XGBoost/production" -p 5001

# Or copy to artifacts/
mlflow models download -m "models:/BankChurn-XGBoost/1" -d ./artifacts/
```

## Release Artifacts

### Build Artifacts

- **Docker images**: Pushed to GHCR
- **Python packages**: Optionally publish to PyPI
- **Model files**: Stored in MLflow Model Registry
- **Documentation**: Auto-generated API docs

### Release Notes Template

```markdown
## 🎉 Release v1.2.0

### 🚀 New Features
- **BankChurn**: Added batch prediction endpoint
- **CarVision**: New market analysis dashboard
- **TelecomAI**: Improved prediction accuracy (+3% F1-score)

### 🐛 Bug Fixes
- Fixed memory leak in CarVision API
- Resolved CORS issues in TelecomAI

### 📈 Performance
- 30% faster inference time in BankChurn
- Reduced Docker image size by 200MB

### 🔒 Security
- Updated all dependencies to patch CVE-2024-XXXX
- Implemented rate limiting on APIs

### 📚 Documentation
- Added OPERATIONS_PORTFOLIO.md
- Updated API documentation

### 🔧 Infrastructure
- Kubernetes manifests with HPA
- Prometheus/Grafana integration

### ⚙️ Breaking Changes
- None

### 📦 Docker Images
- `ghcr.io/duqueom/bankchurn-api:1.2.0`
- `ghcr.io/duqueom/carvision-api:1.2.0`
- `ghcr.io/duqueom/telecom-api:1.2.0`

### 🙏 Contributors
- @DuqueOM

**Full Changelog**: https://github.com/DuqueOM/ML-MLOps-Portfolio/compare/v1.1.0...v1.2.0
```

## Continuous Deployment (Future)

### Auto-Deploy to Staging

```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging

on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to staging
        run: |
          kubectl config use-context staging
          kubectl apply -f k8s/ -n ml-staging
```

### Canary Deployment

```bash
# Deploy canary (10% traffic)
kubectl set image deployment/bankchurn bankchurn=ghcr.io/duqueom/bankchurn-api:1.2.0 -n ml-production
kubectl scale deployment/bankchurn-canary --replicas=1 -n ml-production

# Monitor metrics for 30 minutes
# If healthy, promote to production
kubectl scale deployment/bankchurn --replicas=10 -n ml-production
kubectl scale deployment/bankchurn-canary --replicas=0 -n ml-production
```

## Emergency Procedures

### Critical Bug in Production

1. **Immediate rollback** (< 5 minutes)
2. **Create hotfix branch**
3. **Fix and test** (< 2 hours)
4. **Deploy hotfix**
5. **Post-mortem** (within 24 hours)

### Service Outage

1. **Check health endpoints**
2. **Review logs**: `kubectl logs`
3. **Check resource usage**: `kubectl top pods`
4. **Scale up if needed**: `kubectl scale deployment`
5. **Rollback if necessary**

## Compliance & Audit

### Release Audit Trail

- All releases tagged in Git
- Docker images immutable and signed
- MLflow tracks all model versions
- CI/CD logs retained for 90 days

### Compliance Checklist

- [ ] Security scans passed
- [ ] Data privacy compliance (GDPR, etc.)
- [ ] Model fairness evaluated
- [ ] Documentation updated
- [ ] Stakeholder approval obtained
