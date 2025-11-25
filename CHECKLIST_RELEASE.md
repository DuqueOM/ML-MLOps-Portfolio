# Release Checklist — ML/MLOps Portfolio v1.0

Use this checklist before publishing or sharing the portfolio.

---

## 🎬 Media Assets

- [ ] **Video: BankChurn Demo** (2-3 min)
  - Location: `media/videos/bankchurn-demo.mp4` or [YouTube link]
  - **[RECORD AND UPLOAD — See media/README.md for script]**

- [ ] **Video: CarVision Demo** (2-3 min)
  - Location: `media/videos/carvision-demo.mp4` or [YouTube link]
  - **[RECORD AND UPLOAD — See media/README.md for script]**

- [ ] **Video: TelecomAI Demo** (2-3 min)
  - Location: `media/videos/telecom-demo.mp4` or [YouTube link]
  - **[RECORD AND UPLOAD — See media/README.md for script]**

- [ ] **GIF: BankChurn Preview** (6-8 sec)
  - Location: `media/gifs/bankchurn-preview.gif`
  - Content: API prediction call → response
  - **[CREATE FROM VIDEO]**

- [ ] **GIF: CarVision Preview** (6-8 sec)
  - Location: `media/gifs/carvision-preview.gif`
  - Content: Dashboard interaction → price prediction
  - **[CREATE FROM VIDEO]**

- [ ] **GIF: TelecomAI Preview** (6-8 sec)
  - Location: `media/gifs/telecom-preview.gif`
  - Content: API call → plan recommendation
  - **[CREATE FROM VIDEO]**

- [ ] **Screenshots captured**
  - [ ] CI pipeline passing (`media/screenshots/ci-pipeline-passing.png`)
  - [ ] Coverage report (`media/screenshots/coverage-report.png`)
  - [ ] MLflow dashboard (`media/screenshots/mlflow-dashboard.png`)
  - [ ] API Swagger UIs (`media/screenshots/*-api.png`)
  - **[CAPTURE FROM RUNNING SERVICES]**

- [ ] **Thumbnails created** for videos
  - Location: `media/thumbnails/`
  - **[DESIGN OR AUTO-GENERATE]**

---

## 📄 Documentation

### Root Repository

- [x] `README.md` — Updated with badges, GIF placeholders, video links
- [x] `.dockerignore` — Created to optimize Docker builds
- [x] `.env.example` — Documented all environment variables
- [x] `RUNBOOK.md` — Quick command reference
- [x] `CHECKLIST_RELEASE.md` — This file
- [x] `CONTRIBUTING.md` — Contribution guidelines
- [x] `CHANGELOG.md` — Version history

### Per-Project Documentation

- [x] **BankChurn-Predictor**
  - [x] `README.md` with badges, demo section, quickstart
  - [x] `models/model_card.md` with metrics and reproducibility
  - [ ] **GIF embedded in README** — **[UPDATE AFTER GIF CREATED]**

- [x] **CarVision-Market-Intelligence**
  - [x] `README.md` with badges, demo section, quickstart
  - [x] `models/model_card.md` with metrics and reproducibility
  - [ ] **GIF embedded in README** — **[UPDATE AFTER GIF CREATED]**

- [x] **TelecomAI-Customer-Intelligence**
  - [x] `README.md` with badges, demo section, quickstart
  - [x] `models/model_card.md` with metrics and reproducibility
  - [ ] **GIF embedded in README** — **[UPDATE AFTER GIF CREATED]**

---

## 🔧 Technical Verification

### CI/CD

- [x] GitHub Actions workflow `ci-mlops.yml` passing
- [x] All tests pass on Python 3.11 and 3.12
- [x] Coverage ≥ 70% for all projects
- [x] Docker builds succeed for all projects
- [ ] **Badge URLs point to correct workflow** — Verify after pushing

### Docker

- [x] All Dockerfiles use `python:3.11-slim` base
- [x] Non-root user (`appuser`) in all containers
- [x] Health checks configured on `/health`
- [x] `.dockerignore` excludes unnecessary files

### Security

- [x] No secrets in codebase (checked with Gitleaks)
- [x] `.env.example` has no real credentials
- [x] Bandit scan passes
- [ ] Trivy scan on Docker images — **[RUN BEFORE FINAL RELEASE]**

---

## 🚀 Release Artifacts

### GitHub Release

- [ ] Create GitHub Release tag `v1.0.0`
- [ ] Attach release notes (copy from CHANGELOG.md)
- [ ] Attach coverage report artifact
- [ ] Link to demo videos
- **[CREATE RELEASE ON GITHUB]**

### Container Registry (GHCR)

- [ ] Push `ghcr.io/duqueom/bankchurn-api:1.0.0`
- [ ] Push `ghcr.io/duqueom/carvision-api:1.0.0`
- [ ] Push `ghcr.io/duqueom/telecom-api:1.0.0`
- [ ] Verify packages are visible in GitHub Packages
- **[PUSH AFTER CI PASSES]**

### README Links

- [ ] Update README with links to GHCR packages
- [ ] Add "Docker Pull" badges or commands
- **[UPDATE AFTER GHCR PUSH]**

---

## 📊 Metrics to Document

Capture and document these metrics in project READMEs and model cards:

### BankChurn-Predictor
| Metric | Value |
|--------|-------|
| AUC-ROC | **[INSERT VALUE]** |
| F1-Score | **[INSERT VALUE]** |
| Coverage | 77% |
| Latency (p95) | **[INSERT VALUE]** ms |

### CarVision-Market-Intelligence
| Metric | Value |
|--------|-------|
| RMSE | **[INSERT VALUE]** |
| MAE | **[INSERT VALUE]** |
| R² | **[INSERT VALUE]** |
| Coverage | 96% |

### TelecomAI-Customer-Intelligence
| Metric | Value |
|--------|-------|
| AUC-ROC | **[INSERT VALUE]** |
| Accuracy | **[INSERT VALUE]** |
| Coverage | 96% |

---

## 🎯 Final Review

Before sharing with recruiters/hiring managers:

- [ ] All GIFs load correctly in READMEs
- [ ] Video links work (if using YouTube/Drive)
- [ ] Clone and `docker-compose up` works on fresh machine
- [ ] API endpoints return valid predictions
- [ ] Dashboard loads without errors
- [ ] Mobile-friendly README (preview on phone)

---

## 📞 Contact Information

Ensure contact info is updated in:

- [ ] Root `README.md` — Author section
- [ ] Project READMEs — Maintainers section
- [ ] LinkedIn URL is correct
- [ ] GitHub profile URL is correct

---

## ✅ Sign-Off

| Reviewer | Date | Status |
|----------|------|--------|
| Self-Review | | ⬜ Pending |
| Peer Review (optional) | | ⬜ Pending |

---

**Notes:**
- Items marked **[PLACEHOLDER]** require manual action
- Update this checklist as items are completed
- Keep this file updated for future releases
