# Dependency Conflicts and Remediation

## Overview

This document identifies version conflicts and problematic dependencies across the three projects and provides remediation steps.

## Identified Conflicts

### 1. PyArrow Version Conflicts

**Problem**:
- BankChurn-Predictor: Uses pip-compile with hashed requirements (pyarrow pinned)
- CarVision-Market-Intelligence: Uses unpinned requirements (pyarrow>=8.0.0)
- TelecomAI-Customer-Intelligence: Uses pip-compile with hashed requirements (pyarrow pinned)

**Impact**: Build failures when switching between projects

**Remediation**:
```bash
# Pin to compatible version across all projects
# Update all requirements.in files:
pyarrow==21.0.0

# Recompile
pip-compile --generate-hashes --output-file=requirements.txt requirements.in
```

**Status**: ⚠️ **Action Required**

---

### 2. Python Version Mismatch

**Problem**:
- BankChurn Dockerfile: `FROM python:3.13-slim` (builder) → `FROM python:3.12-slim` (runtime)
- CarVision Dockerfile: `FROM python:3.11-slim`
- TelecomAI Dockerfile: `FROM python:3.11-slim`

**Impact**: Binary incompatibility, hash verification failures

**Remediation**:
```dockerfile
# Standardize all Dockerfiles to:
FROM python:3.11-slim AS builder
FROM python:3.11-slim AS runtime
```

**Status**: ✅ **Fixed**

---

### 3. Pydantic V1 vs V2

**Problem**:
- Code uses `.dict()` method (v1 API)
- Pydantic v2 uses `.model_dump()`

**Remediation**:
```python
# Pin to v1 for stability
pydantic>=1.10.0,<2.0.0
```

**Status**: ✅ **Current code compatible**

---

## Remediation Plan

### Phase 1: Critical Fixes
1. ✅ Standardize Python versions in Dockerfiles
2. ⚠️ Pin PyArrow to 21.0.0
3. ⚠️ Pin Pydantic to v1

### Phase 2: Standardization
4. Create common_requirements.in
5. Update project-specific requirements

### Phase 3: Testing & Validation
6. Rebuild Docker images
7. Run integration tests

---

## Known Issues

### Streamlit FutureWarning
**Location**: CarVision app/streamlit_app.py:341

**Fix**:
```python
df_filtered.groupby("price_category", observed=True)["price"].sum()
```

**Priority**: Low

---

## Summary of Action Items

### High Priority
- [ ] Pin PyArrow to 21.0.0 in all projects
- [ ] Pin Pydantic to v1 (<2.0.0)

### Medium Priority
- [ ] Standardize scikit-learn version
- [ ] Update FastAPI and Uvicorn

### Low Priority
- [ ] Fix Streamlit FutureWarning
- [ ] Remove docker-compose version field
