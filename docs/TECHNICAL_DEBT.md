# Technical Debt Registry

**Last Updated**: 2025-11-25  
**Owner**: @DuqueOM

This document tracks technical debt items identified during code audits and ongoing development.

---

## Priority Legend

| Priority | Description | Target Resolution |
|----------|-------------|-------------------|
| 🔴 **Critical** | Security/stability risk | This sprint |
| 🟠 **High** | Affects maintainability | Next 2 sprints |
| 🟡 **Medium** | Improvement opportunity | Backlog |
| 🟢 **Low** | Nice to have | When convenient |

---

## Active Debt Items

### BankChurn-Predictor

| ID | Item | Priority | Effort | Status | Owner |
|----|------|----------|--------|--------|-------|
| BC-001 | `ChurnPredictor.predict` complexity (C-13) | 🟡 Medium | 2h | Open | - |
| BC-002 | `ChurnTrainer.build_preprocessor` complexity (C-11) | 🟡 Medium | 2h | Open | - |
| BC-003 | `ModelEvaluator.compute_fairness_metrics` (B-10) | 🟡 Medium | 1h | Open | - |
| BC-004 | Add type hints to remaining functions | 🟢 Low | 3h | Open | - |

### CarVision-Market-Intelligence

| ID | Item | Priority | Effort | Status | Owner |
|----|------|----------|--------|--------|-------|
| CV-001 | `infer_feature_types` complexity (C-14) | 🟠 High | 2h | Open | - |
| CV-002 | `MarketAnalyzer.generate_executive_summary` (C-13) | 🟡 Medium | 2h | Open | - |
| CV-003 | `VisualizationEngine` methods (B-10 each) | 🟡 Medium | 3h | Open | - |
| CV-004 | Notebook outputs in EDA.ipynb | 🟢 Low | 0.5h | ✅ Done | Audit |

### TelecomAI-Customer-Intelligence

| ID | Item | Priority | Effort | Status | Owner |
|----|------|----------|--------|--------|-------|
| TC-001 | Add integration tests for FastAPI endpoints | 🟡 Medium | 2h | Open | - |
| TC-002 | Improve docstrings coverage | 🟢 Low | 1h | Open | - |

### Infrastructure / CI

| ID | Item | Priority | Effort | Status | Owner |
|----|------|----------|--------|--------|-------|
| INF-001 | Configure DVC cloud remote (S3/GCS) | 🟠 High | 2h | Open | - |
| INF-002 | Add coverage threshold enforcement in CI | 🟢 Low | 1h | ✅ Done | Audit |
| INF-003 | Enable Dependabot for automated updates | 🟢 Low | 0.5h | ✅ Done | Audit |

---

## Resolved Items (Last 30 Days)

| ID | Item | Resolution | Date | PR |
|----|------|------------|------|-----|
| SEC-001 | Gitleaks false positives in notebooks | Added `.gitleaksignore` and config | 2025-11-25 | #- |
| INF-002 | Quality gates in CI | Added quality-gates job | 2025-11-25 | #- |
| CV-004 | Notebook outputs | Stripped with nbstripout | 2025-11-25 | #- |
| INF-003 | Dependabot | Created `.github/dependabot.yml` | 2025-11-25 | #- |

---

## Debt Metrics

### Current State (2025-11-25)

| Metric | Value | Target |
|--------|-------|--------|
| Total Open Items | 10 | <15 |
| Critical Items | 0 | 0 |
| High Priority Items | 2 | <5 |
| Average Resolution Time | - | <7 days |

### Complexity Summary (Radon CC)

| Project | Files with C+ | Avg Complexity | Target |
|---------|---------------|----------------|--------|
| BankChurn-Predictor | 3 | B (3.76) | A |
| CarVision-Market-Intelligence | 2 | A (4.19) | A |
| TelecomAI-Customer-Intelligence | 0 | A (2.73) | A |

---

## Process

### Adding New Debt

1. Create issue with label `tech-debt`
2. Add entry to this document
3. Assign priority and effort estimate
4. Link to related code/files

### Resolving Debt

1. Create PR with fix
2. Reference debt ID in PR description
3. Update status in this document
4. Move to "Resolved Items" section

### Review Cadence

- **Weekly**: Review critical/high items
- **Monthly**: Full debt review and prioritization
- **Quarterly**: Debt reduction sprint

---

## References

- [Global Code Quality Report](../Reportes%20Portafolio/Global-Code-Quality-Report.md)
- [Radon Documentation](https://radon.readthedocs.io/)
- [Clean Code Principles](https://clean-code-developer.com/)
