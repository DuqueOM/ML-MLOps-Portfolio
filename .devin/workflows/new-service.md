---
description: Create a complete new ML service from template — end-to-end scaffolding
---

# /new-service Workflow

## 1. Gather Requirements

Before creating any files, determine:
- **Service name**: `{ServiceName}-{Purpose}` (e.g., `FraudDetect-Scorer`)
- **Service slug**: lowercase, no hyphens (e.g., `frauddetect`)
- **Business problem**: One sentence
- **Model type**: classification / regression / NLP / time series
- **Dataset**: Source, size, target
- **Explainability needed**: yes / no
- **Latency SLA**: p95 target in ms

## 2. Scaffold from Template

```bash
# Automated scaffolding (recommended)
bash templates/scripts/new-service.sh "${SVC_NAME}" "${SVC_SLUG}"

# Verify: no remaining placeholders
grep -r "{ServiceName}\|{service}\|{SERVICE}" ${SVC_NAME}/ --include="*.py" --include="*.yaml" | head -10
```

If `new-service.sh` is unavailable, manual fallback:
```bash
cp -r templates/service/ ${SVC_NAME}/
find ${SVC_NAME}/ -type f -exec sed -i "s/{ServiceName}/${SVC_NAME}/g" {} +
find ${SVC_NAME}/ -type f -exec sed -i "s/{service}/${SVC_SLUG}/g" {} +
mv ${SVC_NAME}/src/\{service\} ${SVC_NAME}/src/${SVC_SLUG}
```

## 3. Data Validation

- Define Pandera schema in `${SVC_NAME}/src/${SVC_SLUG}/schemas.py`
- Implement validation at training, serving, and drift detection points
- Check for temporal data → leakage review

## 4. Training Pipeline

- Implement feature engineering in `src/${SVC_SLUG}/training/features.py`
- Define model in `src/${SVC_SLUG}/training/model.py`
- Implement full trainer in `src/${SVC_SLUG}/training/train.py`
- Configure Optuna (50+ trials)
- Set up MLflow experiment

## 5. Serving API

- Define Pydantic schemas in `app/schemas.py`
- Implement async inference in `app/main.py`
- Add SHAP integration if needed
- Add Prometheus metrics

## 6. Containerize

- Customize Dockerfile
- Build and test locally
- Verify no models in image

## 7. Kubernetes Manifests

```bash
# Copy K8s templates
cp templates/k8s/deployment.yaml k8s/base/${SVC_SLUG}-deployment.yaml
cp templates/k8s/hpa.yaml k8s/base/${SVC_SLUG}-hpa.yaml
cp templates/k8s/service.yaml k8s/base/${SVC_SLUG}-service.yaml
sed -i "s/{service}/${SVC_SLUG}/g" k8s/base/${SVC_SLUG}-*.yaml
```

Add to kustomization.yaml and create overlay patches.

## 8. Infrastructure

- Add container repository in Terraform
- Update IAM permissions
- `terraform plan` → verify → apply

## 9. CI/CD

- Add to CI build matrix
- Add to drift detection matrix
- Create retrain workflow

## 10. Monitoring

- Create Grafana dashboard from template
- Configure AlertManager rules
- Verify Pushgateway connectivity

## 11. Drift Detection

- Define per-feature PSI thresholds
- Create CronJob
- Configure heartbeat alert

## 12. Documentation

- Create model selection ADR
- Write service README
- Update AGENTS.md
- Create runbook

## 13. Testing

- Write all mandatory tests
- Run load test with Locust
- Verify coverage >= 90%

## 14. Final Verification

Run the acceptance checklist:
- [ ] All tests passing
- [ ] Coverage >= 90%
- [ ] Load test < 1% errors
- [ ] Quality gates passing
- [ ] Fairness DIR >= 0.80
- [ ] Drift detection running
- [ ] Documentation complete
- [ ] ADRs written
