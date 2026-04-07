---
name: release-checklist
description: Guides the full release process for ML-MLOps Portfolio including version bumping, changelog updates, Docker builds, multi-cloud deployment, and git tagging.
---

## Release Process

### Phase 1: Pre-Release Validation

1. **Verify all CI checks pass** on `main` branch
2. **Run full test suite locally**:
   ```bash
   make test
   ```
3. **Check for uncommitted changes**:
   ```bash
   git status
   git diff --stat
   ```
4. **Review CHANGELOG.md** for completeness

### Phase 2: Version Bump

1. Determine version increment (major.minor.patch) following semver
2. Update version in:
   - Each service's `pyproject.toml` or `setup.cfg`
   - `k8s/base/` deployment manifests (image tags)
   - `helm/ml-portfolio/Chart.yaml` (appVersion)
   - `README.md` version badge
3. Update `CHANGELOG.md` with new section

### Phase 3: Build & Push

```bash
# Build Docker images
for svc in BankChurn-Predictor NLPInsight-Analyzer ChicagoTaxi-Demand-Pipeline; do
  docker build -t us-central1-docker.pkg.dev/ml-portfolio-duque-om-202602/ml-portfolio-images/${svc,,}:v${VERSION} ./${svc}
done

# Push to Artifact Registry
for svc in bankchurn-predictor nlpinsight-analyzer chicagotaxi-demand-pipeline; do
  docker push us-central1-docker.pkg.dev/ml-portfolio-duque-om-202602/ml-portfolio-images/${svc}:v${VERSION}
done
```

### Phase 4: Deploy

1. Deploy to GKE first (primary): `kubectl apply -k k8s/overlays/gcp/`
2. Run smoke tests: `./scripts/smoke_test.sh`
3. If smoke tests pass, deploy to EKS: `kubectl apply -k k8s/overlays/aws/`
4. Run smoke tests against EKS

### Phase 5: Tag & Release

```bash
git add -A
git commit -m "Release v${VERSION}"
git tag -a "v${VERSION}" -m "Release v${VERSION}: <summary>"
git push origin main --tags
```

### Phase 6: Post-Release

- [ ] Verify GitHub Actions triggered deploy workflows
- [ ] Check Grafana dashboards for healthy traffic
- [ ] Monitor error rates for 30 minutes
- [ ] Update GitHub release notes
- [ ] Notify stakeholders

See `version-template.md` for CHANGELOG entry template.
