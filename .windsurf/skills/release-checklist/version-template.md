# CHANGELOG Entry Template

## [vX.Y.Z] - YYYY-MM-DD

### Added
- New feature or capability

### Changed
- Modified behavior or updated dependency

### Fixed
- Bug fix with root cause description

### Infrastructure
- K8s manifest changes, Terraform updates, CI/CD changes

### Documentation
- New or updated docs, ADRs

### Models
- Model version updates with metrics comparison

---

## Example Entry

## [v3.6.0] - 2026-06-15

### Added
- SageMaker and Vertex AI endpoint deployments (ADR-017)
- Multi-paradigm ML serving comparison documentation

### Changed
- BankChurn model updated to StackingClassifier v3.0.0 (AUC 0.8693)
- NLPInsight upgraded to ProsusAI/FinBERT (Accuracy 96.91%)

### Fixed
- HPA scale-down issue resolved by removing memory metric (ADR-001)

### Infrastructure
- Helm chart added at helm/ml-portfolio/
- Drift detection CronJob added to k8s/

### Models
| Service | Previous | Current | Delta |
|---------|----------|---------|-------|
| BankChurn | AUC 0.8626 (v2) | AUC 0.8693 (v3) | +0.78% |
| NLPInsight | Acc 88.08% (v2) | Acc 96.91% (v3) | +10.0% |
| ChicagoTaxi | R² 0.8246 (v2) | R² 0.7955 (v3) | -3.5% (honest features) |
