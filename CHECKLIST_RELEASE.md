# Release Checklist - ML/MLOps Portfolio

This checklist ensures all quality gates are met before releasing new versions of the portfolio projects.

---

## 🚀 Pre-Release Requirements

### Code Quality
- [ ] **All tests pass**: `make test` across all projects
- [ ] **Coverage achieved**: All projects > 70% coverage
- [ ] **Linting clean**: `make lint` passes without errors
- [ ] **Type checking**: `make typecheck` reports no critical issues
- [ ] **Security scan**: `make docker-scan` shows no HIGH/CRITICAL vulnerabilities

### Documentation
- [ ] **READMEs updated**: All project READMEs reflect changes
- [ ] **Architecture docs**: ARCHITECTURE.md files updated if needed
- [ ] **Model cards**: Updated for any model changes
- [ ] **API docs**: FastAPI docs accessible and accurate
- [ ] **CHANGELOG**: Updated with new features/fixes (docs/RELEASE.md)

### Docker & Infrastructure
- [ ] **Images build**: `make docker-build` succeeds for all projects
- [ ] **Images scan**: No critical vulnerabilities found
- [ ] **docker-compose files**: Updated if services changed (docker-compose.demo.yml)
- [ ] **Environment variables**: All required vars documented

---

## 🧪 Testing Requirements

### Unit Tests
```bash
# Run all project tests
make test

# Individual project verification
cd BankChurn-Predictor && python -m pytest tests/ -v
cd CarVision-Market-Intelligence && python -m pytest tests/ -v  
cd TelecomAI-Customer-Intelligence && python -m pytest tests/ -v
```

### Integration Tests
- [ ] **API endpoints**: All `/health`, `/predict` endpoints respond correctly
- [ ] **MLflow integration**: Experiments tracked properly
- [ ] **DVC pipelines**: `dvc repro` executes successfully
- [ ] **Docker stack**: `make docker-demo` starts all services

### Performance Tests
- [ ] **API latency**: All predictions < 200ms P95
- [ ] **Memory usage**: Containers within limits (< 1GB each)
- [ ] **Model accuracy**: No regression in key metrics

---

## 🔐 Security Verification

### Code Security
- [ ] **Secrets scan**: `gitleaks` reports no leaks
- [ ] **Dependency scan**: No known vulnerabilities in requirements
- [ ] **API security**: Input validation works correctly
- [ ] **Docker security**: Images run as non-root users

### Infrastructure Security
- [ ] **Network ports**: Only required ports exposed
- [ ] **Environment files**: No secrets in .env files
- [ ] **SSL/TLS**: HTTPS configured for production (if applicable)

---

## 📦 Build & Deployment

### Docker Images
```bash
# Build all images
make docker-build

# Verify images
docker images | grep -E "(bankchurn|carvision|telecomai)"
```

### Version Tagging
- [ ] **Semantic versioning**: Follow MAJOR.MINOR.PATCH format
- [ ] **Git tags**: Created and pushed for release
- [ ] **Image tags**: Consistent with git tags
- [ ] **Release notes**: Comprehensive changelog

### Deployment Testing
- [ ] **Staging deployment**: Test in staging environment first
- [ ] **Health checks**: All services report healthy
- [ ] **Monitoring**: Metrics and logs flowing correctly
- [ ] **Rollback plan**: Documented and tested

---

## 📊 Model Validation

### Model Performance
- [ ] **Metrics stable**: Key metrics within expected ranges
- [ ] **Drift check**: No significant data drift detected
- [ ] **Fairness tests**: Bias metrics within acceptable limits
- [ ] **Explainability**: SHAP values make business sense

### Model Registry
- [ ] **MLflow models**: Registered with correct version
- [ ] **Model artifacts**: All required files included
- [ ] **Model signatures**: Input/output schemas correct
- [ ] **Model lineage**: Clear training data provenance

---

## 🔄 Data Pipeline Verification

### DVC Operations
```bash
# Verify data versioning
dvc status
dvc repro

# Check data integrity
dvc checkout
dvc diff
```

### Data Quality
- [ ] **Data schemas**: No breaking changes in data structure
- [ ] **Data validation**: All validation checks pass
- [ ] **Data lineage**: Clear data source tracking
- [ ] **Data privacy**: No PII in training data

---

## 📋 Documentation Review

### Technical Documentation
- [ ] **API documentation**: Complete and accurate
- [ ] **Architecture diagrams**: Up-to-date and clear
- [ ] **Deployment guides**: Step-by-step instructions
- [ ] **Troubleshooting**: Common issues documented

### User Documentation
- [ ] **Quick start guides**: Work for new users
- [ ] **Examples**: Code examples tested and working
- [ ] **FAQ**: Common questions answered
- [ ] **Contact info**: Support channels clearly listed

---

## 🚀 Final Release Steps

### Git Operations
```bash
# Create release tag
git tag -a v1.2.3 -m "Release v1.2.3: Feature X and bug fixes"

# Push tag
git push origin v1.2.3

# Push main branch
git push origin main
```

### CI/CD Pipeline
- [ ] **Pipeline triggers**: Automatic build and test on tag
- [ ] **Artifact publishing**: Docker images pushed to registry
- [ ] **Documentation deployment**: Docs site updated
- [ ] **Release announcements**: Communications sent

### Post-Release Verification
- [ ] **Production monitoring**: Check error rates and latency
- [ ] **User feedback**: Collect initial user responses
- [ ] **Rollback readiness**: Quick rollback if issues found
- [ ] **Metrics tracking**: Monitor KPIs after release

---

## 📝 Release Notes Template

```markdown
# Release v{VERSION}

## 🚀 New Features
- Feature 1: Description
- Feature 2: Description

## 🐛 Bug Fixes  
- Fix 1: Description
- Fix 2: Description

## 🔧 Improvements
- Improvement 1: Description
- Improvement 2: Description

## 📦 Dependencies
- Updated: Package X to version Y
- Added: Package Z for functionality

## 🔒 Security
- Security fix: Description
- Updated dependencies for security

## 📚 Documentation
- Updated: Documentation section
- Added: New guide

## 🚀 Deployment
- Docker images: Tagged as v{VERSION}
- Breaking changes: List if any
- Migration steps: Required steps if needed

## 🙏 Acknowledgments
- Thanks to contributors
- Special mentions
```

---

## ✅ Release Sign-off

Before releasing, ensure:

- [ ] **All checklist items completed**
- [ ] **Team review performed**  
- [ ] **Stakeholder approval obtained**
- [ ] **Rollback plan documented**
- [ ] **Monitoring configured**

**Release Approved By**: _________________________
**Date**: ______________________________________
**Version**: ____________________________________

---

*This checklist should be used for every release to ensure quality and consistency across the ML/MLOps Portfolio.*
